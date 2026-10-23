import json

from storage.b2_client import BackblazeB2StorageClient
from config.settings import settings


class FakeS3Client:
    def __init__(self):
        self.calls = []
    def put_object(self, **kwargs):
        self.calls.append(kwargs)
        return {"ETag": '"abc123"'}


def make_client():
    client = object.__new__(BackblazeB2StorageClient)
    client.client = FakeS3Client()
    client.is_emulated = False
    client.error_code = None
    return client


def test_b2_raw_upload_calls_s3_put_object():
    storage = make_client()
    result = storage.upload_raw_document("test-doc.txt", b"hello", "text/plain")
    call = storage.client.calls[0]
    assert call["Bucket"] == settings.B2_BUCKET_DOCS
    assert call["Key"] == "test-doc.txt"
    assert call["Body"] == b"hello"
    assert result.mode == "b2"
    assert result.status == "completed"
    assert result.etag == "abc123"


def test_b2_educational_json_upload_calls_s3_put_object():
    storage = make_client()
    result = storage.upload_educational_json("result.json", {"title": "Prueba"})
    call = storage.client.calls[0]
    assert call["Bucket"] == settings.B2_BUCKET_OUTPUTS
    assert call["Key"] == "result.json"
    assert json.loads(call["Body"].decode("utf-8")) == {"title": "Prueba"}
    assert result.status_upload == "completado (Backblaze B2)"

def test_b2_not_configured_reports_local_fallback(monkeypatch, tmp_path):
    storage = object.__new__(BackblazeB2StorageClient)
    storage.client = None
    storage.is_emulated = True
    storage.error_code = "b2_not_configured"

    monkeypatch.setattr(settings, "LOCAL_STORAGE_DIR", tmp_path)

    result = storage.upload_raw_document(
        "test-doc.txt",
        b"hello",
        "text/plain",
    )
    assert result.mode == "local_emulation"
    assert result.status == "local_fallback"
    assert result.error_code == "b2_not_configured"
    assert (tmp_path / settings.B2_BUCKET_DOCS / "test-doc.txt").read_bytes() == b"hello"


def test_b2_write_failure_reports_local_fallback(monkeypatch, tmp_path):
    storage = make_client()
    def fail(**kwargs):
        raise RuntimeError("simulated failure")
    storage.client.put_object = fail
    monkeypatch.setattr(settings, "LOCAL_STORAGE_DIR", tmp_path)
    result = storage.upload_raw_document("test-doc.txt", b"hello", "text/plain")
    assert result.mode == "local_emulation"
    assert result.status == "local_fallback"
    assert (tmp_path / settings.B2_BUCKET_DOCS / "test-doc.txt").read_bytes() == b"hello"
    assert result.error_code == "b2_write_failed"
