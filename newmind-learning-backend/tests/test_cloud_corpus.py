"""Corpus cloud autorizado mediante extracción canónica y la ruta HTTP pública.

Solo se simulan el índice vectorial y el almacenamiento de originales; no se
importan instancias globales de main/OCI/Chroma. La procedencia se vincula a los
bytes originales del corpus, sin ampliar el contrato de la API.
"""

import json
from copy import deepcopy
from dataclasses import fields
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.documents import router
from application.repositories import DocumentRepository
from application.services import DocumentService
from ingestion.chunker import DocumentChunker
from ingestion.loaders import NormalizedDocument, doc_loader
from storage.contracts import StorageResult


CORPUS = Path(__file__).resolve().parents[1] / "data" / "samples" / "cloud_corpus"
DOCUMENTS = [
    "cloud-networking.md",
    "cloud-operations.txt",
    "cloud-retention-table.pdf",
    "cloud-network-columns.pdf",
]


@pytest.fixture
def manifest():
    return json.loads((CORPUS / "manifest.json").read_text(encoding="utf-8"))


@pytest.fixture
def ingestion_http(monkeypatch):
    from config.settings import settings
    monkeypatch.setattr(settings, "STORAGE_PROVIDER", "local")

    repository = DocumentRepository()
    chunks, uploads = [], []

    def store(filename, content, content_type):
        uploads.append((filename, content, content_type))
        return StorageResult("local_emulation", "completed", "test-documents", filename)

    service = DocumentService(
        repository,
        loader=doc_loader,
        chunker=DocumentChunker(chunk_size=256, chunk_overlap=0),
        vector_store=SimpleNamespace(add_chunks=chunks.extend),
        storage=SimpleNamespace(upload_raw_document=store),
    )
    app = FastAPI()
    app.state.document_service = service
    app.include_router(router, prefix="/api/v1")
    with TestClient(app) as client:
        yield SimpleNamespace(
            client=client, repository=repository, chunks=chunks, uploads=uploads,
        )


def test_corpus_manifest_records_origin_and_authorization(manifest):
    assert manifest["schema_version"] == 1
    assert set(manifest["documents"]) == set(DOCUMENTS)
    corpus_files = {
        path.name for path in CORPUS.iterdir()
        if path.suffix in {".pdf", ".md", ".txt"}
        and path.name not in {"AUTHORIZATION.md", "README.md"}
    }
    assert corpus_files == set(manifest["documents"])
    formats = {entry["type"] for entry in manifest["documents"].values()}
    assert formats == {"pdf", "md", "txt"}
    authorization = (CORPUS / "AUTHORIZATION.md").read_text(encoding="utf-8")
    for filename, entry in manifest["documents"].items():
        assert entry["origin"]["kind"] == "original_synthetic"
        assert entry["origin"]["creator"]
        assert entry["origin"]["source"] == filename
        assert entry["authorization"]["declaration"] == "AUTHORIZATION.md"
        assert entry["authorization"]["scope"] == "project_ingestion_tests_and_evaluations"
        assert filename in authorization
        assert sha256((CORPUS / filename).read_bytes()).hexdigest() == entry["sha256"]
        assert entry["expected_text"]


@pytest.mark.parametrize("filename", DOCUMENTS)
def test_cloud_corpus_uses_public_ingestion(filename, manifest, ingestion_http):
    entry = manifest["documents"][filename]
    content = (CORPUS / filename).read_bytes()
    normalized = doc_loader.extract_from_bytes(filename, content)
    assert isinstance(normalized, NormalizedDocument)
    assert [field.name for field in fields(normalized)] == [
        "text", "source", "type", "trace",
    ]
    assert normalized.text == entry["expected_text"]
    assert normalized.source.filename == filename
    assert normalized.type.value == entry["type"]
    assert normalized.trace.page_count == entry["page_count"]
    assert normalized.trace.extractor in entry["extractors"]
    assert doc_loader.extract_from_file(CORPUS / filename) == normalized

    flow = ingestion_http
    response = flow.client.post(
        "/api/v1/documents", files={"file": (filename, content, entry["content_type"])},
    )
    assert response.status_code == 201
    payload = response.json()
    record = flow.repository.get(payload["id"])
    assert record.content == entry["expected_text"]
    assert payload["filename"] == normalized.source.filename
    assert payload["type"] == entry["type"]
    assert payload["size"] == len(content)
    assert flow.client.get(f"/api/v1/documents/{record.id}").json() == payload
    assert flow.client.get("/api/v1/documents").json() == [payload]
    assert flow.chunks
    for chunk in flow.chunks:
        assert chunk["source_filename"] == filename
        assert chunk["document_type"] == entry["type"]
        assert chunk["extractor"] == normalized.trace.extractor
        assert chunk["page_count"] == (entry["page_count"] or 0)
        assert chunk["document_id"] == record.rag_document_id
        assert chunk["content"] in normalized.text
    joined_chunks = "".join(chunk["content"] for chunk in flow.chunks)
    assert "".join(joined_chunks.split()) == "".join(normalized.text.split())
    assert flow.uploads == [(record.storage_object_id, content, entry["content_type"])]
    assert sha256(flow.uploads[0][1]).hexdigest() == entry["sha256"]


