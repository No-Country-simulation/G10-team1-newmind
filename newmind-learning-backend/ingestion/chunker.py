"""Deterministic chunking of canonical normalized documents."""

from __future__ import annotations

from hashlib import sha256
from typing import Any

from config.settings import settings
from ingestion.loaders import NormalizedDocument


RAG_METADATA_FIELDS = (
    "source_filename",
    "document_type",
    "extractor",
    "page_count",
    "chunk_index",
    "chunk_count",
    "chunk_length",
)


class DocumentChunker:
    def __init__(self, chunk_size: int | None = None, chunk_overlap: int | None = None):
        self.chunk_size = settings.DEFAULT_CHUNK_SIZE if chunk_size is None else chunk_size
        self.chunk_overlap = (
            settings.DEFAULT_CHUNK_OVERLAP if chunk_overlap is None else chunk_overlap
        )
        if self.chunk_size <= 0 or not 0 <= self.chunk_overlap < self.chunk_size:
            raise ValueError(
                "chunk_size must be positive and chunk_overlap must be between 0 and chunk_size - 1"
            )

    def split_document(self, document: NormalizedDocument) -> list[dict[str, Any]]:
        """Split one normalized document into bounded, overlapping RAG chunks."""
        if not document.text:
            return []

        step = self.chunk_size - self.chunk_overlap
        contents = [
            document.text[start : start + self.chunk_size]
            for start in range(0, len(document.text), step)
        ]
        document_digest = self._document_digest(document)
        chunk_count = len(contents)

        return [
            {
                "chunk_id": f"{document_digest}-chunk-{index:04d}",
                "content": content,
                "source_filename": document.source.filename,
                "document_type": document.type.value,
                "extractor": document.trace.extractor,
                "page_count": document.trace.page_count or 0,
                "chunk_index": index,
                "chunk_count": chunk_count,
                "chunk_length": len(content),
            }
            for index, content in enumerate(contents)
        ]

    @staticmethod
    def _document_digest(document: NormalizedDocument) -> str:
        canonical_identity = "\0".join(
            (
                document.source.filename,
                document.type.value,
                document.trace.extractor,
                str(document.trace.page_count or 0),
                document.text,
            )
        )
        return sha256(canonical_identity.encode("utf-8")).hexdigest()[:16]


doc_chunker = DocumentChunker()
