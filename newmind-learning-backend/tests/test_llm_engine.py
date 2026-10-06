"""Pruebas del orquestador de adaptación pedagógica."""
import json
import logging
import sys
from types import ModuleType, SimpleNamespace

import pytest

from config.settings import Settings
from models.schemas import AlmacenamientoOCI, SolicitudAdaptacion, PerfilDestinatario, FormatoSalida
from llm.engine import LLMEngine, llm_engine
from llm import engine


@pytest.fixture(autouse=True)
def stub_external_dependencies(monkeypatch):
    def fake_llm_response(system_prompt, user_prompt, request):
        return {
            "titulo": "Adapted content",
            "introduccion_contextualizada": "Contextualized introduction",
            "tiempo_estimado_estudio_minutos": 5,
            "conceptos_clave": ["Grounding", "Retrieval"],
            "items": [{"frente": "What is grounding?", "dorso": "Observed source fidelity.", "pista_didactica": "Check the retrieved similarity."}],
        }

    def fake_upload(objeto_id, payload):
        return AlmacenamientoOCI(
            bucket="nuevamente-contenidos-educativos",
            objeto_id=objeto_id,
            status_upload="emulado_local",
        )

    def fake_retrieve_context(query):
        return "Verified VCN context", [{"text": "Verified VCN context", "similarity": 0.9}], 0.9

    monkeypatch.setattr(llm_engine, "_call_llm", fake_llm_response)
    monkeypatch.setattr("llm.engine.rag_retriever.retrieve_context", fake_retrieve_context)
    monkeypatch.setattr("llm.engine.oci_storage.upload_educational_json", fake_upload)


def _request():
    return SolicitudAdaptacion(
        documento_titulo="Introduccion a la Arquitectura de Redes VCN en OCI",
        documento_contenido="La Virtual Cloud Network (VCN) es una red privada en OCI con subredes y security lists.",
        perfil_destinatario=PerfilDestinatario.PRINCIPIANTE,
        formato_salida=FormatoSalida.FLASHCARDS,
    )


def _provider_engine(monkeypatch, *, grok=None, gemini=None, openai=None):
    monkeypatch.setattr(engine, "settings", SimpleNamespace(
        GROK_API_KEY=grok, GEMINI_API_KEY=gemini, OPENAI_API_KEY=openai,
    ))
    return LLMEngine()


def _mock_openai_sdk(monkeypatch, calls, outcomes):
    sdk = ModuleType("openai")

    def client(*, api_key, **kwargs):
        provider = "grok" if "base_url" in kwargs else "openai"
        calls.append((provider, api_key, kwargs))

        def create(**request):
            calls.append((provider, request))
            outcome = outcomes[provider]
            if isinstance(outcome, Exception):
                raise outcome
            return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=outcome))])

        return SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))

    sdk.OpenAI = client
    monkeypatch.setitem(sys.modules, "openai", sdk)


def _mock_gemini_sdk(monkeypatch, calls, outcome):
    google = ModuleType("google")
    google.__path__ = []
    genai = ModuleType("google.generativeai")
    genai.configure = lambda **kwargs: calls.append(("gemini_config", kwargs))

    def model(**kwargs):
        calls.append(("gemini_model", kwargs))

        def generate(_prompt):
            calls.append(("gemini", _prompt))
            if isinstance(outcome, Exception):
                raise outcome
            return SimpleNamespace(text=outcome)

        return SimpleNamespace(generate_content=generate)

    genai.GenerativeModel = model
    google.generativeai = genai
    monkeypatch.setitem(sys.modules, "google", google)
    monkeypatch.setitem(sys.modules, "google.generativeai", genai)


def test_grok_key_is_optional_and_can_be_read_from_environment(monkeypatch):
    monkeypatch.delenv("GROK_API_KEY", raising=False)
    assert Settings(_env_file=None).GROK_API_KEY is None

    monkeypatch.setenv("GROK_API_KEY", "xai-test-key")
    assert Settings(_env_file=None).GROK_API_KEY == "xai-test-key"


