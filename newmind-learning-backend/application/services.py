
"""Use-case orchestration across ingestion, RAG, LLM, and storage."""

from __future__ import annotations

import logging
import re
from datetime import datetime
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
from storage.contracts import StorageResult


logger = logging.getLogger(__name__)

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
    safe_name = re.sub(
        r"[^A-Za-z0-9._-]+",
        "-",
        basename,
    ).strip(".-")
    return safe_name or "document"


def _parse_datetime(value: str | datetime | None) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(value)


def _storage_result_to_dict(
    storage: StorageResult | None,
) -> dict[str, Any] | None:
    if storage is None:
        return None

    return {
        "mode": storage.mode,
        "status": storage.status,
        "bucket": storage.bucket,
        "object_id": storage.object_id,
        "etag": storage.etag,
        "error_code": storage.error_code,
    }


def _storage_result_from_dict(
    data: dict[str, Any] | None,
) -> StorageResult | None:
    if data is None:
        return None

    return StorageResult(**data)


def _document_to_metadata(record: DocumentRecord) -> dict[str, Any]:
    return {
        "id": record.id,
        "title": record.title,
        "filename": record.filename,
        "type": record.type,
        "size": record.size,
        "content": record.content,
        "created_at": record.created_at.isoformat(),
        "storage_object_id": record.storage_object_id,
        "storage": _storage_result_to_dict(record.storage),
        "rag_document_id": record.rag_document_id,
    }


def _document_from_metadata(data: dict[str, Any]) -> DocumentRecord:
    return DocumentRecord(
        id=int(data["id"]),
        title=data["title"],
        filename=data["filename"],
        type=data["type"],
        size=int(data["size"]),
        content=data["content"],
        created_at=_parse_datetime(data["created_at"]),
        storage_object_id=data["storage_object_id"],
        storage=_storage_result_from_dict(data.get("storage")),
        rag_document_id=data["rag_document_id"],
    )


def _adaptation_to_metadata(
    record: AdaptationRecord,
) -> dict[str, Any]:
    return {
        "id": record.id,
        "document_id": record.document_id,
        "document_title": record.document_title,
        "profile": record.profile,
        "format": record.format,
        "industry": record.industry,
        "detail_level": record.detail_level,
        "status": record.status,
        "domain_request": record.domain_request.model_dump(mode="json"),
        "created_at": record.created_at.isoformat(),
        "completed_at": (
            record.completed_at.isoformat()
            if record.completed_at is not None
            else None
        ),
        "content": record.content,
        "evaluation": record.evaluation,
        "official_response": record.official_response,
        "iteration": record.iteration,
        "error": record.error,
        "json_storage_object_id": record.json_storage_object_id,
        "json_storage_status": record.json_storage_status,
    }


