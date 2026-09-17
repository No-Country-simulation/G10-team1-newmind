"""Pruebas de persistencia OCI Object Storage."""
from storage.oci_client import oci_storage

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
