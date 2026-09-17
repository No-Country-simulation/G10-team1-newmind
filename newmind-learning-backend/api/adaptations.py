"""Adaptation HTTP endpoints."""

from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status

from api.dependencies import get_adaptation_service
from api.mappers import to_adaptation_response, to_domain_request, to_status_response
from api.schemas import (
    AdaptationCreateRequest,
    AdaptationResponse,
    AdaptationStatus,
    AdaptationStatusResponse,
    FormatValue,
    ProfileValue,
)
from application.services import AdaptationService


router = APIRouter(prefix="/adaptations", tags=["adaptations"])


@router.post("", response_model=AdaptationResponse, status_code=status.HTTP_202_ACCEPTED)
def create_adaptation(
    payload: AdaptationCreateRequest,
    background_tasks: BackgroundTasks,
    service: Annotated[AdaptationService, Depends(get_adaptation_service)],
) -> AdaptationResponse:
    document = service.document_service.get(payload.document_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    domain_request = to_domain_request(payload, document)
    record = service.create(
        document_id=payload.document_id,
        profile=payload.profile.value,
        format=payload.format.value,
        industry=payload.industry.value,
        detail_level=payload.detail_level.value,
        domain_request=domain_request,
    )
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    background_tasks.add_task(service.process, record.id)
    return to_adaptation_response(record)


@router.get("", response_model=list[AdaptationResponse])
def list_adaptations(
    service: Annotated[AdaptationService, Depends(get_adaptation_service)],
    profile: Annotated[ProfileValue | None, Query()] = None,
    format: Annotated[FormatValue | None, Query()] = None,
    status_filter: Annotated[AdaptationStatus | None, Query(alias="status")] = None,
) -> list[AdaptationResponse]:
    records = service.list(
        profile=profile.value if profile else None,
        format=format.value if format else None,
        status=status_filter.value if status_filter else None,
    )
    return [to_adaptation_response(record) for record in records]


@router.get("/{adaptation_id}/status", response_model=AdaptationStatusResponse)
def get_adaptation_status(
    adaptation_id: int,
    service: Annotated[AdaptationService, Depends(get_adaptation_service)],
) -> AdaptationStatusResponse:
    record = service.get(adaptation_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Adaptation not found.")
    return to_status_response(record)


@router.get("/{adaptation_id}", response_model=AdaptationResponse)
def get_adaptation(
    adaptation_id: int,
    service: Annotated[AdaptationService, Depends(get_adaptation_service)],
) -> AdaptationResponse:
    record = service.get(adaptation_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Adaptation not found.")
    return to_adaptation_response(record)
