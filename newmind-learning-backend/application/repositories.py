"""Thread-safe in-memory repositories used by the MVP application layer."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from threading import RLock
from typing import Any

from models.schemas import SolicitudAdaptacion


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True, slots=True)
class DocumentRecord:
    id: int
    title: str
    filename: str
    type: str
    size: int
    content: str
    created_at: datetime
    storage_object_id: str


@dataclass(frozen=True, slots=True)
class AdaptationRecord:
    id: int
    document_id: int
    document_title: str
    profile: str
    format: str
    industry: str
    detail_level: str
    status: str
    domain_request: SolicitudAdaptacion
    created_at: datetime
    completed_at: datetime | None = None
    content: dict[str, Any] | None = None
    evaluation: dict[str, Any] | None = None
    official_response: dict[str, Any] | None = None
    iteration: int | None = None
    error: str | None = None


class DocumentRepository:
    def __init__(self) -> None:
        self._lock = RLock()
        self._records: dict[int, DocumentRecord] = {}
        self._next_id = 1

    def create(
        self,
        *,
        title: str,
        filename: str,
        document_type: str,
        size: int,
        content: str,
        storage_object_id: str,
    ) -> DocumentRecord:
        with self._lock:
            record = DocumentRecord(
                id=self._next_id,
                title=title,
                filename=filename,
                type=document_type,
                size=size,
                content=content,
                created_at=utc_now(),
                storage_object_id=storage_object_id,
            )
            self._records[record.id] = record
            self._next_id += 1
            return record

    def get(self, document_id: int) -> DocumentRecord | None:
        with self._lock:
            return self._records.get(document_id)

    def list(self) -> list[DocumentRecord]:
        with self._lock:
            return sorted(self._records.values(), key=lambda item: item.id, reverse=True)

    def delete(self, document_id: int) -> bool:
        with self._lock:
            return self._records.pop(document_id, None) is not None

    def update_storage_object_id(self, document_id: int, object_id: str) -> DocumentRecord:
        with self._lock:
            current = self._records[document_id]
            updated = replace(current, storage_object_id=object_id)
            self._records[document_id] = updated
            return updated


class AdaptationRepository:
    def __init__(self) -> None:
        self._lock = RLock()
        self._records: dict[int, AdaptationRecord] = {}
        self._next_id = 1

    def create(
        self,
        *,
        document_id: int,
        document_title: str,
        profile: str,
        format: str,
        industry: str,
        detail_level: str,
        domain_request: SolicitudAdaptacion,
    ) -> AdaptationRecord:
        with self._lock:
            record = AdaptationRecord(
                id=self._next_id,
                document_id=document_id,
                document_title=document_title,
                profile=profile,
                format=format,
                industry=industry,
                detail_level=detail_level,
                status="pending",
                domain_request=domain_request,
                created_at=utc_now(),
            )
            self._records[record.id] = record
            self._next_id += 1
            return record

    def get(self, adaptation_id: int) -> AdaptationRecord | None:
        with self._lock:
            return self._records.get(adaptation_id)

    def list(self) -> list[AdaptationRecord]:
        with self._lock:
            return sorted(self._records.values(), key=lambda item: item.id, reverse=True)

    def update(self, adaptation_id: int, **changes: Any) -> AdaptationRecord | None:
        with self._lock:
            current = self._records.get(adaptation_id)
            if current is None:
                return None
            updated = replace(current, **changes)
            self._records[adaptation_id] = updated
            return updated
