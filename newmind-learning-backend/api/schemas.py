"""Transport DTOs for the versioned HTTP API."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ApiModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)


class ProfileValue(str, Enum):
    BEGINNER = "Principiante"
    JUNIOR = "Junior"
    SENIOR = "Senior"
    LEADER = "Lider"
    MANAGER = "Gestor"


class FormatValue(str, Enum):
    FLASHCARDS = "Flashcards"
    TUTORIAL = "Tutorial"
    QUIZ = "Quiz"
    EXECUTIVE_SUMMARY = "Resumen Ejecutivo"
    SCRIPT = "Guion"


class IndustryValue(str, Enum):
    FINTECH = "Fintech"
    HEALTH = "Salud"
    ECOMMERCE = "E-commerce"
    GENERAL = "General"


class DetailLevelValue(str, Enum):
    BASIC = "Basico"
    INTERMEDIATE = "Intermedio"
    DIDACTIC = "Didactico"
    DETAILED = "Detallado"


class AdaptationStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class HealthResponse(ApiModel):
    status: str
    service: str
    environment: str
    oci_mode: str
    oci_namespace: str
    chroma_persist_dir: str


class DocumentResponse(ApiModel):
    id: int
    title: str
    type: str
    size: int
    created_at: datetime = Field(serialization_alias="createdAt")


class AdaptationCreateRequest(ApiModel):
    document_id: int = Field(alias="documentId")
    profile: ProfileValue
    format: FormatValue
    industry: IndustryValue
    detail_level: DetailLevelValue = Field(alias="detailLevel")


class QualityEvaluationResponse(ApiModel):
    approved: bool
    score: float
    criteria: dict[str, float]
    issues: list[str]


class AdaptationResponse(ApiModel):
    id: int
    document_id: int = Field(serialization_alias="documentId")
    document_title: str = Field(serialization_alias="documentTitle")
    profile: ProfileValue
    format: FormatValue
    industry: IndustryValue
    detail_level: DetailLevelValue = Field(serialization_alias="detailLevel")
    status: AdaptationStatus
    content: dict[str, Any] | None = None
    evaluation: QualityEvaluationResponse | None = None
    iteration: int | None = None
    created_at: datetime = Field(serialization_alias="createdAt")
    completed_at: datetime | None = Field(default=None, serialization_alias="completedAt")
    error: str | None = None


class AdaptationStatusResponse(ApiModel):
    id: int
    status: AdaptationStatus
    completed_at: datetime | None = Field(default=None, serialization_alias="completedAt")
    error: str | None = None
