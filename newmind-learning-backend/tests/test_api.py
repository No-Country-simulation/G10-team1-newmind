"""Contract tests for the versioned FastAPI boundary."""

import json
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from application.repositories import AdaptationRepository, DocumentRepository
from application.services import AdaptationService, DocumentService
from ingestion.chunker import DocumentChunker
from ingestion.loaders import (
    DocumentSource,
    DocumentType,
    ExtractionTrace,
    NormalizedDocument,
    doc_loader,
)
from main import create_app
from models.schemas import (
    AlmacenamientoOCI,
    ContenidoAdaptado,
    EvaluacionCalidad,
    MetadatosAprendizaje,
    RespuestaAdaptacion,
)


CONTRACT_FIXTURE_PATH = (
    Path(__file__).resolve().parents[1] / "contracts" / "openapi-v1-adaptation-response.fixture.json"
)
CONTRACT_SCHEMA_FIXTURE_PATH = (
    Path(__file__).resolve().parents[1] / "contracts" / "openapi-v1-adaptation-response.schema.json"
)
INGESTION_FIXTURES = Path(__file__).parent / "fixtures" / "ingestion"
OFFICIAL_RESPONSE_BLOCKS = {
    "status",
    "metadatos",
    "contenido_adaptado",
    "evaluacion_calidad",
    "almacenamiento_oci",
}
OFFICIAL_RESPONSE_SCHEMA_NAMES = {
    "RespuestaAdaptacion",
    "MetadatosAprendizaje",
    "ContenidoAdaptado",
    "EvaluacionCalidad",
    "AlmacenamientoOCI",
}
OPENAPI_CONTRACT_KEYS = {
    "$ref",
    "additionalProperties",
    "default",
    "enum",
    "items",
    "maximum",
    "minimum",
    "properties",
    "required",
    "type",
}


def normalize_openapi_contract_schema(value: Any) -> Any:
    if isinstance(value, dict):
        normalized = {}
        for key in sorted(value):
            if key not in OPENAPI_CONTRACT_KEYS:
                continue
            if key == "properties":
                normalized[key] = {
                    property_name: normalize_openapi_contract_schema(property_schema)
                    for property_name, property_schema in sorted(value[key].items())
                }
                continue
            normalized[key] = normalize_openapi_contract_schema(value[key])
        return normalized
    if isinstance(value, list):
        return [normalize_openapi_contract_schema(item) for item in value]
    return value


def adaptation_contract_schema_subset(schemas: dict[str, Any]) -> dict[str, Any]:
    return {
        name: normalize_openapi_contract_schema(schemas[name])
        for name in sorted(OFFICIAL_RESPONSE_SCHEMA_NAMES)
    }


class FakeLoader:
    def __init__(self) -> None:
        self.document: NormalizedDocument | None = None

    def extract_from_bytes(self, filename: str, content: bytes) -> NormalizedDocument:
        self.document = NormalizedDocument(
            text=content.decode("utf-8"),
            source=DocumentSource(filename=filename),
            type=DocumentType.TEXT,
            trace=ExtractionTrace(extractor="fake"),
        )
        return self.document


class FakeChunker:
    def __init__(self) -> None:
        self.document: NormalizedDocument | None = None

    def split_document(self, document: NormalizedDocument) -> list[dict[str, Any]]:
        self.document = document
        return [{"chunk_id": "stable-0", "content": document.text}]


class FakeVectorStore:
    def __init__(self) -> None:
        self.chunks: list[dict[str, Any]] = []

    def add_chunks(self, chunks: list[dict[str, Any]]) -> None:
        self.chunks.extend(chunks)


class FakeStorage:
    def upload_raw_document(self, filename: str, content: bytes, content_type: str) -> dict[str, str]:
        return {"status": "emulated_local", "object_id": filename}


class RecordingStorage:
    def __init__(self) -> None:
        self.uploads: list[dict[str, Any]] = []

    def upload_raw_document(self, filename: str, content: bytes, content_type: str) -> dict[str, str]:
        self.uploads.append(
            {"filename": filename, "content": content, "content_type": content_type}
        )
        return {"status": "emulated_local", "object_id": filename}