def test_cloud_pdf_table_preserves_header_row_value_relationships(manifest):
    entry = manifest["documents"]["cloud-retention-table.pdf"]
    lines = doc_loader.extract_from_file(CORPUS / entry["origin"]["source"]).text.splitlines()
    layout = entry["layout"]
    assert lines == layout["reading_order"]
    assert lines[1] == " ".join(layout["headers"])
    assert len(lines[2:]) == len(layout["rows"])
    for extracted, row in zip(lines[2:], layout["rows"], strict=True):
        assert extracted == " ".join(row[header] for header in layout["headers"])


def test_cloud_pdf_columns_preserve_section_order_and_associations(manifest):
    entry = manifest["documents"]["cloud-network-columns.pdf"]
    lines = doc_loader.extract_from_file(CORPUS / entry["origin"]["source"]).text.splitlines()
    assert lines == entry["layout"]["reading_order"]
    left, right = entry["layout"]["columns"]
    assert lines[1:1 + len(left)] == left
    assert lines[1 + len(left):] == right


@pytest.mark.parametrize("filename", ["cloud-networking.md", "cloud-operations.txt"])
def test_cloud_text_normalization_remains_deterministic(filename, manifest, ingestion_http):
    content = (CORPUS / filename).read_bytes()
    text = content.decode("utf-8-sig")
    variant = ("\ufeff" + text.replace("\n", "\r\n") + "\r\n\r\n").encode("utf-8")
    expected = manifest["documents"][filename]
    assert doc_loader.extract_from_bytes(filename, content) == (
        doc_loader.extract_from_bytes(filename, variant)
    )
    for raw in (content, variant):
        response = ingestion_http.client.post(
            "/api/v1/documents",
            files={"file": (filename, raw, expected["content_type"])},
        )
        assert response.status_code == 201
        record = ingestion_http.repository.get(response.json()["id"])
        assert record.content == expected["expected_text"]


@pytest.mark.parametrize(
    "filename,content,detail",
    [
        ("empty.txt", b"", "Document must not be empty."),
        ("empty.md", b"", "Document must not be empty."),
        ("empty.pdf", b"", "Document must not be empty."),
        ("blank.txt", b" \r\n\t", "Document must not be empty."),
        ("blank.md", b"\xef\xbb\xbf\r\n ", "Document must not be empty."),
        ("corrupt.pdf", b"No es un documento PDF", "PDF document is corrupt."),
        (
            "textless.pdf",
            (Path(__file__).parent / "fixtures" / "ingestion" / "blank.pdf").read_bytes(),
            "PDF document contains no extractable text.",
        ),
        ("invalid.txt", b"\xff", "Document must contain valid UTF-8 text."),
        ("invalid.md", b"\xff", "Document must contain valid UTF-8 text."),
        (
            "utf16.txt", "Almacenamiento cloud".encode("utf-16"),
            "Document must contain valid UTF-8 text.",
        ),
    ],
    ids=[
        "txt-vacio", "md-vacio", "pdf-vacio", "txt-en-blanco", "md-solo-bom",
        "pdf-corrupto", "pdf-sin-texto", "txt-utf8-invalido", "md-utf8-invalido", "txt-utf16",
    ],
)
def test_rejected_cloud_inputs_preserve_prior_public_ingestion(
    filename, content, detail, ingestion_http,
):
    flow = ingestion_http
    seed = "cloud-networking.md"
    created = flow.client.post(
        "/api/v1/documents",
        files={"file": (seed, (CORPUS / seed).read_bytes(), "text/markdown")},
    )
    assert created.status_code == 201
    before = deepcopy((flow.repository.list(), flow.chunks, flow.uploads))
    public_before = flow.client.get("/api/v1/documents").json()
    response = flow.client.post(
        "/api/v1/documents", files={"file": (filename, content, "application/octet-stream")},
    )
    assert response.status_code == 422
    assert response.json() == {"detail": detail}
    assert (flow.repository.list(), flow.chunks, flow.uploads) == before
    assert flow.client.get("/api/v1/documents").json() == public_before
    document_id = created.json()["id"]
    assert flow.client.get(f"/api/v1/documents/{document_id}").json() == created.json()
