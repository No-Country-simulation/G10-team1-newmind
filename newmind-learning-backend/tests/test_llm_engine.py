"""Pruebas del orquestador de adaptación pedagógica."""
import pytest

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
