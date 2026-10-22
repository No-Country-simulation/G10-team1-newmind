"""Public selection -> ingestion -> retrieval regressions"""

from hashlib import sha256
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from application.repositories import AdaptationRepository, DocumentRepository
from application.services import AdaptationService, DocumentService
from ingestion.chunker import DocumentChunker
from ingestion.loaders import doc_loader
from llm import engine as engine_module
from llm.engine import LLMEngine
from main import create_app
from models.schemas import AlmacenamientoOCI
from rag.retriever import RAGRetriever
from tests.test_api import FakeStorage, adaptation_payload
from tests.test_vector_store import canonical_chunk, manager_factory


@pytest.fixture
def selected_document_flow(manager_factory, monkeypatch):
    from config.settings import settings

    monkeypatch.setattr(settings, "STORAGE_PROVIDER", "local")

    manager = manager_factory("document_isolation")
    documents = DocumentService(
        DocumentRepository(), loader=doc_loader,
        chunker=DocumentChunker(chunk_size=120, chunk_overlap=0),
        vector_store=manager, storage=FakeStorage(),
    )
    engine = LLMEngine()
    engine.grok_key = engine.gemini_key = engine.openai_key = None
    prompts = []

    def generate(system_prompt, user_prompt, request):
        prompts.append(user_prompt)
        return {
            "titulo": "Selected source", "introduccion_contextualizada": "Source summary",
            "tiempo_estimado_estudio_minutos": 5, "conceptos_clave": ["Python"],
            "items": [{"seccion": "Source", "contenido": user_prompt}],
        }

    monkeypatch.setattr(engine, "_call_llm", generate)
    monkeypatch.setattr(engine_module, "rag_retriever", RAGRetriever(vs=manager))
    monkeypatch.setattr(
        engine_module, "oci_storage", SimpleNamespace(
            upload_educational_json=lambda key, payload: AlmacenamientoOCI(
                bucket="outputs", objeto_id=key,
            ),
        ),
    )
    adaptations = AdaptationService(documents, AdaptationRepository(), engine=engine)
    with TestClient(create_app(documents, adaptations)) as client:
        yield SimpleNamespace(
            client=client, documents=documents, manager=manager, prompts=prompts, engine=engine,
        )


def upload(flow, filename, text):
    response = flow.client.post(
        "/api/v1/documents", files={"file": (filename, text.encode(), "text/plain")},
    )
    assert response.status_code == 201
    return response.json()["id"]


def adapt(flow, document_id):
    response = flow.client.post("/api/v1/adaptations", json=adaptation_payload(document_id))
    assert response.status_code == 202
    job_id = response.json()["id"]
    status = flow.client.get(f"/api/v1/adaptations/{job_id}/status")
    assert status.status_code == 200
    assert status.json()["status"] == "completed"
    result = flow.client.get(f"/api/v1/adaptations/{job_id}")
    assert result.status_code == 200
    assert result.json()["documentId"] == document_id
    return result.json()


def test_selected_document_http_workflow_excludes_overlapping_other_document(selected_document_flow):
    flow = selected_document_flow
    first = "Python lists preserve insertion order. FIRST_SOURCE_PASSAGE."
    second = "Python lists preserve insertion order. SECOND_SOURCE_PASSAGE."
    first_id = upload(flow, "first.txt", first)
    second_id = upload(flow, "second.txt", second)

    for selected, expected, foreign in [(first_id, first, second), (second_id, second, first)]:
        result = adapt(flow, selected)
        assert expected in flow.prompts[-1]
        assert foreign not in flow.prompts[-1]
        assert expected in result["content"]["items"][0]["contenido"]
        assert foreign not in result["content"]["items"][0]["contenido"]
        identity = flow.documents.get(selected).rag_document_id
        indexed = flow.manager.collection.get(where={"document_id": identity})
        assert indexed["documents"] == [expected]
        assert all(meta["document_id"] == identity for meta in indexed["metadatas"])


