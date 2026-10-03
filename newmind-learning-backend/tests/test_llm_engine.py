"""Pruebas del orquestador de adaptación pedagógica."""
import pytest

from models.schemas import AlmacenamientoOCI, SolicitudAdaptacion, PerfilDestinatario, FormatoSalida
from llm.engine import llm_engine


@pytest.fixture(autouse=True)
def stub_external_dependencies(monkeypatch):
    def fake_llm_response(system_prompt, user_prompt, request):
        return {
            "titulo": "Adapted content",
            "introduccion_contextualizada": "Contextualized introduction",
            "tiempo_estimado_estudio_minutos": 5,
            "conceptos_clave": ["Grounding", "Retrieval"],
            "items": [{"frente": "What is grounding?", "dorso": "Observed source fidelity."}],
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
