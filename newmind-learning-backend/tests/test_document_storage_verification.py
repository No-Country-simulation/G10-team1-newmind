"""Local readback and mocked OCI verifier tests; no deployment evidence."""

from dataclasses import replace
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from storage.contracts import StorageResult
from storage.verify_document_storage import VerificationError, verify_document_storage


@pytest.fixture
def result():
    return StorageResult("oci", "completed", "documents", "unique-source.txt", "etag")


@pytest.fixture
def client():
    fake = Mock()
    fake.head_object.return_value = SimpleNamespace(
        status=200, headers={"content-length": "8", "etag": "etag"}
    )
    fake.get_object.return_value = SimpleNamespace(
        status=200, headers={"etag": "etag"}, data=SimpleNamespace(content=b"original")
    )
    return fake


def verify(result, **kwargs):
    return verify_document_storage(
        result,
        b"original",
        expected_bucket="documents",
        expected_object_id="unique-source.txt",
        **kwargs,
    )


def test_exact_mocked_oci_readback(result, client):
    assert (
        verify(result, client=client, namespace="namespace", require_oci=True) == "OCI"
    )
    for operation in (client.head_object, client.get_object):
        operation.assert_called_once_with(
            namespace_name="namespace",
            bucket_name="documents",
            object_name="unique-source.txt",
        )


@pytest.mark.parametrize(
    "length,content",
    [
        (8.9, b"original"),
        (8.0, b"original"),
        (True, b"x"),
        (False, b""),
        (b"8", b"original"),
        (None, b"original"),
        ("8.9", b"original"),
        ("+8", b"original"),
        (" 8 ", b"original"),
        ("0_8", b"original"),
        ("\u0668", b"original"),
        (-1, b"original"),
    ],
)
def test_malformed_content_length_is_not_oci_proof(result, client, length, content):
    client.head_object.return_value.headers["content-length"] = length
    client.get_object.return_value.data.content = content
    with pytest.raises(VerificationError):
        verify_document_storage(
            result,
            content,
            expected_bucket=result.bucket,
            expected_object_id=result.object_id,
            client=client,
            namespace="namespace",
            require_oci=True,
        )
    client.get_object.assert_not_called()


@pytest.mark.parametrize("length", ["8", 8, "008"])
def test_integer_content_length_remains_supported(result, client, length):
    client.head_object.return_value.headers["content-length"] = length
    assert (
        verify(result, client=client, namespace="namespace", require_oci=True) == "OCI"
    )


@pytest.mark.parametrize("status", ["completed", "local_fallback"])
def test_local_readback_never_proves_oci(result, tmp_path, status):
    local = replace(result, mode="local_emulation", status=status, etag=None)
    destination = tmp_path / local.bucket / local.object_id
    destination.parent.mkdir()
    destination.write_bytes(b"original")
    assert verify(local, local_root=tmp_path) == "LOCAL"
    with pytest.raises(VerificationError):
        verify(local, local_root=tmp_path, require_oci=True)


@pytest.mark.parametrize(
    "change",
    [
        {"bucket": "wrong"},
        {"object_id": "wrong.txt"},
        {"status": "local_fallback"},
    ],
)
def test_identity_or_fallback_rejected_before_cloud_calls(result, client, change):
    with pytest.raises(VerificationError):
        verify(
            replace(result, **change),
            client=client,
            namespace="namespace",
            require_oci=True,
        )
    client.head_object.assert_not_called()
    client.get_object.assert_not_called()


@pytest.mark.parametrize("operation", ["head_object", "get_object"])
def test_missing_or_failed_cloud_read_is_not_proof(result, client, operation):
    getattr(client, operation).side_effect = RuntimeError("private-provider-detail")
    with pytest.raises(VerificationError, match="readback failed") as error:
        verify(result, client=client, namespace="namespace", require_oci=True)
    assert "private-provider-detail" not in str(error.value)


@pytest.mark.parametrize(
    "defect",
    [
        "head_status",
        "get_status",
        "missing_size",
        "size",
        "bytes",
        "etag",
        "head_etag",
        "missing_data",
    ],
)
def test_incomplete_or_mismatched_cloud_response_is_not_proof(result, client, defect):
    head = client.head_object.return_value
    get = client.get_object.return_value
    if defect == "head_status":
        head.status = 404
    elif defect == "get_status":
        get.status = 404
    elif defect == "missing_size":
        head.headers = {}
    elif defect == "size":
        head.headers["content-length"] = "7"
    elif defect == "bytes":
        get.data.content = b"modified"
    elif defect == "etag":
        get.headers["etag"] = "different"
    elif defect == "head_etag":
        head.headers["etag"] = "different"
    else:
        get.data = None
    with pytest.raises(VerificationError):
        verify(result, client=client, namespace="namespace", require_oci=True)


@pytest.mark.parametrize("content", [None, b"modified", b"short"])
def test_missing_or_wrong_local_bytes_rejected(result, tmp_path, content):
    local = replace(result, mode="local_emulation", etag=None)
    if content is not None:
        destination = tmp_path / local.bucket / local.object_id
        destination.parent.mkdir()
        destination.write_bytes(content)
    with pytest.raises(VerificationError):
        verify(local, local_root=tmp_path)


def test_oci_requires_explicit_client_and_namespace(result):
    with pytest.raises(VerificationError):
        verify(result, require_oci=True)


@pytest.mark.parametrize(
    "change",
    [{"mode": "unknown"}, {"status": "unknown"}, {"error_code": "oci_write_failed"}],
)
def test_invalid_completion_metadata_is_not_proof(result, client, change):
    with pytest.raises(VerificationError):
        verify(replace(result, **change), client=client, namespace="namespace")
    client.head_object.assert_not_called()


def test_local_root_must_be_explicit(result):
    with pytest.raises(VerificationError):
        verify(replace(result, mode="local_emulation"))


def test_unsafe_local_identity_rejected_even_when_expected_matches(result, tmp_path):
    local = replace(result, mode="local_emulation", object_id="../outside.txt")
    with pytest.raises(VerificationError):
        verify_document_storage(
            local,
            b"original",
            expected_bucket="documents",
            expected_object_id="../outside.txt",
            local_root=tmp_path,
        )
