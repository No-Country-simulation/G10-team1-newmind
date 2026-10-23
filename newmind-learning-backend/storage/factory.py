"""Selección del proveedor de almacenamiento; OCI es el predeterminado."""

from config.settings import settings

provider = (settings.STORAGE_PROVIDER or "oci").strip().lower()

if provider not in {"oci", "b2", "local"}:
    raise ValueError(
        "STORAGE_PROVIDER debe ser 'oci', 'b2' o 'local'."
    )

if provider == "b2":
    from storage.b2_client import b2_storage as object_storage
elif provider == "local":
    from storage.local_client import local_storage as object_storage
else:
    from storage.oci_client import oci_storage as object_storage