class FakeEngine:
    def __init__(self) -> None:
        self.last_request = None

    def adapt_content(self, request):
        self.last_request = request
        return RespuestaAdaptacion(
            status="exito",
            metadatos=MetadatosAprendizaje(
                perfil_aplicado=request.perfil_destinatario.value,
                formato_generado=request.formato_salida.value,
                tiempo_estimado_estudio_minutos=5,
                conceptos_clave=["API"],
            ),
            contenido_adaptado=ContenidoAdaptado(
                titulo="Adapted content",
                introduccion_contextualizada="An introduction",
                items=[{"concept": "API contract"}],
            ),
            evaluacion_calidad=EvaluacionCalidad(
                anclaje_fuente_score=0.9,
                claridad_pedagogica="High",
                observaciones="Grounded",
            ),
            almacenamiento_oci=AlmacenamientoOCI(
                bucket="outputs",
                objeto_id="result.json",
            ),
        )


@pytest.fixture
def api_context():
    engine = FakeEngine()
    documents = DocumentService(
        DocumentRepository(),
        loader=FakeLoader(),
        chunker=FakeChunker(),
        vector_store=FakeVectorStore(),
        storage=FakeStorage(),
    )
    adaptations = AdaptationService(documents, AdaptationRepository(), engine=engine)
    with TestClient(create_app(documents, adaptations)) as client:
        yield client, engine


@pytest.fixture
def real_ingestion_api_context():
    repository = DocumentRepository()
    vector_store = FakeVectorStore()
    storage = RecordingStorage()
    documents = DocumentService(
        repository,
        loader=doc_loader,
        chunker=DocumentChunker(chunk_size=64, chunk_overlap=8),
        vector_store=vector_store,
        storage=storage,
    )
    adaptations = AdaptationService(documents, AdaptationRepository(), engine=FakeEngine())
    with TestClient(create_app(documents, adaptations)) as client:
        yield client, repository, vector_store, storage


def upload_document(client: TestClient, filename: str = "source.txt") -> dict[str, Any]:
    response = client.post(
        "/api/v1/documents",
        files={"file": (filename, b"Technical source content", "text/plain")},
    )
    assert response.status_code == 201
    return response.json()


def adaptation_payload(
    document_id: int, *, output_format: str = "Resumen Ejecutivo"
) -> dict[str, Any]:
    return {
        "documentId": document_id,
        "profile": "Lider",
        "format": output_format,
        "industry": "Fintech",
        "detailLevel": "Detallado",
    }


def test_health_and_openapi_expose_required_contract(api_context):
    client, _ = api_context
    assert client.get("/health").json()["status"] == "ok"

    paths = client.get("/openapi.json").json()["paths"]
    assert {
        "/health",
        "/api/v1/documents",
        "/api/v1/documents/{document_id}",
        "/api/v1/adaptations",
        "/api/v1/adaptations/{adaptation_id}",
        "/api/v1/adaptations/{adaptation_id}/status",
    } <= paths.keys()
    assert client.get("/docs").status_code == 200

    schemas = client.get("/openapi.json").json()["components"]["schemas"]
    assert "RespuestaAdaptacion" in schemas
    assert schemas["RespuestaAdaptacion"]["required"] == [
        "status",
        "metadatos",
        "contenido_adaptado",
        "evaluacion_calidad",
        "almacenamiento_oci",
    ]
    assert set(schemas["RespuestaAdaptacion"]["properties"]) == OFFICIAL_RESPONSE_BLOCKS
    assert schemas["MetadatosAprendizaje"]["properties"]["tiempo_estimado_estudio_minutos"]["type"] == "integer"
    assert schemas["ContenidoAdaptado"]["properties"]["items"]["type"] == "array"
    assert schemas["EvaluacionCalidad"]["properties"]["anclaje_fuente_score"]["type"] == "number"
    assert schemas["AlmacenamientoOCI"]["properties"]["objeto_id"]["type"] == "string"

    cors_response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert cors_response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_canonical_contract_fixture_preserves_official_blocks():
    fixture = json.loads(CONTRACT_FIXTURE_PATH.read_text(encoding="utf-8"))

    assert set(fixture) == OFFICIAL_RESPONSE_BLOCKS
    validated = RespuestaAdaptacion.model_validate(fixture)

    assert validated.status == "exito"
    assert isinstance(validated.metadatos.tiempo_estimado_estudio_minutos, int)
    assert isinstance(validated.contenido_adaptado.items, list)
    assert isinstance(validated.evaluacion_calidad.anclaje_fuente_score, float)
    assert isinstance(validated.almacenamiento_oci.objeto_id, str)


