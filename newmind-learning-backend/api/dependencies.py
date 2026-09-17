"""FastAPI dependencies for application services."""

from fastapi import Request

from application.services import AdaptationService, DocumentService


def get_document_service(request: Request) -> DocumentService:
    return request.app.state.document_service


def get_adaptation_service(request: Request) -> AdaptationService:
    return request.app.state.adaptation_service
