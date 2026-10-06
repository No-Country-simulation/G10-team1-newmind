"""OCI Object Storage persistence and readiness tests."""
from storage.oci_client import build_oci_storage_readiness, oci_storage


def test_readiness_reports_local_emulation_without_secrets(monkeypatch, tmp_path):
    monkeypatch.setattr("storage.oci_client.settings.OCI_CONFIG_FILE", str(tmp_path / "missing-config"))
    monkeypatch.setattr("storage.oci_client.settings.OCI_USER_OCID", None)
    monkeypatch.setattr("storage.oci_client.settings.OCI_FINGERPRINT", None)
    monkeypatch.setattr("storage.oci_client.settings.OCI_TENANCY_OCID", None)
    monkeypatch.setattr("storage.oci_client.settings.OCI_KEY_FILE", None)
    monkeypatch.setattr("storage.oci_client.settings.OCI_OBJECT_STORAGE_NAMESPACE", None)

    readiness = build_oci_storage_readiness(is_emulated=True, namespace="nuevamente-local-namespace")

    assert readiness["mode"] == "local_emulation"
    assert readiness["auth_source"] == "local_emulation"
    assert readiness["real_oci_ready"] is False
    assert readiness["local_fallback"] is True
    assert set(readiness["missing_required_fields"]) >= {
        "OCI_USER_OCID",
        "OCI_FINGERPRINT",
        "OCI_TENANCY_OCID",
        "OCI_KEY_FILE",
        "OCI_OBJECT_STORAGE_NAMESPACE",
    }
    assert readiness["buckets"] == [
        "nuevamente-documentos-origen",
        "nuevamente-contenidos-educativos",
    ]


def test_readiness_reports_explicit_env_auth_source(monkeypatch, tmp_path):
    monkeypatch.setattr("storage.oci_client.settings.OCI_CONFIG_FILE", str(tmp_path / "missing-config"))
    monkeypatch.setattr("storage.oci_client.settings.OCI_USER_OCID", "configured")
    monkeypatch.setattr("storage.oci_client.settings.OCI_FINGERPRINT", "configured")
    monkeypatch.setattr("storage.oci_client.settings.OCI_TENANCY_OCID", "configured")
    monkeypatch.setattr("storage.oci_client.settings.OCI_REGION", "us-ashburn-1")
    monkeypatch.setattr("storage.oci_client.settings.OCI_KEY_FILE", "configured")
    monkeypatch.setattr("storage.oci_client.settings.OCI_OBJECT_STORAGE_NAMESPACE", "safe-namespace")

    readiness = build_oci_storage_readiness(is_emulated=False, namespace="safe-namespace")

    assert readiness["mode"] == "oci"
    assert readiness["auth_source"] == "explicit_env"
    assert readiness["real_oci_ready"] is True
    assert readiness["local_fallback"] is False
    assert readiness["missing_required_fields"] == []
    assert readiness["namespace"] == "safe-namespace"


def test_readiness_reports_config_file_auth_source(monkeypatch, tmp_path):
    config_file = tmp_path / "config"
    config_file.write_text("[DEFAULT]\n", encoding="utf-8")
    monkeypatch.setattr("storage.oci_client.settings.OCI_CONFIG_FILE", str(config_file))

    readiness = build_oci_storage_readiness(is_emulated=False, namespace="safe-namespace")

    assert readiness["mode"] == "oci"
    assert readiness["auth_source"] == "config_file"
    assert readiness["real_oci_ready"] is True
    assert readiness["missing_required_fields"] == []


def test_upload_raw_document(monkeypatch, tmp_path):
    monkeypatch.setattr("storage.oci_client.settings.LOCAL_STORAGE_DIR", tmp_path)
    content = b"Contenido de prueba para almacenamiento OCI"
    res = oci_storage.upload_raw_document("test_doc.txt", content)
    assert res.mode == "local_emulation"
    assert res.status == "completed"
    assert res.object_id == "test_doc.txt"
    assert (tmp_path / res.bucket / res.object_id).read_bytes() == content


def test_mocked_oci_put_preserves_bytes_and_type(monkeypatch):
    from types import SimpleNamespace
    from unittest.mock import Mock
    from storage.oci_client import OCIStorageClient

    storage = OCIStorageClient()
    storage.is_emulated = False
    storage.namespace = "test-namespace"
    storage.client = Mock()
    storage.client.put_object.return_value = SimpleNamespace(headers={"etag": "test-etag"})
    content = b"\x00\xfforiginal"
    result = storage.upload_raw_document("unique-source.txt", content, "text/plain")
    assert result.mode == "oci"
    assert result.status == "completed"
    assert result.etag == "test-etag"
    storage.client.put_object.assert_called_once_with(
        namespace_name="test-namespace", bucket_name=result.bucket,
        object_name=result.object_id, put_object_body=content, content_type="text/plain",
    )


def test_oci_failure_is_distinct_local_fallback(monkeypatch, tmp_path, caplog):
    from unittest.mock import Mock
    from storage.oci_client import OCIStorageClient

    monkeypatch.setattr("storage.oci_client.settings.LOCAL_STORAGE_DIR", tmp_path)
    storage = OCIStorageClient()
    storage.is_emulated = False
    storage.client = Mock()
    storage.client.put_object.side_effect = RuntimeError("secret-provider-detail")
    result = storage.upload_raw_document("fallback.txt", b"original")
    assert result.mode == "local_emulation"
    assert result.status == "local_fallback"
    assert result.error_code == "oci_write_failed"
    assert (tmp_path / result.bucket / result.object_id).read_bytes() == b"original"
    assert "secret-provider-detail" not in caplog.text


def test_raw_storage_rejects_unsafe_key(monkeypatch, tmp_path):
    import pytest

    monkeypatch.setattr("storage.oci_client.settings.LOCAL_STORAGE_DIR", tmp_path)
    for key in ("../escape.txt", "C:\\escape.txt", "/escape.txt", "", ".."):
        with pytest.raises(ValueError):
            oci_storage.upload_raw_document(key, b"original")

def test_upload_educational_json():
    data = {"prueba": "valor", "estado": "ok"}
    res = oci_storage.upload_educational_json("resultado_test.json", data)
    assert res.objeto_id == "resultado_test.json"
    assert "completado" in res.status_upload


def test_local_write_failure_propagates(monkeypatch, tmp_path):
    import pytest
    blocked = tmp_path / "not-a-directory"
    blocked.write_bytes(b"blocked")
    monkeypatch.setattr("storage.oci_client.settings.LOCAL_STORAGE_DIR", blocked)
    with pytest.raises(OSError):
        oci_storage.upload_raw_document("source.txt", b"original")
