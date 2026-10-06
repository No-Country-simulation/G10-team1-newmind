"""Use-case orchestration across ingestion, RAG, LLM, and storage capabilities."""

from __future__ import annotations

import re
from pathlib import Path, PurePath
from typing import Any
from uuid import uuid4

from application.repositories import (
    AdaptationRecord,
    AdaptationRepository,
    DocumentRecord,
    DocumentRepository,
    utc_now,
)
from ingestion.loaders import (
    SUPPORTED_FORMATS,
    CorruptPdfError,
    EmptyDocumentError,
    InvalidTextEncodingError,
    PdfNoExtractableTextError,
)
from models.schemas import SolicitudAdaptacion


MAX_DOCUMENT_SIZE = 20 * 1024 * 1024
INGESTION_ERROR_MESSAGES = {
    EmptyDocumentError: "Document must not be empty.",
    InvalidTextEncodingError: "Document must contain valid UTF-8 text.",
    CorruptPdfError: "PDF document is corrupt.",
    PdfNoExtractableTextError: "PDF document contains no extractable text.",
}


class DocumentValidationError(ValueError):
    pass


class DocumentProcessingError(RuntimeError):
    pass


def sanitize_filename(filename: str) -> str:
    basename = PurePath(filename.replace("\\", "/")).name
    safe_name = re.sub(r"[^A-Za-z0-9._-]+", "-", basename).strip(".-")
    return safe_name or "document"


class DocumentService:
    def __init__(
        self,
        repository: DocumentRepository | None = None,
        *,
        loader: Any = None,
        chunker: Any = None,
        vector_store: Any = None,
        storage: Any = None,
    ) -> None:
        self.repository = repository or DocumentRepository()
        if loader is None:
            from ingestion.loaders import doc_loader

            loader = doc_loader
        if chunker is None:
            from ingestion.chunker import doc_chunker

            chunker = doc_chunker
        if vector_store is None:
            from rag.vector_store import vector_store as default_vector_store

            vector_store = default_vector_store
        if storage is None:
            from storage.oci_client import oci_storage

            storage = oci_storage
        self.loader = loader
        self.chunker = chunker
        self.vector_store = vector_store
        self.storage = storage

    def upload(self, filename: str, content: bytes, content_type: str) -> DocumentRecord:
        safe_filename = sanitize_filename(filename)
        suffix = Path(safe_filename).suffix.lower()
        if suffix not in SUPPORTED_FORMATS:
            raise DocumentValidationError("Unsupported document type. Allowed types: PDF, MD, TXT.")
        if len(content) > MAX_DOCUMENT_SIZE:
            raise DocumentValidationError("Document exceeds the 20 MB size limit.")
        if not content:
            raise DocumentValidationError("Document must not be empty.")

        try:
            normalized_document = self.loader.extract_from_bytes(safe_filename, content)
        except tuple(INGESTION_ERROR_MESSAGES) as exc:
            raise DocumentValidationError(INGESTION_ERROR_MESSAGES[type(exc)]) from exc
        except Exception as exc:
            raise DocumentProcessingError("Document content could not be extracted.") from exc
        record = self.repository.create(
            title=Path(safe_filename).stem,
            filename=filename,
            document_type=normalized_document.type.value,
            size=len(content),
            content=normalized_document.text,
            storage_object_id=f"{uuid4().hex}-{safe_filename}",
        )

        try:
            chunks = self.chunker.split_document(normalized_document)
            self.vector_store.add_chunks(chunks)
            storage = self.storage.upload_raw_document(
                record.storage_object_id, content, content_type
            )
            record = self.repository.update_storage(record.id, storage)
        except Exception as exc:
            self.repository.delete(record.id)
            raise DocumentProcessingError("Document could not be indexed or stored.") from exc
        return record

    def list(self) -> list[DocumentRecord]:
        # Upload reserves a record before indexing; publish only stored originals.
        return [record for record in self.repository.list() if record.storage is not None]

    def get(self, document_id: int) -> DocumentRecord | None:
        record = self.repository.get(document_id)
        return record if record is not None and record.storage is not None else None

    def delete(self, document_id: int) -> bool:
        return self.repository.delete(document_id)


class AdaptationService:
    def __init__(
        self,
        document_service: DocumentService,
        repository: AdaptationRepository | None = None,
        *,
        engine: Any = None,
    ) -> None:
        self.document_service = document_service
        self.repository = repository or AdaptationRepository()
        if engine is None:
            from llm.engine import llm_engine

            engine = llm_engine
        self.engine = engine

    def create(
        self,
        *,
        document_id: int,
        profile: str,
        format: str,
        industry: str,
        detail_level: str,
        domain_request: SolicitudAdaptacion,
    ) -> AdaptationRecord | None:
        document = self.document_service.get(document_id)
        if document is None:
            return None
        return self.repository.create(
            document_id=document.id,
            document_title=document.title,
            profile=profile,
            format=format,
            industry=industry,
            detail_level=detail_level,
            domain_request=domain_request,
        )

    def process(self, adaptation_id: int) -> None:
        record = self.repository.update(adaptation_id, status="processing", error=None)
        if record is None:
            return
        try:
            result = self.engine.adapt_content(record.domain_request)
            score = result.evaluacion_calidad.anclaje_fuente_score
            self.repository.update(
                adaptation_id,
                status="completed",
                official_response=result.model_dump(mode="json"),
                content=result.contenido_adaptado.model_dump(mode="json"),
                evaluation={
                    "approved": score >= 0.8,
                    "score": score,
                    "criteria": {
                        "fidelity": score,
                        "profile_alignment": score,
                        "format_compliance": score,
                        "coherence": score,
                    },
                    "issues": [],
                },
                iteration=1,
                completed_at=utc_now(),
            )
        except Exception as exc:
            self.repository.update(
                adaptation_id,
                status="failed",
                error=str(exc) or "Adaptation processing failed.",
                completed_at=utc_now(),
            )

    def get(self, adaptation_id: int) -> AdaptationRecord | None:
        return self.repository.get(adaptation_id)

    def list(
        self,
        *,
        profile: str | None = None,
        format: str | None = None,
        status: str | None = None,
    ) -> list[AdaptationRecord]:
        records = self.repository.list()
        return [
            record
            for record in records
            if (profile is None or record.profile == profile)
            and (format is None or record.format == format)
            and (status is None or record.status == status)
        ]
