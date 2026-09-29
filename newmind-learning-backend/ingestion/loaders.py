"""Canonical, deterministic document ingestion for supported source formats."""

from __future__ import annotations

import io
import unicodedata
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from types import MappingProxyType


class DocumentType(str, Enum):
    PDF = "pdf"
    MARKDOWN = "md"
    TEXT = "txt"


SUPPORTED_FORMATS = MappingProxyType(
    {
        ".pdf": DocumentType.PDF,
        ".md": DocumentType.MARKDOWN,
        ".txt": DocumentType.TEXT,
    }
)


@dataclass(frozen=True)
class DocumentSource:
    filename: str


@dataclass(frozen=True)
class ExtractionTrace:
    extractor: str
    page_count: int | None = None


@dataclass(frozen=True)
class NormalizedDocument:
    text: str
    source: DocumentSource
    type: DocumentType
    trace: ExtractionTrace


class DocumentExtractionError(ValueError):
    """Base error for rejected or unextractable document content."""


class UnsupportedDocumentTypeError(DocumentExtractionError):
    pass


class EmptyDocumentError(DocumentExtractionError):
    pass


class InvalidTextEncodingError(DocumentExtractionError):
    pass


class CorruptPdfError(DocumentExtractionError):
    pass


class PdfNoExtractableTextError(DocumentExtractionError):
    pass


def normalize_text(text: str) -> str:
    """Produce stable Unicode and whitespace without embedding trace markers."""
    normalized = unicodedata.normalize("NFC", text).removeprefix("\ufeff")
    normalized = normalized.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip() for line in normalized.split("\n")]
    compacted: list[str] = []
    previous_was_blank = False
    for line in lines:
        is_blank = not line
        if not (is_blank and previous_was_blank):
            compacted.append(line)
        previous_was_blank = is_blank
    return "\n".join(compacted).strip()


def _normalized_pages(page_texts: list[str]) -> str:
    return normalize_text("\n\n".join(page_texts))


class DocumentLoader:
    @staticmethod
    def extract_from_bytes(filename: str, content: bytes) -> NormalizedDocument:
        source = DocumentSource(filename=Path(filename).name)
        extension = Path(source.filename).suffix.lower()
        document_type = SUPPORTED_FORMATS.get(extension)
        if document_type is None:
            display_extension = extension or "<none>"
            raise UnsupportedDocumentTypeError(f"Unsupported document type: {display_extension}")
        if not content:
            raise EmptyDocumentError(f"Document is empty: {source.filename}")

        if document_type is DocumentType.PDF:
            text, trace = DocumentLoader._extract_from_pdf_bytes(source.filename, content)
        else:
            try:
                decoded = content.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise InvalidTextEncodingError(
                    f"Document is not valid UTF-8: {source.filename}"
                ) from exc
            text = normalize_text(decoded)
            trace = ExtractionTrace(extractor="utf-8")

        if not text:
            raise EmptyDocumentError(f"Document is empty: {source.filename}")
        return NormalizedDocument(text=text, source=source, type=document_type, trace=trace)

    @staticmethod
    def extract_from_file(file_path: str | Path) -> NormalizedDocument:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File does not exist: {file_path}")
        return DocumentLoader.extract_from_bytes(path.name, path.read_bytes())

    @staticmethod
    def _extract_from_pdf_bytes(filename: str, content: bytes) -> tuple[str, ExtractionTrace]:
        parsed_pdf = False
        try:
            page_texts, page_count = DocumentLoader._extract_with_pypdf(content)
            parsed_pdf = True
            text = _normalized_pages(page_texts)
            if text:
                return text, ExtractionTrace(extractor="pypdf", page_count=page_count)
        except Exception:
            pass

        try:
            page_texts, page_count = DocumentLoader._extract_with_pymupdf(content)
            parsed_pdf = True
            text = _normalized_pages(page_texts)
            if text:
                return text, ExtractionTrace(extractor="pymupdf", page_count=page_count)
        except Exception as exc:
            if not parsed_pdf:
                raise CorruptPdfError(f"Corrupt PDF: {filename}") from exc

        raise PdfNoExtractableTextError(f"PDF contains no extractable text: {filename}")

    @staticmethod
    def _extract_with_pypdf(content: bytes) -> tuple[list[str], int]:
        import pypdf

        reader = pypdf.PdfReader(io.BytesIO(content))
        page_texts: list[str] = []
        page_count = 0
        for page in reader.pages:
            page_count += 1
            page_text = page.extract_text()
            if page_text:
                page_texts.append(page_text)
        return page_texts, page_count

    @staticmethod
    def _extract_with_pymupdf(content: bytes) -> tuple[list[str], int]:
        import fitz

        document = fitz.open(stream=content, filetype="pdf")
        try:
            page_texts = [page.get_text() for page in document]
            return page_texts, document.page_count
        finally:
            close = getattr(document, "close", None)
            if close is not None:
                close()


doc_loader = DocumentLoader()