def test_grok_success_uses_xai_endpoint_and_json_mode_before_other_providers(monkeypatch):
    calls = []
    payload = {"titulo": "Grok adaptation", "items": []}
    _mock_openai_sdk(monkeypatch, calls, {"grok": json.dumps(payload)})
    _mock_gemini_sdk(monkeypatch, calls, json.dumps({"titulo": "Gemini"}))
    provider = _provider_engine(monkeypatch, grok="xai-test-key", gemini="gemini-test-key", openai="openai-test-key")

    assert provider._call_llm("system", "user", _request()) == payload
    assert calls == [
        ("grok", "xai-test-key", {"base_url": "https://api.x.ai/v1"}),
        ("grok", {
            "model": "grok-4.7",
            "messages": [{"role": "system", "content": "system"}, {"role": "user", "content": "user"}],
            "response_format": {"type": "json_object"},
        }),
    ]


@pytest.mark.parametrize("grok_outcome", [RuntimeError("secret-in-provider-error"), "not json"])
def test_grok_failure_falls_through_to_gemini_then_openai(monkeypatch, caplog, grok_outcome):
    calls = []
    _mock_openai_sdk(monkeypatch, calls, {"grok": grok_outcome, "openai": '{"titulo": "OpenAI"}'})
    _mock_gemini_sdk(monkeypatch, calls, RuntimeError("gemini-secret-in-error"))
    provider = _provider_engine(monkeypatch, grok="secret-xai", gemini="secret-gemini", openai="secret-openai")

    with caplog.at_level(logging.WARNING, logger="llm.engine"):
        assert provider._call_llm("system", "user", _request()) == {"titulo": "OpenAI"}

    assert [call[0] for call in calls] == ["grok", "grok", "gemini_config", "gemini_model", "gemini", "openai", "openai"]
    assert "secret" not in caplog.text
    assert "Grok" in caplog.text and "Gemini" in caplog.text


def test_no_grok_key_retains_gemini_priority(monkeypatch):
    calls = []
    _mock_openai_sdk(monkeypatch, calls, {"openai": '{"titulo": "OpenAI"}'})
    _mock_gemini_sdk(monkeypatch, calls, '{"titulo": "Gemini"}')
    provider = _provider_engine(monkeypatch, gemini="gemini-test-key", openai="openai-test-key")

    assert provider._call_llm("system", "user", _request()) == {"titulo": "Gemini"}
    assert [call[0] for call in calls] == ["gemini_config", "gemini_model", "gemini"]


def test_all_providers_fail_and_heuristic_remains_available(monkeypatch, caplog):
    calls = []
    _mock_openai_sdk(monkeypatch, calls, {"grok": "not json", "openai": RuntimeError("secret-openai-error")})
    _mock_gemini_sdk(monkeypatch, calls, "not json")
    provider = _provider_engine(monkeypatch, grok="secret-xai", gemini="secret-gemini", openai="secret-openai")

    with caplog.at_level(logging.WARNING, logger="llm.engine"):
        result = provider._call_llm("system", "user", _request())

    assert result == provider._generate_heuristic_demo(_request())
    assert "secret" not in caplog.text


def test_no_keys_uses_heuristic_without_importing_providers(monkeypatch):
    provider = _provider_engine(monkeypatch)
    assert provider._call_llm("system", "user", _request()) == provider._generate_heuristic_demo(_request())


def test_adapt_content_vcn_flashcards():
    req = _request()
    resp = llm_engine.adapt_content(req)
    assert resp.status == "exito"
    assert resp.metadatos.perfil_aplicado == "Principiante"
    assert resp.metadatos.formato_generado == "Flashcards"
    assert len(resp.contenido_adaptado.items) > 0
    assert resp.evaluacion_calidad.anclaje_fuente_score >= 0.8
    assert resp.almacenamiento_oci.objeto_id.endswith(".json")


