"""
Cliente OCI Object Storage para la capa Always Free.
Soporta autenticación con OCI SDK y modo emulado local de persistencia para pruebas continuas.
"""
import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from config.settings import settings
from models.schemas import AlmacenamientoOCI

logger = logging.getLogger(__name__)

EXPLICIT_ENV_AUTH_FIELDS = [
    "OCI_USER_OCID",
    "OCI_FINGERPRINT",
    "OCI_TENANCY_OCID",
    "OCI_REGION",
    "OCI_KEY_FILE",
    "OCI_OBJECT_STORAGE_NAMESPACE",
]


def _present(value: Any) -> bool:
    return value is not None and str(value).strip() != ""


def build_oci_storage_readiness(
    *,
    is_emulated: bool,
    namespace: str | None,
) -> dict[str, Any]:
    """Return secret-safe OCI Object Storage readiness metadata."""
    config_path = os.path.expanduser(settings.OCI_CONFIG_FILE)
    config_file_exists = os.path.exists(config_path)
    missing_explicit_fields = [
        field for field in EXPLICIT_ENV_AUTH_FIELDS if not _present(getattr(settings, field))
    ]
    explicit_env_configured = not missing_explicit_fields

    if config_file_exists:
        auth_source = "config_file"
        missing_required_fields = []
    elif explicit_env_configured:
        auth_source = "explicit_env"
        missing_required_fields = []
    else:
        auth_source = "local_emulation"
        missing_required_fields = missing_explicit_fields

    bucket_names = [settings.OCI_BUCKET_DOCS, settings.OCI_BUCKET_OUTPUTS]
    buckets_configured = all(_present(bucket) for bucket in bucket_names)
    runtime_mode = "local_emulation" if is_emulated else "oci"

    return {
        "mode": runtime_mode,
        "auth_source": auth_source,
        "real_oci_ready": runtime_mode == "oci" and auth_source != "local_emulation",
        "local_fallback": runtime_mode == "local_emulation",
        "missing_required_fields": missing_required_fields,
        "namespace": namespace if _present(namespace) else None,
        "buckets": bucket_names if buckets_configured else [],
    }

class OCIStorageClient:
    def __init__(self):
        self.client = None
        self.namespace = settings.OCI_OBJECT_STORAGE_NAMESPACE
        self.is_emulated = True
        self._init_oci_client()

    def _init_oci_client(self):
        """Inicializa el cliente de OCI SDK si las credenciales están presentes."""
        try:
            import oci
            
            # Intento 1: Cargar desde archivo de configuración estándar (~/.oci/config)
            config_path = os.path.expanduser(settings.OCI_CONFIG_FILE)
            if os.path.exists(config_path):
                config = oci.config.from_file(config_path, settings.OCI_CONFIG_PROFILE)
                self.client = oci.object_storage.ObjectStorageClient(config)
                if not self.namespace:
                    self.namespace = self.client.get_namespace().data
                self.is_emulated = False
                logger.info(f"OCI Client conectado exitosamente vía config file. Namespace: {self.namespace}")
                return

            # Intento 2: Cargar desde variables de entorno explícitas
            if settings.OCI_USER_OCID and settings.OCI_TENANCY_OCID and settings.OCI_KEY_FILE:
                key_path = os.path.expanduser(settings.OCI_KEY_FILE)
                if os.path.exists(key_path):
                    config = {
                        "user": settings.OCI_USER_OCID,
                        "fingerprint": settings.OCI_FINGERPRINT,
                        "tenancy": settings.OCI_TENANCY_OCID,
                        "region": settings.OCI_REGION,
                        "key_file": key_path
                    }
                    oci.config.validate_config(config)
                    self.client = oci.object_storage.ObjectStorageClient(config)
                    if not self.namespace:
                        self.namespace = self.client.get_namespace().data
                    self.is_emulated = False
                    logger.info(f"OCI Client conectado exitosamente vía variables de entorno. Namespace: {self.namespace}")
                    return

        except Exception as e:
            logger.warning(f"No se pudo conectar a OCI Object Storage: {e}. Usando modo emulado local.")

        # Modo de fallback emulado
        self.is_emulated = True
        self.namespace = self.namespace or "nuevamente-local-namespace"
        settings.LOCAL_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        (settings.LOCAL_STORAGE_DIR / settings.OCI_BUCKET_DOCS).mkdir(parents=True, exist_ok=True)
        (settings.LOCAL_STORAGE_DIR / settings.OCI_BUCKET_OUTPUTS).mkdir(parents=True, exist_ok=True)
        logger.info(f"OCI Storage operando en modo local emulado en: {settings.LOCAL_STORAGE_DIR}")

    def readiness(self) -> dict[str, Any]:
        """Return secret-safe runtime readiness for health checks."""
        return build_oci_storage_readiness(
            is_emulated=self.is_emulated,
            namespace=self.namespace,
        )

    def upload_raw_document(self, filename: str, content: bytes, content_type: str = "application/octet-stream") -> Dict[str, Any]:
        """Sube un documento original al bucket de documentos de origen."""
        bucket_name = settings.OCI_BUCKET_DOCS
        if not self.is_emulated and self.client:
            try:
                import oci
                response = self.client.put_object(
                    namespace_name=self.namespace,
                    bucket_name=bucket_name,
                    object_name=filename,
                    put_object_body=content,
                    content_type=content_type
                )
                return {
                    "status": "completado",
                    "bucket": bucket_name,
                    "object_id": filename,
                    "etag": response.headers.get("etag")
                }
            except Exception as e:
                logger.error(f"Error subiendo a OCI: {e}. Guardando en réplica local.")

        # Guardado local emulado
        dest_path = settings.LOCAL_STORAGE_DIR / bucket_name / filename
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        with open(dest_path, "wb") as f:
            f.write(content)

        return {
            "status": "emulado_local",
            "bucket": bucket_name,
            "object_id": filename,
            "local_path": str(dest_path)
        }

    def upload_educational_json(self, object_id: str, data: Dict[str, Any]) -> AlmacenamientoOCI:
        """Sube el contenido educativo generado en formato JSON al bucket de resultados."""
        bucket_name = settings.OCI_BUCKET_OUTPUTS
        json_bytes = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")

        if not self.is_emulated and self.client:
            try:
                self.client.put_object(
                    namespace_name=self.namespace,
                    bucket_name=bucket_name,
                    object_name=object_id,
                    put_object_body=json_bytes,
                    content_type="application/json"
                )
                return AlmacenamientoOCI(
                    bucket=bucket_name,
                    objeto_id=object_id,
                    status_upload="completado"
                )
            except Exception as e:
                logger.error(f"Error subiendo JSON a OCI: {e}. Guardando localmente.")

        # Guardado local emulado
        dest_path = settings.LOCAL_STORAGE_DIR / bucket_name / object_id
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        with open(dest_path, "wb") as f:
            f.write(json_bytes)

        return AlmacenamientoOCI(
            bucket=bucket_name,
            objeto_id=object_id,
            status_upload="completado (local/emulado)"
        )

# Instancia singleton
oci_storage = OCIStorageClient()
