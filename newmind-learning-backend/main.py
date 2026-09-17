"""FastAPI entrypoint for the NewMind backend."""

from __future__ import annotations

import logging
import os
from typing import Any

import uvicorn
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.adaptations import router as adaptations_router
from api.documents import router as documents_router
from api.schemas import HealthResponse
from application.services import AdaptationService, DocumentService
from config.settings import settings
from storage.oci_client import oci_storage


logger = logging.getLogger(__name__)


def build_health_payload() -> dict[str, Any]:
    """Return runtime health metadata for container checks."""
    return {
        "status": "ok",
        "service": "newmind-learning-backend",
        "environment": settings.APP_ENV,
        "oci_mode": "emulated" if oci_storage.is_emulated else "oci",
        "oci_namespace": oci_storage.namespace,
        "chroma_persist_dir": settings.CHROMA_PERSIST_DIR,
    }


def create_app(
    document_service: DocumentService | None = None,
    adaptation_service: AdaptationService | None = None,
) -> FastAPI:
    document_service = document_service or DocumentService(storage=oci_storage)
    adaptation_service = adaptation_service or AdaptationService(document_service)

    application = FastAPI(
        title="NewMind Learning API",
        version="1.0.0",
        description="Contract-first API for document ingestion and educational adaptations.",
    )
    application.state.document_service = document_service
    application.state.adaptation_service = adaptation_service
    origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]
    application.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    root_router = APIRouter()

    @root_router.get("/", response_model=HealthResponse, include_in_schema=False)
    @root_router.get("/health", response_model=HealthResponse, tags=["health"])
    def health() -> dict[str, Any]:
        return build_health_payload()

    application.include_router(root_router)
    application.include_router(documents_router, prefix="/api/v1")
    application.include_router(adaptations_router, prefix="/api/v1")
    return application


app = create_app()


def run() -> None:
    """Start the backend on the Docker-compatible host and port."""
    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    uvicorn.run(
        app,
        host=os.getenv("BACKEND_HOST", "0.0.0.0"),
        port=int(os.getenv("BACKEND_PORT", "8000")),
    )


if __name__ == "__main__":
    run()