@pytest.mark.parametrize("item", [
    {"frente": "Question", "dorso": "Answer"},
    {"frente": "Question", "dorso": "Answer", "pista_didactica": "   "},
])
def test_invalid_flashcards_are_not_uploaded(monkeypatch, item):
    uploads = []
    monkeypatch.setattr(engine.rag_retriever, "retrieve_context", lambda **kwargs: ("context", [], 0.9))
    monkeypatch.setattr(LLMEngine, "_call_llm", lambda self, *args: {"items": [item]})
    monkeypatch.setattr(engine.oci_storage, "upload_educational_json", lambda *args: uploads.append(args))

    request = SolicitudAdaptacion(documento_titulo="Networks", documento_contenido="Source")
    with pytest.raises(ValueError):
        LLMEngine().adapt_content(request)

    assert uploads == []


@pytest.mark.parametrize("output_format,items", [
    (FormatoSalida.FLASHCARDS, [{"frente": "Question", "dorso": "Answer", "pista_didactica": "Hint"}]),
    (FormatoSalida.RESUMEN, [{"concept": "Flexible item"}]),
])
def test_valid_adaptation_uploads_success_payload(monkeypatch, output_format, items):
    uploads = []
    monkeypatch.setattr(engine.rag_retriever, "retrieve_context", lambda **kwargs: ("context", [], 0.9))
    monkeypatch.setattr(LLMEngine, "_call_llm", lambda self, *args: {"items": items})

    def upload(object_id, payload):
        uploads.append((object_id, payload))
        return AlmacenamientoOCI(bucket="outputs", objeto_id=object_id)

    monkeypatch.setattr(engine.oci_storage, "upload_educational_json", upload)
    request = SolicitudAdaptacion(
        documento_titulo="Networks", documento_contenido="Source", formato_salida=output_format
    )

    response = LLMEngine().adapt_content(request)

    assert len(uploads) == 1
    object_id, payload = uploads[0]
    assert object_id.endswith(".json")
    assert payload["status"] == response.status == "exito"
    assert payload["contenido_adaptado"]["items"] == response.contenido_adaptado.items == items
    assert payload["metadatos"] == response.metadatos.model_dump()
    assert payload["evaluacion_calidad"] == response.evaluacion_calidad.model_dump()
    assert response.almacenamiento_oci.objeto_id == object_id


def test_grounding_score_preserves_satisfactory_observed_similarity(monkeypatch):
    monkeypatch.setattr(
        "llm.engine.rag_retriever.retrieve_context",
        lambda query: ("Verified context", [{"text": "Verified context", "similarity": 0.86}], 0.86),
    )

    resp = llm_engine.adapt_content(_request())

    assert resp.evaluacion_calidad.anclaje_fuente_score == 0.86
    assert resp.evaluacion_calidad.anclaje_fuente_score >= 0.8


def test_grounding_score_preserves_insufficient_observed_similarity(monkeypatch):
    monkeypatch.setattr(
        "llm.engine.rag_retriever.retrieve_context",
        lambda query: ("Weak context", [{"text": "Weak context", "similarity": 0.42}], 0.42),
    )

    resp = llm_engine.adapt_content(_request())

    assert resp.evaluacion_calidad.anclaje_fuente_score == 0.42
    assert resp.evaluacion_calidad.anclaje_fuente_score < 0.8


def test_grounding_score_uses_zero_for_missing_retrieved_similarity(monkeypatch):
    monkeypatch.setattr(
        "llm.engine.rag_retriever.retrieve_context",
        lambda query: ("", [], 0.0),
    )

    resp = llm_engine.adapt_content(_request())

    assert resp.evaluacion_calidad.anclaje_fuente_score == 0.0
    assert resp.evaluacion_calidad.anclaje_fuente_score < 0.8
