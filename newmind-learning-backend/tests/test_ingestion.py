"""Behavior tests for canonical document ingestion and chunking."""

from dataclasses import fields
from pathlib import Path
from types import SimpleNamespace

import pytest

from ingestion.chunker import DocumentChunker
from ingestion.loaders import (
    CorruptPdfError,
    DocumentSource,
    DocumentType,
    EmptyDocumentError,
    ExtractionTrace,
    InvalidTextEncodingError,
    NormalizedDocument,
    PdfNoExtractableTextError,
    SUPPORTED_FORMATS,
    UnsupportedDocumentTypeError,
    doc_loader,
)


FIXTURES = Path(__file__).parent / "fixtures" / "ingestion"


def test_supported_format_policy_is_exact_and_authoritative():
    assert tuple(SUPPORTED_FORMATS) == (".pdf", ".md", ".txt")


def normalized_document(
    text: str = "Technical source content",
    *,
    filename: str = "guide.md",
    document_type: DocumentType = DocumentType.MARKDOWN,
    extractor: str = "utf-8",
    page_count: int | None = None,
) -> NormalizedDocument:
    return NormalizedDocument(
        text=text,
        source=DocumentSource(filename=filename),
        type=document_type,
        trace=ExtractionTrace(extractor=extractor, page_count=page_count),
    )


def test_chunker_emits_deterministic_chunks_with_flat_rag_metadata():
    document = normalized_document(
        "Technical paragraph. " * 8,
        filename="guide.pdf",
        document_type=DocumentType.PDF,
        extractor="pypdf",
        page_count=3,
    )
    chunker = DocumentChunker(chunk_size=48, chunk_overlap=8)

    first = chunker.split_document(document)
    second = chunker.split_document(document)

    assert first == second
    assert len(first) >= 2
    assert len({chunk["chunk_id"] for chunk in first}) == len(first)
    assert all(
        set(chunk) == {
            "chunk_id",
            "content",
            "source_filename",
            "document_type",
            "extractor",
            "page_count",
            "chunk_index",
            "chunk_count",
            "chunk_length",
        }
        for chunk in first
    )
    assert all(chunk["source_filename"] == "guide.pdf" for chunk in first)
    assert all(chunk["document_type"] == "pdf" for chunk in first)
    assert all(chunk["extractor"] == "pypdf" for chunk in first)
    assert all(chunk["page_count"] == 3 for chunk in first)
    assert [chunk["chunk_index"] for chunk in first] == list(range(len(first)))
    assert all(chunk["chunk_count"] == len(first) for chunk in first)
    assert all(chunk["chunk_length"] == len(chunk["content"]) for chunk in first)


def test_chunker_enforces_chunk_size_and_overlap():
    chunker = DocumentChunker(chunk_size=10, chunk_overlap=3)

    chunks = chunker.split_document(normalized_document("abcdefghijklmnopqrstuvwxyz"))

    assert [chunk["content"] for chunk in chunks] == [
        "abcdefghij",
        "hijklmnopq",
        "opqrstuvwx",
        "vwxyz",
    ]
    assert all(chunk["chunk_length"] <= 10 for chunk in chunks)
    assert all(
        previous["content"][-3:] == current["content"][:3]
        for previous, current in zip(chunks, chunks[1:])
    )


@pytest.mark.parametrize(
    ("chunk_size", "chunk_overlap"),
    [(0, 0), (-1, 0), (10, -1), (10, 10), (10, 11)],
)
def test_chunker_rejects_invalid_size_and_overlap(chunk_size: int, chunk_overlap: int):
    with pytest.raises(ValueError) as error:
        DocumentChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    assert str(error.value) == (
        "chunk_size must be positive and chunk_overlap must be between 0 and chunk_size - 1"
    )


def test_vector_store_receives_the_flat_chunk_metadata(monkeypatch, tmp_path):
    from config.settings import settings

    monkeypatch.setattr(settings, "CHROMA_PERSIST_DIR", str(tmp_path / "chroma"))
    from rag.vector_store import VectorStoreManager

    class RecordingCollection:
        def upsert(self, **payload):
            self.payload = payload

    chunk = DocumentChunker(chunk_size=100, chunk_overlap=10).split_document(
        normalized_document()
    )[0]
    manager = object.__new__(VectorStoreManager)
    manager.collection = RecordingCollection()

    manager.add_chunks([chunk])

    assert manager.collection.payload == {
        "documents": ["Technical source content"],
        "metadatas": [
            {
                "source_filename": "guide.md",
                "document_type": "md",
                "extractor": "utf-8",
                "page_count": 0,
                "chunk_index": 0,
                "chunk_count": 1,
                "chunk_length": 24,
            }
        ],
        "ids": [chunk["chunk_id"]],
    }


