"""Behavior tests for canonical document ingestion and chunking."""

from dataclasses import fields
from pathlib import Path
from types import SimpleNamespace

import pytest

from ingestion.chunker import doc_chunker
from ingestion.loaders import (
    CorruptPdfError,
    DocumentType,
    EmptyDocumentError,
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


def test_chunker_segmentation():
    sample_text = "Technical paragraph. " * 30 + "\n\n" + "More details. " * 30

    chunks = doc_chunker.split_text(sample_text, source_id="test_doc")

    assert len(chunks) >= 2
    assert "chunk_id" in chunks[0]
    assert "content" in chunks[0]


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
