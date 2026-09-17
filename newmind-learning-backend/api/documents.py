"""Document HTTP endpoints."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Response, UploadFile, status

from api.dependencies import get_document_service
from api.schemas import DocumentResponse
from application.services import (
    MAX_DOCUMENT_SIZE,
    DocumentProcessingError,
    DocumentService,
    DocumentValidationError,
)


router = APIRouter(prefix="/documents", tags=["documents"])


def to_response(record: Any) -> DocumentResponse:
    return DocumentResponse(
        id=record.id,
        title=record.title,
        type=record.type,
        size=record.size,
        created_at=record.created_at,
    )


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile,
    service: Annotated[DocumentService, Depends(get_document_service)],
) -> DocumentResponse:
    content = await file.read(MAX_DOCUMENT_SIZE + 1)
    try:
        record = service.upload(
            filename=file.filename or "document",
            content=content,
            content_type=file.content_type or "application/octet-stream",
        )
    except DocumentValidationError as exc:
        status_code = (
            status.HTTP_413_CONTENT_TOO_LARGE
            if len(content) > MAX_DOCUMENT_SIZE
            else status.HTTP_422_UNPROCESSABLE_CONTENT
        )
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc
    except DocumentProcessingError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)) from exc
    finally:
        await file.close()
    return to_response(record)


@router.get("", response_model=list[DocumentResponse])
def list_documents(
    service: Annotated[DocumentService, Depends(get_document_service)],
) -> list[DocumentResponse]:
    return [to_response(record) for record in service.list()]


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: int,
    service: Annotated[DocumentService, Depends(get_document_service)],
) -> DocumentResponse:
    record = service.get(document_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    return to_response(record)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: int,
    service: Annotated[DocumentService, Depends(get_document_service)],
) -> Response:
    if not service.delete(document_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
