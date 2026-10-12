"""Offline safety regressions and an explicitly gated real-provider smoke."""
import builtins
import json
import logging
import os
import sys

import pytest

from tests import provider_engine_harness as harness
from tests.provider_engine_harness import isolated_engine, smoke_selection


class Controls(dict):
    def get(self, key, default=None):
        assert key.startswith("NEWMIND_SMOKE_"), "Credential accessed before gate"
        return super().get(key, default)


def test_default_gate_does_not_inspect_credentials():
    controls = Controls(GEMINI_API_KEY="synthetic", OPENAI_API_KEY="synthetic",
                        GROK_API_KEY="synthetic")
    assert smoke_selection(controls) is None
    assert harness.run_selected_smoke(controls) == {"validation": "skipped"}


@pytest.mark.parametrize("controls", [
    {"NEWMIND_SMOKE_GATE": "yes"},
    {"NEWMIND_SMOKE_PROVIDER": "gemini"},
    {"NEWMIND_SMOKE_GATE": "authorized", "NEWMIND_SMOKE_PROVIDER": "grok"},
    {"NEWMIND_SMOKE_GATE": "authorized", "NEWMIND_SMOKE_PROVIDER": "openai",
     "NEWMIND_SMOKE_ENVIRONMENT": "/private/path"},
])
def test_invalid_controls_fail_before_credentials(controls):
    with pytest.raises(ValueError, match="Invalid smoke controls"):
        smoke_selection(Controls(controls))


@pytest.mark.parametrize("provider", ["gemini", "openai"])
def test_valid_controls_select_only_supported_provider(provider):
    controls = Controls(NEWMIND_SMOKE_GATE="authorized", NEWMIND_SMOKE_PROVIDER=provider,
                        NEWMIND_SMOKE_ENVIRONMENT="env-01234567")
    assert smoke_selection(controls) == (provider, "env-01234567")


def test_isolated_import_restores_modules_on_exception():
    names = ("config", "config.settings", "rag", "rag.retriever", "storage",
             "storage.oci_client", "llm", "llm.engine", "llm.prompts")
    missing = object()
    before = {name: sys.modules.get(name, missing) for name in names}
    with pytest.raises(RuntimeError, match="synthetic"):
        with isolated_engine() as engine:
            assert engine.llm_engine.gemini_key is None
            assert engine.llm_engine.grok_key is None
            assert engine.llm_engine.openai_key is None
            raise RuntimeError("synthetic")
    assert all(sys.modules.get(name, missing) is original for name, original in before.items())


def test_isolated_import_blocks_startup_and_restores_parent_attribute(monkeypatch):
    import llm

    sentinel = object()
    monkeypatch.setattr(llm, "engine", sentinel, raising=False)
    original_import = builtins.__import__
    attempts = []

    def guarded_import(name, *args, **kwargs):
        if name.split(".")[0] in ("dotenv", "chromadb", "oci", "openai", "google"):
            attempts.append(name)
            raise AssertionError("External startup forbidden")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded_import)
    with isolated_engine() as engine:
        assert engine.LLMEngine().openai_key is None
    assert llm.engine is sentinel
    assert attempts == []


@pytest.mark.parametrize("provider", ["gemini", "openai"])
def test_missing_credential_does_not_import_engine_or_sdk(monkeypatch, provider):
    monkeypatch.setattr(harness, "isolated_engine", lambda: pytest.fail("Engine imported too early"))
    controls = dict(NEWMIND_SMOKE_GATE="authorized", NEWMIND_SMOKE_PROVIDER=provider,
                    NEWMIND_SMOKE_ENVIRONMENT="env-01234567")
    assert harness.run_selected_smoke(controls) == {"validation": "missing_credential"}


@pytest.mark.parametrize("outcome", ["valid", "invalid", "error", "fallback"])
@pytest.mark.parametrize("provider", ["gemini", "openai"])
def test_smoke_evidence_is_sanitized_and_rejects_fallback(monkeypatch, capsys, provider, outcome):
    from contextlib import contextmanager

    with isolated_engine() as engine:
        @contextmanager
        def fake_scope():
            yield engine

        monkeypatch.setattr(harness, "isolated_engine", fake_scope)
        # Evidence formatting is isolated from SDK behavior, tested separately below.
        from contextlib import nullcontext
        monkeypatch.setattr(harness, "bounded_gemini", nullcontext)

        def synthetic_call(instance, *args):
            assert instance.grok_key is None
            assert (instance.gemini_key is None) == (provider != "gemini")
            assert (instance.openai_key is None) == (provider != "openai")
            print("private-provider-response")
            logging.warning("private-provider-error")
            if outcome == "error":
                raise RuntimeError("private-provider-error")
            if outcome == "fallback":
                return instance._generate_heuristic_demo(args[-1])
            if outcome == "invalid":
                return {"items": []}
            return dict(titulo="Synthetic", introduccion_contextualizada="Synthetic lesson",
                        tiempo_estimado_estudio_minutos=1, conceptos_clave=["Subnet"], items=[])

        monkeypatch.setattr(engine.LLMEngine, "_call_llm", synthetic_call)
        controls = dict(NEWMIND_SMOKE_GATE="authorized", NEWMIND_SMOKE_PROVIDER=provider,
                        NEWMIND_SMOKE_ENVIRONMENT="env-01234567",
                        GEMINI_API_KEY="synthetic-key", OPENAI_API_KEY="synthetic-key")
        result = harness.run_selected_smoke(controls)
    assert result["validation"] == ("passed" if outcome == "valid" else "failed")
    assert "private" not in json.dumps(result) and "synthetic-key" not in json.dumps(result)
    assert capsys.readouterr() == ("", "")
    if outcome == "valid":
        assert set(result) == {"provider", "model", "utc", "environment", "validation"}
        assert result["provider"] == provider
        assert result["model"] == ("gemini-3.1-flash-lite" if provider == "gemini" else "gpt-4o-mini")
        assert result["utc"].endswith("+00:00")


