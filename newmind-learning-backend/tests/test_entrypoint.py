"""Tests for the backend container entrypoint."""

from main import build_health_payload


def test_build_health_payload_contains_runtime_status():
    payload = build_health_payload()

    assert payload["status"] == "ok"
    assert payload["service"] == "newmind-learning-backend"
    assert payload["oci_mode"] in {"emulated", "oci"}
    assert "chroma_persist_dir" in payload
