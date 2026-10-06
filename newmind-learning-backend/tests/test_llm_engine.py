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


def _generated_payload(*, items=None):
    return {
        "titulo": "Adapted networks",
        "introduccion_contextualizada": "An introduction to networks.",
        "tiempo_estimado_estudio_minutos": 5,
        "conceptos_clave": ["VCN"],
        "items": items if items is not None else [
            {"frente": "What is a VCN?", "dorso": "A virtual network.", "pista_didactica": "Think of a neighborhood."}
        ],
    }


def _provider_engine(monkeypatch, *, grok=None, gemini=None, openai=None):
    monkeypatch.setattr(engine, "settings", SimpleNamespace(
        GROK_API_KEY=grok, GEMINI_API_KEY=gemini, OPENAI_API_KEY=openai,
        OCI_BUCKET_OUTPUTS="outputs",
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


def test_no_gemini_key_uses_grok_endpoint_and_json_mode(monkeypatch):
    calls = []
    payload = _generated_payload(items=[])
    _mock_openai_sdk(monkeypatch, calls, {"grok": json.dumps(payload)})
    provider = _provider_engine(monkeypatch, grok="xai-test-key", openai="openai-test-key")

    assert provider._call_llm("system", "user", _request()) == payload
    assert calls == [
        ("grok", "xai-test-key", {"base_url": "https://api.x.ai/v1"}),
        ("grok", {
            "model": "grok-4.7",
            "messages": [{"role": "system", "content": "system"}, {"role": "user", "content": "user"}],
            "response_format": {"type": "json_object"},
        }),
    ]


@pytest.mark.parametrize("gemini_outcome", [RuntimeError("secret-in-provider-error"), "not json"])
def test_gemini_failure_falls_through_to_grok_then_openai(monkeypatch, caplog, gemini_outcome):
    calls = []
    payload = _generated_payload()
    _mock_openai_sdk(monkeypatch, calls, {"grok": RuntimeError("grok-secret-in-error"), "openai": json.dumps(payload)})
    _mock_gemini_sdk(monkeypatch, calls, gemini_outcome)
    provider = _provider_engine(monkeypatch, grok="secret-xai", gemini="secret-gemini", openai="secret-openai")

    with caplog.at_level(logging.WARNING, logger="llm.engine"):
        assert provider._call_llm("system", "user", _request()) == payload

    assert [call[0] for call in calls] == ["gemini_config", "gemini_model", "gemini", "grok", "grok", "openai", "openai"]
    assert "secret" not in caplog.text
    assert "Grok" in caplog.text and "Gemini" in caplog.text


def test_gemini_wins_when_both_keys_are_configured(monkeypatch):
    calls = []
    payload = _generated_payload()
    _mock_openai_sdk(monkeypatch, calls, {"grok": json.dumps(_generated_payload(items=[])), "openai": json.dumps(payload)})
    _mock_gemini_sdk(monkeypatch, calls, json.dumps(payload))
    provider = _provider_engine(monkeypatch, grok="grok-test-key", gemini="gemini-test-key", openai="openai-test-key")

    assert provider._call_llm("system", "user", _request()) == payload
    assert [call[0] for call in calls] == ["gemini_config", "gemini_model", "gemini"]


@pytest.mark.parametrize("gemini_outcome", [RuntimeError("secret-gemini-error"), "not json", json.dumps({"items": []})])
def test_gemini_failure_or_invalid_payload_uses_grok_before_openai(monkeypatch, caplog, gemini_outcome):
    calls = []
    payload = _generated_payload()
    _mock_gemini_sdk(monkeypatch, calls, gemini_outcome)
    _mock_openai_sdk(monkeypatch, calls, {"grok": json.dumps(payload), "openai": json.dumps(_generated_payload(items=[]))})
    provider = _provider_engine(monkeypatch, gemini="secret-gemini", grok="secret-grok", openai="secret-openai")

    with caplog.at_level(logging.WARNING, logger="llm.engine"):
        assert provider._call_llm("system", "user", _request()) == payload

    assert [call[0] for call in calls] == ["gemini_config", "gemini_model", "gemini", "grok", "grok"]
    assert "secret" not in caplog.text


def test_all_providers_fail_and_heuristic_remains_available(monkeypatch, caplog):
    calls = []
    _mock_openai_sdk(monkeypatch, calls, {"grok": "not json", "openai": RuntimeError("secret-openai-error")})
    _mock_gemini_sdk(monkeypatch, calls, "not json")
    provider = _provider_engine(monkeypatch, grok="secret-xai", gemini="secret-gemini", openai="secret-openai")

    with caplog.at_level(logging.WARNING, logger="llm.engine"):
        result = provider._call_llm("system", "user", _request())

    assert result == provider._generate_heuristic_demo(_request())
    assert [call[0] for call in calls] == ["gemini_config", "gemini_model", "gemini", "grok", "grok", "openai", "openai"]
    assert "secret" not in caplog.text


def test_no_keys_uses_heuristic_without_importing_providers(monkeypatch):
    provider = _provider_engine(monkeypatch)
    assert provider._call_llm("system", "user", _request()) == provider._generate_heuristic_demo(_request())


@pytest.mark.parametrize("invalid", [
    ["not an object"],
    {"items": []},
    {**_generated_payload(), "conceptos_clave": "not a list"},
    {**_generated_payload(), "tiempo_estimado_estudio_minutos": "not an integer"},
    {**_generated_payload(), "items": ["not an item"]},
    {**_generated_payload(), "items": [{"frente": "Question", "dorso": "Answer"}]},
    {**_generated_payload(), "items": [{"frente": "Question", "dorso": "Answer", "pista_didactica": "  "}]},
])
def test_invalid_gemini_payload_falls_through_to_grok_without_leaking_details(monkeypatch, caplog, invalid):
    calls = []
    valid = _generated_payload()
    _mock_openai_sdk(monkeypatch, calls, {"grok": json.dumps(valid), "openai": json.dumps(valid)})
    _mock_gemini_sdk(monkeypatch, calls, json.dumps(invalid))
    provider = _provider_engine(monkeypatch, grok="secret-xai", gemini="secret-gemini", openai="secret-openai")

    with caplog.at_level(logging.WARNING, logger="llm.engine"):
        assert provider._call_llm("system", "user", _request()) == valid

    assert [call[0] for call in calls] == ["gemini_config", "gemini_model", "gemini", "grok", "grok"]
    assert "secret" not in caplog.text
    assert "not an item" not in caplog.text


@pytest.mark.parametrize("output_format,invalid_item", [
    (FormatoSalida.QUIZ, {"pregunta": "Question", "opciones": ["A"], "respuesta_correcta": "A"}),
    (FormatoSalida.TUTORIAL, {"paso": 1, "titulo_paso": "Step", "descripcion": "Do it"}),
])
def test_invalid_format_item_from_gemini_falls_through_to_openai(monkeypatch, output_format, invalid_item):
    calls = []
    valid = _generated_payload(items=[])
    _mock_openai_sdk(monkeypatch, calls, {"openai": json.dumps(valid)})
    _mock_gemini_sdk(monkeypatch, calls, json.dumps(_generated_payload(items=[invalid_item])))
    provider = _provider_engine(monkeypatch, gemini="gemini-key", openai="openai-key")

    assert provider._call_llm("system", "user", _request().model_copy(update={"formato_salida": output_format})) == valid
    assert [call[0] for call in calls] == ["gemini_config", "gemini_model", "gemini", "openai", "openai"]


def test_invalid_openai_payload_uses_heuristic_before_upload(monkeypatch):
    calls = []
    uploads = []
    _mock_openai_sdk(monkeypatch, calls, {"openai": json.dumps(_generated_payload(items=[{"frente": "broken"}]))})
    monkeypatch.setattr(engine.rag_retriever, "retrieve_context", lambda **kwargs: ("context", [], 0.9))

    def upload(object_id, payload):
        uploads.append(payload)
        return AlmacenamientoOCI(bucket="outputs", objeto_id=object_id)

    monkeypatch.setattr(engine.oci_storage, "upload_educational_json", upload)
    provider = _provider_engine(monkeypatch, openai="openai-key")

    response = provider.adapt_content(_request())

    assert [call[0] for call in calls] == ["openai", "openai"]
    assert response.contenido_adaptado.items == provider._generate_heuristic_demo(_request())["items"]
    assert len(uploads) == 1
    assert uploads[0]["contenido_adaptado"]["items"] == response.contenido_adaptado.items


def test_invalid_grok_and_gemini_use_valid_openai_before_upload(monkeypatch):
    calls = []
    uploads = []
    valid = _generated_payload()
    _mock_openai_sdk(monkeypatch, calls, {
        "grok": json.dumps(_generated_payload(items=[{"frente": "broken"}])),
        "openai": json.dumps(valid),
    })
    _mock_gemini_sdk(monkeypatch, calls, json.dumps(_generated_payload(items=[{"frente": "broken"}])))
    monkeypatch.setattr(engine.rag_retriever, "retrieve_context", lambda **kwargs: ("context", [], 0.9))

    def upload(object_id, payload):
        uploads.append(payload)
        return AlmacenamientoOCI(bucket="outputs", objeto_id=object_id)

    monkeypatch.setattr(engine.oci_storage, "upload_educational_json", upload)
    provider = _provider_engine(monkeypatch, grok="grok-key", gemini="gemini-key", openai="openai-key")

    response = provider.adapt_content(_request())

    assert [call[0] for call in calls] == [
        "gemini_config", "gemini_model", "gemini", "grok", "grok", "openai", "openai"
    ]
    assert len(uploads) == 1
    assert uploads[0]["contenido_adaptado"]["items"] == response.contenido_adaptado.items == valid["items"]


@pytest.mark.parametrize("output_format,item", [
    (FormatoSalida.QUIZ, {
        "pregunta": "Question", "opciones": ["A", "B"], "respuesta_correcta": "A",
        "justificacion_didactica": "Grounded explanation",
    }),
    (FormatoSalida.TUTORIAL, {
        "paso": 1, "titulo_paso": "Step", "descripcion": "Do it", "verificacion": "Check it",
    }),
])
def test_valid_format_items_preserve_provider_response(monkeypatch, output_format, item):
    calls = []
    payload = _generated_payload(items=[item])
    _mock_openai_sdk(monkeypatch, calls, {"grok": json.dumps(payload)})
    provider = _provider_engine(monkeypatch, grok="grok-key")

    assert provider._call_llm("system", "user", _request().model_copy(update={"formato_salida": output_format})) == payload
    assert [call[0] for call in calls] == ["grok", "grok"]


@pytest.mark.parametrize("output_format", [FormatoSalida.RESUMEN, FormatoSalida.GUION])
def test_flexible_formats_accept_structurally_valid_items(monkeypatch, output_format):
    calls = []
    payload = _generated_payload(items=[{"concept": "Flexible item"}])
    _mock_openai_sdk(monkeypatch, calls, {"grok": json.dumps(payload)})
    provider = _provider_engine(monkeypatch, grok="grok-key")

    assert provider._call_llm("system", "user", _request().model_copy(update={"formato_salida": output_format})) == payload
    assert [call[0] for call in calls] == ["grok", "grok"]


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
