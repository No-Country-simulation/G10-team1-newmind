"""Backblaze B2 client using its S3-compatible API.

Selected only when STORAGE_PROVIDER=b2. Keeps credentials server-side and
reports local fallback explicitly instead of claiming cloud persistence.
"""
from __future__ import annotations

import json
import logging
from typing import Any, Dict

from config.settings import settings
from models.schemas import AlmacenamientoOCI
from storage.contracts import StorageResult, validate_object_id

logger = logging.getLogger(__name__)


def _configured() -> bool:
    return all((settings.B2_ENDPOINT_URL, settings.B2_REGION, settings.B2_KEY_ID, settings.B2_APPLICATION_KEY))


class BackblazeB2StorageClient:
    def __init__(self) -> None:
        self.client = None
        self.is_emulated = True
        self.error_code: str | None = None
        if _configured():
            try:
                import boto3
                from botocore.config import Config
                self.client = boto3.client(
                    "s3",
                    endpoint_url=settings.B2_ENDPOINT_URL,
                    region_name=settings.B2_REGION,
                    aws_access_key_id=settings.B2_KEY_ID,
                    aws_secret_access_key=settings.B2_APPLICATION_KEY,
                    config=Config(signature_version="s3v4"),
                )
                self.is_emulated = False
            except Exception as exc:
                # Do not log credentials or full exception payloads.
                logger.warning("No se pudo inicializar Backblaze B2 (%s); se usará almacenamiento local.", type(exc).__name__)
                self.error_code = "b2_client_init_failed"
        else:
            self.error_code = "b2_not_configured"

        if self.is_emulated:
            settings.LOCAL_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
            for bucket in (settings.B2_BUCKET_DOCS, settings.B2_BUCKET_OUTPUTS):
                (settings.LOCAL_STORAGE_DIR / bucket).mkdir(parents=True, exist_ok=True)

    def readiness(self) -> dict[str, Any]:
        return {
            "provider": "backblaze_b2",
            "mode": "local_emulation" if self.is_emulated else "b2",
            "real_storage_ready": not self.is_emulated,
            "local_fallback": self.is_emulated,
            "endpoint_configured": bool(settings.B2_ENDPOINT_URL),
            "region_configured": bool(settings.B2_REGION),
            "credentials_configured": bool(settings.B2_KEY_ID and settings.B2_APPLICATION_KEY),
            "buckets": [settings.B2_BUCKET_DOCS, settings.B2_BUCKET_OUTPUTS],
            "error_code": self.error_code,
        }

    def _upload(self, bucket: str, object_id: str, content: bytes, content_type: str) -> tuple[str, str | None]:
        if not self.is_emulated and self.client is not None:
            try:
                response = self.client.put_object(Bucket=bucket, Key=object_id, Body=content, ContentType=content_type)
                return "b2", response.get("ETag", "").strip('"') or None
            except Exception as exc:
                logger.warning("Escritura B2 fallida (%s); se utilizará fallback local.", type(exc).__name__)
                error_code = "b2_write_failed"
        else:
            error_code = self.error_code or "b2_not_configured"

        destination = settings.LOCAL_STORAGE_DIR / bucket / object_id
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
        self.error_code = error_code
        return "local_emulation", None

    def upload_raw_document(self, filename: str, content: bytes, content_type: str = "application/octet-stream") -> StorageResult:
        validate_object_id(filename)
        mode, etag = self._upload(settings.B2_BUCKET_DOCS, filename, content, content_type)
        return StorageResult(
            mode=mode, status="completed" if mode == "b2" else "local_fallback",
            bucket=settings.B2_BUCKET_DOCS, object_id=filename, etag=etag,
            error_code=None if mode == "b2" else self.error_code,
        )

    def upload_educational_json(self, object_id: str, data: Dict[str, Any]) -> AlmacenamientoOCI:
        validate_object_id(object_id)
        payload = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
        mode, _ = self._upload(settings.B2_BUCKET_OUTPUTS, object_id, payload, "application/json")
        status = "completado (Backblaze B2)" if mode == "b2" else "completado (local/emulado; B2 no confirmado)"
        return AlmacenamientoOCI(bucket=settings.B2_BUCKET_OUTPUTS, objeto_id=object_id, status_upload=status)


    def download_raw_document(self, object_id: str) -> bytes:
        """Recover the original document from the configured B2 bucket."""
        validate_object_id(object_id)

        if self.is_emulated or self.client is None:
            raise RuntimeError(
                "Backblaze B2 is not active; remote download is unavailable."
            )

        try:
            response = self.client.get_object(
                Bucket=settings.B2_BUCKET_DOCS,
                Key=object_id,
            )
            return response["Body"].read()
        except Exception as exc:
            logger.warning(
                "Falló la descarga del documento desde B2 (%s).",
                type(exc).__name__,
            )
            raise RuntimeError(
                "The original document could not be recovered from Backblaze B2."
            ) from exc

    def download_educational_json(self, object_id: str) -> bytes:
        """Recover the generated JSON bytes from the configured B2 bucket."""
        validate_object_id(object_id)

        if self.is_emulated or self.client is None:
            raise RuntimeError(
                "Backblaze B2 is not active; remote download is unavailable."
            )

        try:
            response = self.client.get_object(
                Bucket=settings.B2_BUCKET_OUTPUTS,
                Key=object_id,
            )
            return response["Body"].read()
        except Exception as exc:
            logger.warning(
                "Falló la descarga del JSON desde B2 (%s).",
                type(exc).__name__,
            )
            raise RuntimeError(
                "The generated JSON could not be recovered from Backblaze B2."
            ) from exc


    def save_metadata(
        self,
        kind: str,
        record_id: int,
        data: Dict[str, Any],
    ) -> str:
        """Persist one document or adaptation metadata record in B2."""
        if kind not in {"document", "adaptation"}:
            raise ValueError("Unsupported metadata type.")

        if record_id < 1:
            raise ValueError("Invalid metadata record ID.")

        bucket = (
            settings.B2_BUCKET_DOCS
            if kind == "document"
            else settings.B2_BUCKET_OUTPUTS
        )
        object_id = f"metadata-{kind}-{record_id:010d}.json"
        validate_object_id(object_id)

        payload = json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
        ).encode("utf-8")

        mode, _ = self._upload(
            bucket,
            object_id,
            payload,
            "application/json",
        )

        if mode != "b2":
            raise RuntimeError(
                "Metadata was not persisted to Backblaze B2."
            )

        return object_id

    def list_metadata(self, kind: str) -> list[Dict[str, Any]]:
        """Load persisted metadata records of one supported type."""
        if kind not in {"document", "adaptation"}:
            raise ValueError("Unsupported metadata type.")

        if self.is_emulated or self.client is None:
            raise RuntimeError(
                "Backblaze B2 is not active; metadata recovery is unavailable."
            )

        bucket = (
            settings.B2_BUCKET_DOCS
            if kind == "document"
            else settings.B2_BUCKET_OUTPUTS
        )
        prefix = f"metadata-{kind}-"
        records: list[Dict[str, Any]] = []

        try:
            paginator = self.client.get_paginator("list_objects_v2")

            for page in paginator.paginate(
                Bucket=bucket,
                Prefix=prefix,
            ):
                for item in page.get("Contents", []):
                    key = item["Key"]

                    if not key.endswith(".json"):
                        continue

                    response = self.client.get_object(
                        Bucket=bucket,
                        Key=key,
                    )

                    raw = response["Body"].read()
                    record = json.loads(raw.decode("utf-8"))

                    if isinstance(record, dict):
                        records.append(record)

            return records

        except Exception as exc:
            logger.warning(
                "Metadata recovery from B2 failed (%s).",
                type(exc).__name__,
            )
            raise RuntimeError(
                "Metadata could not be recovered from Backblaze B2."
            ) from exc

    def delete_metadata(self, kind: str, record_id: int) -> None:
        """Delete one persisted metadata record from B2."""
        if kind not in {"document", "adaptation"}:
            raise ValueError("Unsupported metadata type.")

        if self.is_emulated or self.client is None:
            raise RuntimeError(
                "Backblaze B2 is not active; metadata deletion is unavailable."
            )

        bucket = (
            settings.B2_BUCKET_DOCS
            if kind == "document"
            else settings.B2_BUCKET_OUTPUTS
        )
        object_id = f"metadata-{kind}-{record_id:010d}.json"
        validate_object_id(object_id)

        try:
            self.client.delete_object(
                Bucket=bucket,
                Key=object_id,
            )
        except Exception as exc:
            logger.warning(
                "Metadata deletion from B2 failed (%s).",
                type(exc).__name__,
            )
            raise RuntimeError(
                "Metadata could not be deleted from Backblaze B2."
            ) from exc


b2_storage = BackblazeB2StorageClient()