@pytest.mark.parametrize(
    ("filename", "document_type", "expected_text"),
    [
        ("sample.md", DocumentType.MARKDOWN, "# Café\n\nNormalized Markdown fixture."),
        ("sample.txt", DocumentType.TEXT, "Plain text fixture."),
        ("sample.pdf", DocumentType.PDF, "Normalized PDF content."),
    ],
)
def test_supported_fixtures_return_one_canonical_result_type(
    filename: str,
    document_type: DocumentType,
    expected_text: str,
):
    result = doc_loader.extract_from_file(FIXTURES / filename)

    assert isinstance(result, NormalizedDocument)
    assert [field.name for field in fields(result)] == ["text", "source", "type", "trace"]
    assert result.text == expected_text
    assert result.source.filename == filename
    assert result.type is document_type
    assert result.trace.extractor
    assert result.trace.page_count == (1 if document_type is DocumentType.PDF else None)


@pytest.mark.parametrize("filename", ["sample.md", "sample.txt", "sample.pdf"])
def test_repeated_fixture_extraction_is_deterministic(filename: str):
    path = FIXTURES / filename

    assert doc_loader.extract_from_file(path) == doc_loader.extract_from_file(path)


def test_text_normalization_is_deterministic_and_keeps_trace_out_of_text():
    result = doc_loader.extract_from_bytes(
        "notes.txt",
        "  Cafe\u0301  \r\n\r\n\r\nSecond line\t \r\n".encode(),
    )

    assert result.text == "Café\n\nSecond line"
    assert "utf-8" not in result.text
    assert result.trace.extractor == "utf-8"


@pytest.mark.parametrize(
    ("filename", "content", "error_type", "message"),
    [
        ("notes.rst", b"content", UnsupportedDocumentTypeError, "Unsupported document type: .rst"),
        ("empty.md", b"", EmptyDocumentError, "Document is empty: empty.md"),
        (
            "invalid.txt",
            b"\xff",
            InvalidTextEncodingError,
            "Document is not valid UTF-8: invalid.txt",
        ),
    ],
)
def test_text_inputs_raise_typed_stable_errors(filename, content, error_type, message):
    with pytest.raises(error_type) as error:
        doc_loader.extract_from_bytes(filename, content)

    assert str(error.value) == message


def test_corrupt_pdf_raises_typed_stable_error():
    with pytest.raises(CorruptPdfError) as error:
        doc_loader.extract_from_file(FIXTURES / "corrupt.pdf")

    assert str(error.value) == "Corrupt PDF: corrupt.pdf"


def test_pdf_without_extractable_text_raises_typed_stable_error():
    with pytest.raises(PdfNoExtractableTextError) as error:
        doc_loader.extract_from_file(FIXTURES / "blank.pdf")

    assert str(error.value) == "PDF contains no extractable text: blank.pdf"


def test_pdf_fallback_discards_partial_primary_extraction(monkeypatch):
    class FailingPages:
        def __iter__(self):
            yield SimpleNamespace(extract_text=lambda: "partial primary text")
            raise RuntimeError("primary parser failed")

    class FallbackDocument(list):
        page_count = 1

    fallback_document = FallbackDocument([SimpleNamespace(get_text=lambda: "fallback text")])

    monkeypatch.setitem(
        __import__("sys").modules,
        "pypdf",
        SimpleNamespace(PdfReader=lambda _stream: SimpleNamespace(pages=FailingPages())),
    )
    monkeypatch.setitem(
        __import__("sys").modules,
        "fitz",
        SimpleNamespace(open=lambda **_kwargs: fallback_document),
    )

    result = doc_loader.extract_from_bytes("fallback.pdf", b"%PDF-fallback-test")

    assert result.text == "fallback text"
    assert "partial primary text" not in result.text
    assert result.trace.extractor == "pymupdf"
