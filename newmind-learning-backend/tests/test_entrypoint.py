"""Tests for the backend container entrypoint."""

from main import build_health_payload


def test_build_health_payload_contains_runtime_status():
    payload = build_health_payload()

    assert payload["status"] == "ok"
    assert payload["service"] == "newmind-learning-backend"
    assert payload["oci_mode"] in {"emulated", "oci", "b2"}
    assert payload["oci_storage"]["mode"] in {
        "local_emulation",
        "oci",
        "b2",
    }
    assert "chroma_persist_dir" in payload

    storage = payload["oci_storage"]
    provider = storage.get("provider")

    if provider in {"backblaze_b2", "local"}:
        # Los proveedores alternativos exponen su propio estado.
        assert "real_storage_ready" in storage
        assert "local_fallback" in storage
    else:
        # Conserva las comprobaciones específicas del cliente OCI.
        assert storage["auth_source"] in {
            "config_file",
            "explicit_env",
            "local_emulation",
        }
        assert "real_oci_ready" in storage
        assert "missing_required_fields" in storage
