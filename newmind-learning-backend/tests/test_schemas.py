"""Pruebas de esquemas Pydantic y contratos de datos oficiales."""
import pytest
from models.schemas import (
    SolicitudAdaptacion,
    RespuestaAdaptacion,
    MetadatosAprendizaje,
    ContenidoAdaptado,
    EvaluacionCalidad,
    AlmacenamientoOCI,
    PerfilDestinatario,
    FormatoSalida
)

def test_solicitud_adaptacion_valida():
    req = SolicitudAdaptacion(
        documento_titulo="VCN OCI",
        documento_contenido="Contenido de prueba de Virtual Cloud Network",
        perfil_destinatario=PerfilDestinatario.PRINCIPIANTE,
        formato_salida=FormatoSalida.FLASHCARDS
    )
    assert req.documento_titulo == "VCN OCI"
    assert req.perfil_destinatario == PerfilDestinatario.PRINCIPIANTE

def test_respuesta_adaptacion_valida():
    resp = RespuestaAdaptacion(
        status="exito",
        metadatos=MetadatosAprendizaje(
            perfil_aplicado="Principiante",
            formato_generado="Flashcards",
            tiempo_estimado_estudio_minutos=5,
            conceptos_clave=["VCN", "Subredes"]
        ),
        contenido_adaptado=ContenidoAdaptado(
            titulo="Redes desde Cero",
            introduccion_contextualizada="Analogía de prueba",
            items=[{"frente": "Q1", "dorso": "A1", "pista_didactica": "Pista"}]
        ),
        evaluacion_calidad=EvaluacionCalidad(
            anclaje_fuente_score=0.98,
            claridad_pedagogica="Alta",
            observaciones="Sin tecnicismos excesivos"
        ),
        almacenamiento_oci=AlmacenamientoOCI(
            bucket="nuevamente-contenidos-educativos",
            objeto_id="contenido-001.json",
            status_upload="completado"
        )
    )
    assert resp.status == "exito"
    assert resp.metadatos.tiempo_estimado_estudio_minutos == 5
    assert resp.evaluacion_calidad.anclaje_fuente_score == 0.98


def build_response(items, formato_generado="Flashcards"):
    return RespuestaAdaptacion(
        status="exito",
        metadatos=MetadatosAprendizaje(
            perfil_aplicado="Principiante",
            formato_generado=formato_generado,
            tiempo_estimado_estudio_minutos=5,
            conceptos_clave=["VCN"],
        ),
        contenido_adaptado=ContenidoAdaptado(
            titulo="Redes desde Cero",
            introduccion_contextualizada="Analogía de prueba",
            items=items,
        ),
        evaluacion_calidad=EvaluacionCalidad(
            anclaje_fuente_score=0.98,
            claridad_pedagogica="Alta",
            observaciones="Contenido validado",
        ),
        almacenamiento_oci=AlmacenamientoOCI(
            bucket="nuevamente-contenidos-educativos",
            objeto_id="contenido-001.json",
        ),
    )


def canonical_flashcard():
    return {
        "frente": "¿Qué es una VCN?",
        "dorso": "Una red privada virtual en OCI.",
        "pista_didactica": "Considere una red privada.",
    }


@pytest.mark.parametrize("missing_field", ["frente", "dorso", "pista_didactica"])
def test_flashcards_reject_items_with_missing_canonical_fields(missing_field):
    item = canonical_flashcard()
    item.pop(missing_field)

    with pytest.raises(ValueError):
        build_response([item])


@pytest.mark.parametrize("blank_field", ["frente", "dorso", "pista_didactica"])
def test_flashcards_reject_items_with_blank_canonical_fields(blank_field):
    item = canonical_flashcard()
    item[blank_field] = "   "

    with pytest.raises(ValueError):
        build_response([item])


def test_flashcards_reject_arbitrary_item_shapes():
    with pytest.raises(ValueError):
        build_response([{"concept": "API contract"}])


def test_non_flashcards_preserve_flexible_item_shapes():
    response = build_response(
        [{"concept": "API contract"}],
        formato_generado="Resumen Ejecutivo (TL;DR)",
    )

    assert response.contenido_adaptado.items == [{"concept": "API contract"}]
