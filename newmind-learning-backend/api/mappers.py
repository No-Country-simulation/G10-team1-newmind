"""Explicit mappings between frontend transport values and domain contracts."""

from api.schemas import AdaptationCreateRequest, AdaptationResponse, AdaptationStatusResponse
from application.repositories import AdaptationRecord, DocumentRecord
from models.schemas import FormatoSalida, NichoSector, NivelDetalle, PerfilDestinatario, SolicitudAdaptacion


PROFILE_TO_DOMAIN = {
    "Principiante": PerfilDestinatario.PRINCIPIANTE,
    "Junior": PerfilDestinatario.JUNIOR_MID,
    "Senior": PerfilDestinatario.JUNIOR_MID,
    "Lider": PerfilDestinatario.ARQUITECTO,
    "Gestor": PerfilDestinatario.EJECUTIVO,
}

FORMAT_TO_DOMAIN = {
    "Flashcards": FormatoSalida.FLASHCARDS,
    "Tutorial": FormatoSalida.TUTORIAL,
    "Quiz": FormatoSalida.QUIZ,
    "Resumen Ejecutivo": FormatoSalida.RESUMEN,
    "Guion": FormatoSalida.GUION,
}

INDUSTRY_TO_DOMAIN = {
    "Fintech": NichoSector.FINTECH,
    "Salud": NichoSector.SALUD,
    "E-commerce": NichoSector.ECOMMERCE,
    "General": NichoSector.GENERAL,
}

DETAIL_TO_DOMAIN = {
    "Basico": NivelDetalle.DIDACTICO,
    "Intermedio": NivelDetalle.TECNICO,
    "Didactico": NivelDetalle.DIDACTICO,
    "Detallado": NivelDetalle.TECNICO,
}


def to_domain_request(payload: AdaptationCreateRequest, document: DocumentRecord) -> SolicitudAdaptacion:
    return SolicitudAdaptacion(
        documento_titulo=document.title,
        documento_contenido=document.content,
        perfil_destinatario=PROFILE_TO_DOMAIN[payload.profile.value],
        formato_salida=FORMAT_TO_DOMAIN[payload.format.value],
        nicho_sector=INDUSTRY_TO_DOMAIN[payload.industry.value],
        nivel_detalle=DETAIL_TO_DOMAIN[payload.detail_level.value],
    )


def to_adaptation_response(record: AdaptationRecord) -> AdaptationResponse:
    return AdaptationResponse(
        id=record.id,
        document_id=record.document_id,
        document_title=record.document_title,
        profile=record.profile,
        format=record.format,
        industry=record.industry,
        detail_level=record.detail_level,
        status=record.status,
        content=record.content,
        evaluation=record.evaluation,
        iteration=record.iteration,
        created_at=record.created_at,
        completed_at=record.completed_at,
        error=record.error,
    )


def to_status_response(record: AdaptationRecord) -> AdaptationStatusResponse:
    return AdaptationStatusResponse(
        id=record.id,
        status=record.status,
        completed_at=record.completed_at,
        error=record.error,
    )