@pytest.mark.parametrize("outcome", ["valid", "error", "invalid"])
def test_gemini_smoke_bounds_and_restores_sdk(monkeypatch, outcome):
    from types import ModuleType, SimpleNamespace
    import sys

    calls = []
    models = []

    class Model:
        def __init__(self, **kwargs):
            models.append(self)
            calls.append(("model", kwargs))

        def generate_content(self, prompt, *, request_options=None, generation_config=None):
            calls.append(("generate", prompt, request_options, generation_config))
            if outcome == "error":
                raise RuntimeError("synthetic quota failure")
            payload = {"items": []} if outcome == "invalid" else dict(
                titulo="Synthetic", introduccion_contextualizada="Synthetic lesson",
                tiempo_estimado_estudio_minutos=1, conceptos_clave=["Subnet"],
                items=[dict(frente="Subnet?", dorso="A network division.", pista_didactica="Division")],
            )
            return SimpleNamespace(text=json.dumps(payload))

    sdk = ModuleType("google.generativeai")
    sdk.GenerativeModel = Model
    sdk.configure = lambda **kwargs: None
    google = ModuleType("google")
    google.__path__ = []
    google.generativeai = sdk
    monkeypatch.setitem(sys.modules, "google", google)
    monkeypatch.setitem(sys.modules, "google.generativeai", sdk)
    controls = dict(NEWMIND_SMOKE_GATE="authorized", NEWMIND_SMOKE_PROVIDER="gemini",
                    NEWMIND_SMOKE_ENVIRONMENT="env-01234567", GEMINI_API_KEY="synthetic")
    result = harness.run_selected_smoke(controls)
    assert result["validation"] == ("passed" if outcome == "valid" else "failed")
    assert sdk.GenerativeModel is Model
    assert "generate_content" not in models[0].__dict__
    assert len(calls) == 2
    assert calls[0][1]["model_name"] == "gemini-3.1-flash-lite"
    assert calls[0][1]["generation_config"] == {"response_mime_type": "application/json"}
    assert "exactly one short flashcard" in calls[1][1]
    assert calls[1][2] == {"retry": None, "timeout": 30}
    assert calls[1][3] == {"response_mime_type": "application/json",
                           "max_output_tokens": 1024, "candidate_count": 1}


@pytest.mark.parametrize("compatible", [True, False])
def test_gemini_bounds_reject_repeat_or_unsupported_signature(monkeypatch, compatible):
    from types import ModuleType
    import sys

    calls = []

    class Model:
        def generate_content(self, prompt, *, request_options=None, generation_config=None):
            calls.append(prompt)
            return "synthetic"

    if not compatible:
        def unsupported(self, prompt):
            calls.append(prompt)
        Model.generate_content = unsupported
    original = Model.generate_content
    sdk = ModuleType("google.generativeai")
    sdk.GenerativeModel = Model
    google = ModuleType("google")
    google.__path__ = []
    google.generativeai = sdk
    monkeypatch.setitem(sys.modules, "google", google)
    monkeypatch.setitem(sys.modules, "google.generativeai", sdk)
    with harness.bounded_gemini():
        if compatible:
            model = sdk.GenerativeModel()
            assert model.generate_content("synthetic") == "synthetic"
            with pytest.raises(RuntimeError, match="Only one"):
                model.generate_content("repeat")
        else:
            with pytest.raises(TypeError):
                sdk.GenerativeModel()
    assert calls == (["synthetic"] if compatible else [])
    assert sdk.GenerativeModel is Model
    assert Model.generate_content is original
    if compatible:
        assert "generate_content" not in model.__dict__


def test_real_provider_smoke(capfd):
    # Controls are checked before any credential or SDK access. No .env loader.
    try:
        selection = smoke_selection(os.environ)
    except ValueError:
        pytest.fail("Invalid smoke controls", pytrace=False)
    if selection is None:
        pytest.skip("Real provider execution requires separate explicit authorization")
    result = harness.run_selected_smoke(os.environ)
    capfd.readouterr()  # Discard any native SDK output as well as Python output.
    if result["validation"] != "passed":
        pytest.fail("Provider smoke failed; no real execution evidence accepted", pytrace=False)
    print(json.dumps(result, sort_keys=True))
