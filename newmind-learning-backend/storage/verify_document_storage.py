"""Strict readback, with no settings imports, credentials discovery or SDK creation."""

from pathlib import Path
from typing import Any, Literal

from storage.contracts import StorageResult, validate_object_id


class VerificationError(ValueError):
    """Secret-safe failure: no persistence proof is available."""


def verify_document_storage(
    result: StorageResult,
    expected_content: bytes,
    *,
    expected_bucket: str,
    expected_object_id: str,
    local_root: Path | None = None,
    client: Any = None,
    namespace: str | None = None,
    require_oci: bool = False,
) -> Literal["LOCAL", "OCI"]:
    """Verify exact identity and original bytes; mocks only prove verifier behavior.

    A cloud client and namespace must be explicitly supplied by the caller.
    This function never obtains permission or credentials on the caller's behalf.
    """
    if (result.bucket, result.object_id) != (expected_bucket, expected_object_id):
        raise VerificationError("Storage identity mismatch.")
    if result.mode not in ("oci", "local_emulation") or result.status not in (
        "completed",
        "local_fallback",
    ):
        raise VerificationError("Invalid storage mode or status.")
    if require_oci and (result.mode != "oci" or result.status != "completed"):
        raise VerificationError("OCI persistence required; local storage is not proof.")

    if result.mode == "local_emulation":
        if local_root is None:
            raise VerificationError("Local root must be explicitly supplied.")
        try:
            validate_object_id(result.object_id)
            validate_object_id(result.bucket)
            root = Path(local_root).resolve()
            path = (root / result.bucket / result.object_id).resolve()
            if not path.is_relative_to(root):
                raise ValueError("Outside local root")
            actual = path.read_bytes()
        except Exception:
            raise VerificationError("Local readback failed.") from None
        label = "LOCAL"
    else:
        if result.status != "completed" or result.error_code is not None:
            raise VerificationError("OCI completion required.")
        if client is None or not namespace or not namespace.strip():
            raise VerificationError("Explicit OCI client and namespace required.")
        identity = dict(
            namespace_name=namespace,
            bucket_name=result.bucket,
            object_name=result.object_id,
        )
        try:
            head = client.head_object(**identity)
            length = head.headers["content-length"]
            if not (
                type(length) is int
                or (isinstance(length, str) and length.isascii() and length.isdecimal())
            ):
                raise ValueError("Invalid content-length")
            if head.status != 200 or int(length) != len(expected_content):
                raise ValueError("Invalid head response")
            get = client.get_object(**identity)
            if get.status != 200:
                raise ValueError("Invalid get response")
            if result.etag is not None and any(
                response.headers.get("etag") != result.etag for response in (head, get)
            ):
                raise ValueError("ETag mismatch")
            actual = get.data.content
        except Exception:
            raise VerificationError("OCI readback failed.") from None
        label = "OCI"
    if not isinstance(actual, bytes) or actual != expected_content:
        raise VerificationError("Stored bytes do not match original content.")
    return label
