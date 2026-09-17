"""Contract tests for the versioned FastAPI boundary."""

from typing import Any

import pytest
from fastapi.testclient import TestClient

from application.repositories import AdaptationRepository, DocumentRepository
from application.services import AdaptationService, DocumentService
from main import create_app
from models.schemas import (
    AlmacenamientoOCI,
    ContenidoAdaptado,
    EvaluacionCalidad,
    MetadatosAprendizaje,
    RespuestaAdaptacion,
)


class FakeLoader:
    def extract_from_bytes(self, filename: str, content: bytes) -> str:
        return content.decode("utf-8")


class FakeChunker:
    def split_text(self, text: str, source_id: str) -> list[dict[str, Any]]:
        return [{"chunk_id": f"{source_id}-0", "content": text, "source": source_id}]


class FakeVectorStore:
    def __init__(self) -> None:
        self.chunks: list[dict[str, Any]] = []

    def add_chunks(self, chunks: list[dict[str, Any]]) -> None:
        self.chunks.extend(chunks)


class FakeStorage:
    def upload_raw_document(self, filename: str, content: bytes, content_type: str) -> dict[str, str]:
        return {"status": "emulated_local", "object_id": filename}


class FakeEngine:
    def __init__(self) -> None:
        self.last_request = None

    def adapt_content(self, request):
        self.last_request = request
        return RespuestaAdaptacion(
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


def upload_document(client: TestClient, filename: str = "source.txt") -> dict[str, Any]:
    response = client.post(
        "/api/v1/documents",
        files={"file": (filename, b"Technical source content", "text/plain")},
    )
    assert response.status_code == 201
    return response.json()


def adaptation_payload(document_id: int) -> dict[str, Any]:
    return {
        "documentId": document_id,
        "profile": "Lider",
        "format": "Resumen Ejecutivo",
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

    cors_response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert cors_response.headers["access-control-allow-origin"] == "http://localhost:5173"


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


def test_adaptation_for_missing_document_returns_404(api_context):
    client, _ = api_context
    response = client.post("/api/v1/adaptations", json=adaptation_payload(999))
    assert response.status_code == 404
    assert response.json()["detail"] == "Document not found."
