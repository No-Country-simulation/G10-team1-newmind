"""Explicit local-only object storage provider for development/tests."""
import json
from typing import Any, Dict
from config.settings import settings
from models.schemas import AlmacenamientoOCI
from storage.contracts import StorageResult, validate_object_id

class LocalStorageClient:
    is_emulated = True
    def readiness(self) -> dict[str, Any]:
        return {"provider": "local", "mode": "local_emulation", "real_storage_ready": False, "local_fallback": True, "buckets": [settings.OCI_BUCKET_DOCS, settings.OCI_BUCKET_OUTPUTS]}
    def _write(self, bucket: str, key: str, body: bytes) -> None:
        target = settings.LOCAL_STORAGE_DIR / bucket / key
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(body)
    def upload_raw_document(self, filename: str, content: bytes, content_type: str = "application/octet-stream") -> StorageResult:
        validate_object_id(filename); self._write(settings.OCI_BUCKET_DOCS, filename, content)
        return StorageResult(mode="local_emulation", status="local_fallback", bucket=settings.OCI_BUCKET_DOCS, object_id=filename)
    def upload_educational_json(self, object_id: str, data: Dict[str, Any]) -> AlmacenamientoOCI:
        validate_object_id(object_id); self._write(settings.OCI_BUCKET_OUTPUTS, object_id, json.dumps(data, indent=2, ensure_ascii=False).encode())
        return AlmacenamientoOCI(bucket=settings.OCI_BUCKET_OUTPUTS, objeto_id=object_id, status_upload="completado (local/emulado)")

local_storage = LocalStorageClient()
