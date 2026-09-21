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


def test_upload_raw_document():
    content = b"Contenido de prueba para almacenamiento OCI"
    res = oci_storage.upload_raw_document("test_doc.txt", content)
    assert res["status"] in ["completado", "emulado_local"]
    assert res["object_id"] == "test_doc.txt"

def test_upload_educational_json():
    data = {"prueba": "valor", "estado": "ok"}
    res = oci_storage.upload_educational_json("resultado_test.json", data)
    assert res.objeto_id == "resultado_test.json"
    assert "completado" in res.status_upload