@pytest.mark.parametrize("identical_content", [False, True])
def test_same_filename_uploads_keep_distinct_retrieval_identities(selected_document_flow, identical_content):
    flow = selected_document_flow
    first = "Python lists preserve insertion order. FIRST_SOURCE_PASSAGE."
    second = first if identical_content else "Python lists preserve insertion order. SECOND_SOURCE_PASSAGE."
    first_id = upload(flow, "guide.txt", first)
    second_id = upload(flow, "guide.txt", second)
    identities = [flow.documents.get(i).rag_document_id for i in (first_id, second_id)]
    assert identities[0] != identities[1]
    assert flow.manager.collection.count() == 2
    for selected, identity, text in zip((first_id, second_id), identities, (first, second)):
        context, chunks, score = RAGRetriever(vs=flow.manager).retrieve_context(
            "Python", document_id=identity,
        )
        assert len(chunks) == 1
        assert chunks[0]["content"] == text
        assert chunks[0]["metadata"]["document_id"] == identity
        assert text in context
        assert score == pytest.approx(1.0)
        adapt(flow, selected)
        assert text in flow.prompts[-1]
        if not identical_content:
            assert (second if selected == first_id else first) not in flow.prompts[-1]


def test_selected_document_top_k_is_bounded_by_selected_chunk_count(selected_document_flow, monkeypatch):
    flow = selected_document_flow
    selected = upload(flow, "selected.txt", "Python selected passage.")
    upload(flow, "other.txt", "Python foreign passage. " * 20)
    identity = flow.documents.get(selected).rag_document_id
    original_query = flow.manager.collection.query
    calls = []

    def query(**kwargs):
        calls.append(kwargs)
        return original_query(**kwargs)

    monkeypatch.setattr(flow.manager.collection, "query", query)
    results = flow.manager.search_similar("Python", top_k=99, document_id=identity)
    assert len(results) == 1
    assert results[0]["content"] == "Python selected passage."
    assert results[0]["metadata"]["document_id"] == identity
    assert calls[0]["n_results"] == 1
    assert calls[0]["where"] == {"document_id": identity}
    assert len(flow.manager.search_similar("Python", top_k=1, document_id=identity)) == 1


def test_selected_document_without_chunks_never_queries_other_documents(selected_document_flow, monkeypatch):
    flow = selected_document_flow
    selected = upload(flow, "selected.txt", "Python SELECTED_ONLY_SOURCE.")
    upload(flow, "other.txt", "Python FOREIGN_ONLY_SOURCE.")
    flow.manager.collection.delete(where={"source_filename": "selected.txt"})
    calls = []
    original_query = flow.manager.collection.query

    def query(**kwargs):
        calls.append(kwargs)
        return original_query(**kwargs)

    monkeypatch.setattr(flow.manager.collection, "query", query)
    result = adapt(flow, selected)
    assert "SELECTED_ONLY_SOURCE" in flow.prompts[-1]
    assert "FOREIGN_ONLY_SOURCE" not in flow.prompts[-1]
    assert calls == []
    assert result["evaluation"]["score"] == 0.0


def test_no_result_fallback_uses_only_selected_document_content(selected_document_flow, monkeypatch):
    flow = selected_document_flow
    selected = upload(flow, "selected.txt", "Python SELECTED_ONLY_SOURCE.")
    upload(flow, "other.txt", "Python FOREIGN_ONLY_SOURCE.")
    calls = []

    def no_results(**kwargs):
        calls.append(kwargs)
        return {"documents": [[]], "metadatas": [[]], "distances": [[]], "ids": [[]]}

    monkeypatch.setattr(flow.manager.collection, "query", no_results)
    result = adapt(flow, selected)
    assert "SELECTED_ONLY_SOURCE" in flow.prompts[-1]
    assert "FOREIGN_ONLY_SOURCE" not in flow.prompts[-1]
    assert calls == [{
        "query_texts": ["selected Líder Técnico / Arquitecto Resumen Ejecutivo (TL;DR)"],
        "n_results": 1,
        "where": {"document_id": flow.documents.get(selected).rag_document_id},
    }]
    assert result["evaluation"]["score"] == 0.0


def test_empty_selected_content_never_uses_other_document_context(selected_document_flow):
    flow = selected_document_flow
    upload(flow, "other.txt", "Python FOREIGN_ONLY_SOURCE.")
    record = flow.documents.repository.create(
        title="empty", filename="empty.txt", document_type="txt", size=0,
        content="", storage_object_id="empty-original",
    )
    flow.documents.repository.update_storage(
        record.id, FakeStorage().upload_raw_document("empty-original", b"", "text/plain"),
    )
    result = adapt(flow, record.id)
    assert "FOREIGN_ONLY_SOURCE" not in flow.prompts[-1]
    assert "CONTEXTO TÉCNICO VERIFICADO:\n\n" in flow.prompts[-1]
    assert result["evaluation"]["score"] == 0.0