def test_openapi_schema_matches_frozen_v1_adaptation_contract(api_context):
    client, _ = api_context
    schemas = client.get("/openapi.json").json()["components"]["schemas"]
    expected = json.loads(CONTRACT_SCHEMA_FIXTURE_PATH.read_text(encoding="utf-8"))

    assert adaptation_contract_schema_subset(schemas) == expected


def test_document_crud_and_filename_sanitization(api_context):
    client, _ = api_context
    document = upload_document(client, "../unsafe name.txt")
    assert document["title"] == "unsafe-name"
    assert document["type"] == "txt"
    assert "createdAt" in document
    assert client.get("/api/v1/documents").json() == [document]
    assert client.get(f"/api/v1/documents/{document['id']}").json() == document
    assert client.delete(f"/api/v1/documents/{document['id']}").status_code == 204
    assert client.get(f"/api/v1/documents/{document['id']}").status_code == 404


def test_document_service_passes_the_canonical_document_directly_and_preserves_content():
    loader = FakeLoader()
    chunker = FakeChunker()
    vector_store = FakeVectorStore()
    repository = DocumentRepository()
    service = DocumentService(
        repository,
        loader=loader,
        chunker=chunker,
        vector_store=vector_store,
        storage=FakeStorage(),
    )

    record = service.upload("guide.txt", b"Canonical content", "text/plain")

    assert chunker.document is loader.document
    assert record.content == loader.document.text
    assert repository.get(record.id).content == "Canonical content"
    assert vector_store.chunks == [{"chunk_id": "stable-0", "content": "Canonical content"}]


@pytest.mark.parametrize(
    ("filename", "content_type", "expected_type", "expected_text", "expected_page_count"),
    [
        ("sample.pdf", "application/pdf", "pdf", "Normalized PDF content.", 1),
        ("sample.md", "text/markdown", "md", "# Café\n\nNormalized Markdown fixture.", 0),
        ("sample.txt", "text/plain", "txt", "Plain text fixture.", 0),
    ],
)
def test_http_upload_uses_real_ingestion_chunking_and_vector_metadata(
    real_ingestion_api_context,
    filename,
    content_type,
    expected_type,
    expected_text,
    expected_page_count,
):
    client, repository, vector_store, storage = real_ingestion_api_context
    content = (INGESTION_FIXTURES / filename).read_bytes()

    response = client.post(
        "/api/v1/documents",
        files={"file": (filename, content, content_type)},
    )

    assert response.status_code == 201
    record = repository.get(response.json()["id"])
    assert record is not None
    assert record.content == expected_text
    assert record.type == expected_type
    assert len(vector_store.chunks) == 1
    chunk = vector_store.chunks[0]
    assert chunk["content"] == expected_text
    assert chunk["source_filename"] == filename
    assert chunk["document_type"] == expected_type
    if expected_type == "pdf":
        assert chunk["extractor"] in {"pypdf", "pymupdf"}
    else:
        assert chunk["extractor"] == "utf-8"
    assert chunk["page_count"] == expected_page_count
    assert chunk["chunk_index"] == 0
    assert chunk["chunk_count"] == 1
    assert chunk["chunk_length"] == len(expected_text)
    assert storage.uploads == [
        {
            "filename": f"{record.id}-{filename}",
            "content": content,
            "content_type": content_type,
        }
    ]


@pytest.mark.parametrize(
    ("filename", "content", "expected_detail"),
    [
        (
            "source.exe",
            b"content",
            "Unsupported document type. Allowed types: PDF, MD, TXT.",
        ),
        ("empty.txt", b"", "Document must not be empty."),
        ("whitespace.txt", b" \r\n\t", "Document must not be empty."),
        ("whitespace.md", b"\n\n  \t", "Document must not be empty."),
        ("invalid.txt", b"\xff", "Document must contain valid UTF-8 text."),
        (
            "corrupt.pdf",
            (INGESTION_FIXTURES / "corrupt.pdf").read_bytes(),
            "PDF document is corrupt.",
        ),
        (
            "blank.pdf",
            (INGESTION_FIXTURES / "blank.pdf").read_bytes(),
            "PDF document contains no extractable text.",
        ),
    ],
)
def test_http_upload_returns_stable_422_without_partial_state(
    real_ingestion_api_context,
    filename,
    content,
    expected_detail,
):
    client, repository, vector_store, storage = real_ingestion_api_context

    response = client.post(
        "/api/v1/documents",
        files={"file": (filename, content, "application/octet-stream")},
    )

    assert response.status_code == 422
    assert response.json() == {"detail": expected_detail}
    assert repository.list() == []
    assert vector_store.chunks == []
    assert storage.uploads == []


