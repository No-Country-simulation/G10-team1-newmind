"""Secret-safe result for original-document storage (not educational JSON)."""

import re
from dataclasses import dataclass
from typing import Literal


def validate_object_id(object_id: str) -> None:
    """Raw documents use a single safe basename, never a user-supplied path."""
    if not re.fullmatch(r"[A-Za-z0-9_-][A-Za-z0-9._-]*", object_id):
        raise ValueError("Invalid raw-document object key.")


@dataclass(frozen=True, slots=True)
class StorageResult:
    mode: Literal["oci", "b2", "local_emulation"]
    status: Literal["completed", "local_fallback"]
    bucket: str
    object_id: str
    etag: str | None = None
    error_code: Literal[
        "oci_write_failed",
        "b2_write_failed",
        "b2_not_configured",
        "b2_client_init_failed",
    ] | None = None
