"""Scoped engine imports without settings, RAG, or OCI startup effects."""
import importlib
import io
import inspect
import logging
import re
import sys
from contextlib import ExitStack, contextmanager, nullcontext, redirect_stderr, redirect_stdout
from datetime import datetime, timezone
from types import ModuleType, SimpleNamespace
from unittest.mock import patch


def _forbidden(*args, **kwargs):
    raise AssertionError("External state is forbidden in provider tests")


@contextmanager
def isolated_engine():
    """Restore module entries and parent attributes, even after a failed test."""
    names = ("config", "config.settings", "rag", "rag.retriever",
             "storage", "storage.oci_client", "llm", "llm.engine", "llm.prompts")
    missing = object()
    previous = {name: sys.modules.get(name, missing) for name in names}
    parent_attributes = []
    for name in names:
        parent, _, child = name.rpartition(".")
        if parent and parent in sys.modules:
            module = sys.modules[parent]
            parent_attributes.append((module, child, getattr(module, child, missing)))
    stubs = {}
    for parent in ("config", "rag", "storage"):
        package = ModuleType(parent)
        package.__path__ = []
        stubs[parent] = package
    settings = ModuleType("config.settings")
    settings.settings = SimpleNamespace(
        GEMINI_API_KEY=None, GROK_API_KEY=None, OPENAI_API_KEY=None,
        OCI_BUCKET_OUTPUTS="outputs",
    )
    rag = ModuleType("rag.retriever")
    rag.rag_retriever = SimpleNamespace(retrieve_context=_forbidden)
    storage = ModuleType("storage.oci_client")
    storage.oci_storage = SimpleNamespace(upload_educational_json=_forbidden)
    stubs.update({"config.settings": settings, "rag.retriever": rag,
                  "storage.oci_client": storage})
    try:
        for name in ("llm", "llm.engine", "llm.prompts"):
            sys.modules.pop(name, None)
        sys.modules.update(stubs)
        yield importlib.import_module("llm.engine")
    finally:
        for name, original in previous.items():
            if original is missing:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = original
        for module, child, original in parent_attributes:
            if original is missing:
                module.__dict__.pop(child, None)
            else:
                setattr(module, child, original)


def smoke_selection(environ):
    """Resolve opt-in controls before inspecting any credential."""
    gate = environ.get("NEWMIND_SMOKE_GATE")
    provider = environ.get("NEWMIND_SMOKE_PROVIDER")
    alias = environ.get("NEWMIND_SMOKE_ENVIRONMENT")
    if gate is None and provider is None and alias is None:
        return None
    if (gate != "authorized" or provider not in ("gemini", "openai")
            or not isinstance(alias, str) or not re.fullmatch(r"env-[a-z0-9]{8,16}", alias)):
        raise ValueError("Invalid smoke controls")
    return provider, alias


@contextmanager
def bounded_gemini():
    """Bound one smoke invocation; restore factory and instance methods on exit."""
    import google.generativeai as genai

    factory = genai.GenerativeModel
    attempted = False
    with ExitStack() as patches:
        def make_model(*args, **kwargs):
            model = factory(*args, **kwargs)
            generate = model.generate_content
            options = dict(request_options={"retry": None, "timeout": 30},
                           generation_config={"response_mime_type": "application/json",
                                              "max_output_tokens": 1024, "candidate_count": 1})
            # Reject an incompatible signature before any generation request.
            inspect.signature(generate).bind("synthetic", **options)

            def generate_once(prompt):
                nonlocal attempted
                if attempted:
                    raise RuntimeError("Only one Gemini smoke invocation is permitted")
                attempted = True
                return generate(prompt, **options)

            patches.enter_context(patch.object(model, "generate_content", generate_once))
            return model

        patches.enter_context(patch.object(genai, "GenerativeModel", make_model))
        yield


def run_selected_smoke(environ):
    """Return safe evidence only; never propagate SDK errors or response bodies."""
    previous_logging = logging.root.manager.disable
    try:
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            logging.disable(sys.maxsize)
            selection = smoke_selection(environ)
            if selection is None:
                return {"validation": "skipped"}
            provider, alias = selection
            key = environ.get("GEMINI_API_KEY" if provider == "gemini" else "OPENAI_API_KEY")
            if not isinstance(key, str) or not key.strip():
                return {"validation": "missing_credential"}
            with isolated_engine() as engine:
                instance = engine.LLMEngine()
                instance.gemini_key = key if provider == "gemini" else None
                instance.openai_key = key if provider == "openai" else None
                instance.grok_key = None
                instance._generate_heuristic_demo = _forbidden
                request = engine.SolicitudAdaptacion(
                    documento_titulo="Synthetic network lesson",
                    documento_contenido="A subnet divides a virtual network.",
                    formato_salida=engine.FormatoSalida.FLASHCARDS,
                )
                with bounded_gemini() if provider == "gemini" else nullcontext():
                    payload = instance._call_llm(
                        "Return only a JSON object for a synthetic educational lesson.",
                        "Create exactly one short flashcard about a subnet. Include titulo, "
                        "introduccion_contextualizada, tiempo_estimado_estudio_minutos (integer), "
                        "conceptos_clave (string list), "
                        "items (list of frente, dorso, pista_didactica objects).",
                        request,
                    )
                instance._validate_generated(payload, request)
            return {
                "provider": provider,
                "model": "gemini-3.1-flash-lite" if provider == "gemini" else "gpt-4o-mini",
                "utc": datetime.now(timezone.utc).isoformat(),
                "environment": alias,
                "validation": "passed",
            }
    except BaseException:
        # No exception chaining, traceback, key, response, or provider error escapes.
        return {"validation": "failed"}
    finally:
        logging.disable(previous_logging)