def _adaptation_from_metadata(
    data: dict[str, Any],
) -> AdaptationRecord:
    return AdaptationRecord(
        id=int(data["id"]),
        document_id=int(data["document_id"]),
        document_title=data["document_title"],
        profile=data["profile"],
        format=data["format"],
        industry=data["industry"],
        detail_level=data["detail_level"],
        status=data["status"],
        domain_request=SolicitudAdaptacion.model_validate(
            data["domain_request"]
        ),
        created_at=_parse_datetime(data["created_at"]),
        completed_at=_parse_datetime(data.get("completed_at")),
        content=data.get("content"),
        evaluation=data.get("evaluation"),
        official_response=data.get("official_response"),
        iteration=data.get("iteration"),
        error=data.get("error"),
        json_storage_object_id=data.get("json_storage_object_id"),
        json_storage_status=data.get("json_storage_status"),
    )


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
            from storage.factory import object_storage
            storage = object_storage

        self.loader = loader
        self.chunker = chunker
        self.vector_store = vector_store
        self.storage = storage

        self._restore_metadata()

    def _restore_metadata(self) -> None:
        """Restore document records when the storage provider supports it."""
        list_metadata = getattr(self.storage, "list_metadata", None)
        if not callable(list_metadata):
            return

        from config.settings import settings

        provider = (settings.STORAGE_PROVIDER or "oci").strip().lower()
        if provider != "b2":
            return

        raw_records = list_metadata("document")
        records = [
            _document_from_metadata(item)
            for item in raw_records
        ]
        self.repository.restore(records)

        logger.info(
            "Restored %s document metadata records.",
            len(records),
        )

    def _persist_metadata(self, record: DocumentRecord) -> None:
        from config.settings import settings

        provider = (settings.STORAGE_PROVIDER or "oci").strip().lower()
        if provider != "b2":
            return

        save_metadata = getattr(self.storage, "save_metadata", None)
        if not callable(save_metadata):
            # Test doubles and legacy storage adapters may not implement B2
            # metadata persistence.
            return

        save_metadata(
            "document",
            record.id,
            _document_to_metadata(record),
        )

    def upload(
        self,
        filename: str,
        content: bytes,
        content_type: str,
    ) -> DocumentRecord:
        safe_filename = sanitize_filename(filename)
        suffix = Path(safe_filename).suffix.lower()

        if suffix not in SUPPORTED_FORMATS:
            raise DocumentValidationError(
                "Unsupported document type. Allowed types: PDF, MD, TXT."
            )

        if len(content) > MAX_DOCUMENT_SIZE:
            raise DocumentValidationError(
                "Document exceeds the 20 MB size limit."
            )

        if not content:
            raise DocumentValidationError("Document must not be empty.")

        try:
            normalized_document = self.loader.extract_from_bytes(
                safe_filename,
                content,
            )
        except tuple(INGESTION_ERROR_MESSAGES) as exc:
            raise DocumentValidationError(
                INGESTION_ERROR_MESSAGES[type(exc)]
            ) from exc
        except Exception as exc:
            raise DocumentProcessingError(
                "Document content could not be extracted."
            ) from exc

        record = self.repository.create(
            title=Path(safe_filename).stem,
            filename=filename,
            document_type=normalized_document.type.value,
            size=len(content),
            content=normalized_document.text,
            storage_object_id=f"{uuid4().hex}-{safe_filename}",
        )

        try:
            chunks = self.chunker.split_document(
                normalized_document,
                document_id=record.rag_document_id,
            )
            self.vector_store.add_chunks(chunks)

            storage_result = self.storage.upload_raw_document(
                record.storage_object_id,
                content,
                content_type,
            )

            from config.settings import settings

            provider = (
                settings.STORAGE_PROVIDER or "oci"
            ).strip().lower()

            if provider == "b2" and storage_result.mode != "b2":
                raise DocumentProcessingError(
                    "The original document was not confirmed in Backblaze B2."
                )

            record = self.repository.update_storage(
                record.id,
                storage_result,
            )

            # Persist only after the original file has been confirmed in B2.
            self._persist_metadata(record)

        except Exception as exc:
            self.repository.delete(record.id)
            raise DocumentProcessingError(
                "Document could not be indexed or stored."
            ) from exc

        return record

    def list(self) -> list[DocumentRecord]:
        # Publish only records with confirmed original-file storage.
        return [
            record
            for record in self.repository.list()
            if record.storage is not None
        ]

    def get(self, document_id: int) -> DocumentRecord | None:
        record = self.repository.get(document_id)
        return (
            record
            if record is not None and record.storage is not None
            else None
        )


    def rebuild_rag_index(self) -> dict[str, int]:
        """Rebuild the ChromaDB index from original documents stored in B2."""
        from config.settings import settings

        provider = (settings.STORAGE_PROVIDER or "oci").strip().lower()
        if provider != "b2":
            logger.info("RAG rebuild skipped: storage provider is not B2.")
            return {"documents": 0, "chunks": 0, "failed": 0}

        download_document = getattr(
            self.storage, "download_raw_document", None
        )
        add_chunks = getattr(self.vector_store, "add_chunks", None)

        if not callable(download_document) or not callable(add_chunks):
            logger.warning(
                "RAG rebuild skipped: storage or vector store "
                "does not support the required operations."
            )
            return {"documents": 0, "chunks": 0, "failed": 0}

        documents_indexed = 0
        chunks_indexed = 0
        documents_failed = 0

        for record in self.list():
            try:
                if not record.storage_object_id or not record.rag_document_id:
                    raise ValueError(
                        "Document metadata lacks its storage or RAG identifier."
                    )

                original_content = download_document(record.storage_object_id)

                normalized_document = self.loader.extract_from_bytes(
                    sanitize_filename(record.filename),
                    original_content,
                )

                chunks = self.chunker.split_document(
                    normalized_document,
                    document_id=record.rag_document_id,
                )

                add_chunks(chunks)

                documents_indexed += 1
                chunks_indexed += len(chunks)

                logger.info(
                    "RAG document restored: document_id=%s, chunks=%s",
                    record.id,
                    len(chunks),
                )

            except Exception:
                documents_failed += 1
                logger.exception(
                    "Could not rebuild RAG index for document_id=%s",
                    record.id,
                )

        logger.info(
            "RAG rebuild finished: documents=%s, chunks=%s, failed=%s",
            documents_indexed,
            chunks_indexed,
            documents_failed,
        )

        return {
            "documents": documents_indexed,
            "chunks": chunks_indexed,
            "failed": documents_failed,
        }


    def delete(self, document_id: int) -> bool:
        from config.settings import settings

        record = self.repository.get(document_id)
        if record is None:
            return False

        provider = (settings.STORAGE_PROVIDER or "oci").strip().lower()

        if provider == "b2":
            delete_metadata = getattr(
                self.storage,
                "delete_metadata",
                None,
            )
            if callable(delete_metadata):
                delete_metadata("document", document_id)

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

        self._restore_metadata()

    def _restore_metadata(self) -> None:
        storage = self.document_service.storage
        list_metadata = getattr(storage, "list_metadata", None)

        if not callable(list_metadata):
            return

        from config.settings import settings

        provider = (settings.STORAGE_PROVIDER or "oci").strip().lower()
        if provider != "b2":
            return

        raw_records = list_metadata("adaptation")
        records = [
            _adaptation_from_metadata(item)
            for item in raw_records
        ]
        self.repository.restore(records)

        logger.info(
            "Restored %s adaptation metadata records.",
            len(records),
        )

    def _persist_metadata(self, record: AdaptationRecord) -> None:
        from config.settings import settings

        provider = (settings.STORAGE_PROVIDER or "oci").strip().lower()
        if provider != "b2":
            return

        storage = self.document_service.storage
        save_metadata = getattr(storage, "save_metadata", None)

        if not callable(save_metadata):
            return

        save_metadata(
            "adaptation",
            record.id,
            _adaptation_to_metadata(record),
        )

    def _update_and_persist(
        self,
        adaptation_id: int,
        **changes: Any,
    ) -> AdaptationRecord | None:
        record = self.repository.update(adaptation_id, **changes)
        if record is not None:
            self._persist_metadata(record)
        return record

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

        record = self.repository.create(
            document_id=document.id,
            document_title=document.title,
            profile=profile,
            format=format,
            industry=industry,
            detail_level=detail_level,
            domain_request=domain_request,
        )

        try:
            self._persist_metadata(record)
        except Exception:
            self.repository.update(
                record.id,
                status="failed",
                error="Could not persist adaptation metadata.",
                completed_at=utc_now(),
            )
            raise

        return record

    def process(self, adaptation_id: int) -> None:
        try:
            record = self._update_and_persist(
                adaptation_id,
                status="processing",
                error=None,
            )
        except Exception:
            logger.exception(
                "Could not persist processing status for adaptation %s",
                adaptation_id,
            )
            return

        if record is None:
            return

        try:
            result = self.engine.adapt_content(record.domain_request)

            score = result.evaluacion_calidad.anclaje_fuente_score
            approved = score >= 0.8

            issues: list[str] = []
            if not approved:
                issues.append(
                    "El indicador de anclaje a la fuente no alcanzó "
                    "el umbral de aprobación del 80 %. Contrasta la "
                    "información importante con el documento original "
                    "antes de utilizarla."
                )

            from config.settings import settings

            provider = (
                settings.STORAGE_PROVIDER or "oci"
            ).strip().lower()

            json_object_id = None
            json_storage_status = None

            if provider == "b2":
                # Unique object keys avoid overwriting prior generations
                # if an ID is ever reused in another deployment.
                json_object_id = f"adaptation-{adaptation_id}.json"

                generated_json = {
                    "provider": "Backblaze B2",
                    "adaptation_id": adaptation_id,
                    "document_id": record.document_id,
                    "document_title": record.document_title,
                    "official_response": result.model_dump(mode="json"),
                    "content": result.contenido_adaptado.model_dump(
                        mode="json"
                    ),
                    "evaluation": {
                        "approved": approved,
                        "score": score,
                        "criteria": {
                            "source_grounding": score,
                        },
                        "issues": issues,
                    },
                }

                storage_result = (
                    self.document_service.storage.upload_educational_json(
                        json_object_id,
                        generated_json,
                    )
                )

                if (
                    storage_result.status_upload
                    != "completado (Backblaze B2)"
                ):
                    raise RuntimeError(
                        "The generated JSON was not confirmed in Backblaze B2."
                    )

                json_storage_status = storage_result.status_upload

            completed = self._update_and_persist(
                adaptation_id,
                status="completed",
                official_response=result.model_dump(mode="json"),
                content=result.contenido_adaptado.model_dump(mode="json"),
                evaluation={
                    "approved": approved,
                    "score": score,
                    "criteria": {
                        "source_grounding": score,
                    },
                    "issues": issues,
                },
                iteration=1,
                completed_at=utc_now(),
                json_storage_object_id=json_object_id,
                json_storage_status=json_storage_status,
            )

            if completed is None:
                raise RuntimeError(
                    "Adaptation record disappeared during processing."
                )

        except Exception as exc:
            logger.exception(
                "Error processing adaptation %s",
                adaptation_id,
            )

            try:
                self._update_and_persist(
                    adaptation_id,
                    status="failed",
                    error=str(exc) or "Adaptation processing failed.",
                    completed_at=utc_now(),
                )
            except Exception:
                logger.exception(
                    "Could not persist failure status for adaptation %s",
                    adaptation_id,
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