def test_scoped_search_excludes_legacy_chunks_without_changing_unscoped_search(selected_document_flow):
    flow = selected_document_flow
    selected = upload(flow, "selected.txt", "Python selected passage.")
    legacy = canonical_chunk("legacy", "Python legacy passage.", chunk_index=0, chunk_count=1)
    flow.manager.add_chunks([legacy])
    identity = flow.documents.get(selected).rag_document_id
    scoped = flow.manager.search_similar("Python", top_k=99, document_id=identity)
    assert [chunk["content"] for chunk in scoped] == ["Python selected passage."]
    assert flow.manager.search_similar("Python", document_id="unknown-document") == []
    unscoped = flow.manager.search_similar("Python", top_k=99)
    assert {chunk["content"] for chunk in unscoped} == {"Python selected passage.", legacy["content"]}
    assert all(chunk["similarity_score"] == pytest.approx(1.0) for chunk in unscoped)


def test_document_identity_survives_storage_update_and_repository_restart(selected_document_flow):
    flow = selected_document_flow
    selected = upload(flow, "guide.txt", "Python selected passage.")
    original = flow.documents.get(selected)
    flow.documents.repository.update_storage(
        selected, FakeStorage().upload_raw_document("relocated-object", b"", "text/plain"),
    )
    assert flow.documents.get(selected).rag_document_id == original.rag_document_id
    restarted = DocumentService(
        DocumentRepository(), loader=doc_loader, chunker=DocumentChunker(),
        vector_store=flow.manager, storage=FakeStorage(),
    ).upload("guide.txt", b"Python selected passage.", "text/plain")
    assert original.id == restarted.id == 1
    assert original.rag_document_id != restarted.rag_document_id
    assert flow.manager.collection.count() == 2
    reopened = flow.manager.__class__(collection_name=flow.manager.collection_name)
    for record in (original, restarted):
        hits = reopened.search_similar("Python", document_id=record.rag_document_id)
        assert len(hits) == 1
        assert hits[0]["metadata"]["document_id"] == record.rag_document_id


def test_missing_selected_chunks_keep_actual_heuristic_fallback_isolated(selected_document_flow, monkeypatch):
    flow = selected_document_flow
    selected = upload(flow, "selected.txt", "Python SELECTED_ONLY_SOURCE.")
    upload(flow, "other.txt", "Virtual cloud network VCN FOREIGN_ONLY_SOURCE.")
    flow.manager.collection.delete(where={"source_filename": "selected.txt"})
    monkeypatch.setattr(flow.engine, "_call_llm", flow.engine.__class__._call_llm.__get__(flow.engine))
    result = adapt(flow, selected)
    assert result["content"]["titulo"] == "Síntesis Adaptativa: selected"
    assert "FOREIGN_ONLY_SOURCE" not in str(result)
    assert result["evaluation"]["score"] == 0.0


def test_rejected_upload_and_selection_preserve_persisted_index(selected_document_flow):
    flow = selected_document_flow
    upload(flow, "selected.txt", "Python selected passage.")

    def index_hashes():
        return {
            path.relative_to(flow.manager.persist_dir): sha256(path.read_bytes()).hexdigest()
            for path in flow.manager.persist_dir.rglob("*") if path.is_file()
        }

    before = index_hashes()
    for filename, content, detail in [
        ("invalid.exe", b"content", "Unsupported document type. Allowed types: PDF, MD, TXT."),
        ("empty.txt", b"", "Document must not be empty."),
    ]:
        response = flow.client.post(
            "/api/v1/documents", files={"file": (filename, content, "text/plain")},
        )
        assert response.status_code == 422
        assert response.json() == {"detail": detail}
        assert index_hashes() == before
    response = flow.client.post("/api/v1/adaptations", json=adaptation_payload(999))
    assert response.status_code == 404
    assert response.json() == {"detail": "Document not found."}
    assert index_hashes() == before
