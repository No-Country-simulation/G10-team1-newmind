"""Tests for the backend container entrypoint."""

from main import build_health_payload


def test_build_health_payload_contains_runtime_status():
    payload = build_health_payload()

    assert payload["status"] == "ok"
    assert payload["service"] == "newmind-learning-backend"
    assert payload["oci_mode"] in {"emulated", "oci"}
    assert payload["oci_storage"]["mode"] in {"local_emulation", "oci"}
    assert payload["oci_storage"]["auth_source"] in {
        "config_file",
        "explicit_env",
        "local_emulation",
    }
    assert "real_oci_ready" in payload["oci_storage"]
    assert "missing_required_fields" in payload["oci_storage"]
    assert "chroma_persist_dir" in payload