@pytest.mark.parametrize("filename", ["source.exe", "source.json", "source.markdown"])
def test_upload_rejects_unsupported_types(api_context, filename):
    client, _ = api_context
    response = client.post(
        "/api/v1/documents",
        files={"file": (filename, b"content", "application/octet-stream")},
    )
    assert response.status_code == 422
    assert response.json()["detail"] == "Unsupported document type. Allowed types: PDF, MD, TXT."


def test_upload_rejects_oversized_documents(api_context, monkeypatch):
    import api.documents as documents_api
    import application.services as services

    client, _ = api_context
    monkeypatch.setattr(documents_api, "MAX_DOCUMENT_SIZE", 5)
    monkeypatch.setattr(services, "MAX_DOCUMENT_SIZE", 5)
    response = client.post(
        "/api/v1/documents",
        files={"file": ("large.txt", b"123456", "text/plain")},
    )
    assert response.status_code == 413
    assert response.json()["detail"] == "Document exceeds the 20 MB size limit."


def test_adaptation_workflow_maps_transport_values_and_filters(api_context):
    client, engine = api_context
    document = upload_document(client)
    response = client.post("/api/v1/adaptations", json=adaptation_payload(document["id"]))
    assert response.status_code == 202
    created = response.json()
    assert created["status"] == "pending"
    assert created["documentId"] == document["id"]

    status_response = client.get(f"/api/v1/adaptations/{created['id']}/status")
    assert status_response.json()["status"] == "completed"
    completed = client.get(f"/api/v1/adaptations/{created['id']}").json()
    assert set(completed["officialResponse"]) == OFFICIAL_RESPONSE_BLOCKS
    assert completed["officialResponse"]["status"] == "exito"
    assert completed["officialResponse"]["metadatos"]["perfil_aplicado"] == "Líder Técnico / Arquitecto"
    assert completed["officialResponse"]["contenido_adaptado"]["titulo"] == "Adapted content"
    assert completed["officialResponse"]["evaluacion_calidad"]["anclaje_fuente_score"] == 0.9
    assert completed["officialResponse"]["almacenamiento_oci"]["objeto_id"] == "result.json"
    assert completed["content"]["titulo"] == "Adapted content"
    assert completed["evaluation"]["score"] == 0.9
    assert engine.last_request.perfil_destinatario.value == "Líder Técnico / Arquitecto"
    assert engine.last_request.formato_salida.value == "Resumen Ejecutivo (TL;DR)"
    assert engine.last_request.nivel_detalle.value == "Tecnico"

    filtered = client.get(
        "/api/v1/adaptations",
        params={"profile": "Lider", "format": "Resumen Ejecutivo", "status": "completed"},
    ).json()
    assert [item["id"] for item in filtered] == [created["id"]]
    assert client.get("/api/v1/adaptations", params={"profile": "Gestor"}).json() == []


def test_invalid_flashcards_response_is_not_persisted_as_completed(api_context):
    client, _ = api_context
    document = upload_document(client)

    response = client.post(
        "/api/v1/adaptations",
        json=adaptation_payload(document["id"], output_format="Flashcards"),
    )

    assert response.status_code == 202
    adaptation_id = response.json()["id"]
    assert client.get(f"/api/v1/adaptations/{adaptation_id}/status").json()["status"] == "failed"
    persisted = client.get(f"/api/v1/adaptations/{adaptation_id}").json()
    assert persisted["status"] == "failed"
    assert persisted["officialResponse"] is None
    assert persisted["content"] is None


def test_adaptation_for_missing_document_returns_404(api_context):
    client, _ = api_context
    response = client.post("/api/v1/adaptations", json=adaptation_payload(999))
    assert response.status_code == 404
    assert response.json()["detail"] == "Document not found."
