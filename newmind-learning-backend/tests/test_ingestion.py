"""Pruebas para extracción de texto y chunking."""
from pathlib import Path
from ingestion.loaders import doc_loader
from ingestion.chunker import doc_chunker

def test_chunker_segmentation():
    sample_text = "Párrafo 1 con contenido técnico. " * 30 + "\n\n" + "Párrafo 2 con más detalles. " * 30
    chunks = doc_chunker.split_text(sample_text, source_id="test_doc")
    assert len(chunks) >= 2
    assert "chunk_id" in chunks[0]
    assert "content" in chunks[0]

def test_loader_extract_bytes():
    content = b"# Documento Markdown\n\nEste es un parrafo de prueba."
    text = doc_loader.extract_from_bytes("test.md", content)
    assert "Documento Markdown" in text
    assert "parrafo de prueba" in text
