"""Pruebas del orquestador de adaptación pedagógica."""
from models.schemas import SolicitudAdaptacion, PerfilDestinatario, FormatoSalida
from llm.engine import llm_engine

def test_adapt_content_vcn_flashcards():
    req = SolicitudAdaptacion(
        documento_titulo="Introduccion a la Arquitectura de Redes VCN en OCI",
        documento_contenido="La Virtual Cloud Network (VCN) es una red privada en OCI con subredes y security lists.",
        perfil_destinatario=PerfilDestinatario.PRINCIPIANTE,
        formato_salida=FormatoSalida.FLASHCARDS
    )
    resp = llm_engine.adapt_content(req)
    assert resp.status == "exito"
    assert resp.metadatos.perfil_aplicado == "Principiante"
    assert resp.metadatos.formato_generado == "Flashcards"
    assert len(resp.contenido_adaptado.items) > 0
    assert resp.evaluacion_calidad.anclaje_fuente_score >= 0.8
    assert resp.almacenamiento_oci.objeto_id.endswith(".json")
