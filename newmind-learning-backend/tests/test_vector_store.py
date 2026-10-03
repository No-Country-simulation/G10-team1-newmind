from __future__ import annotations

from typing import Any

import chromadb
import pytest
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings

from config.settings import settings
from ingestion.chunker import RAG_METADATA_FIELDS


class DeterministicEmbedding(EmbeddingFunction[Documents]):
    """Small local embedding function with predictable cosine distances."""

    def __init__(self) -> None:
        pass

    def __call__(self, input: Documents) -> Embeddings:
        return [self._embed(text) for text in input]

    @staticmethod
    def _embed(text: str) -> list[float]:
        normalized = text.casefold()
        if "python" in normalized:
            return [1.0, 0.0]
        if "opposite" in normalized:
            return [-1.0, 0.0]
        return [0.0, 1.0]

    @staticmethod
    def name() -> str:
        return "odd-21-deterministic-embedding"

    def get_config(self) -> dict[str, Any]:
        return {}

    @staticmethod
    def build_from_config(config: dict[str, Any]) -> DeterministicEmbedding:
        return DeterministicEmbedding()


class EmbeddingClient:
    """Delegate to a real persistent client while injecting local embeddings."""

    def __init__(self, path: str, persistent_client: Any) -> None:
        self._client = persistent_client(path=path)
        self._embedding = DeterministicEmbedding()

    def get_or_create_collection(self, **kwargs: Any) -> Any:
        return self._client.get_or_create_collection(
            **kwargs,
            embedding_function=self._embedding,
        )

    def delete_collection(self, name: str) -> None:
        self._client.delete_collection(name=name)


@pytest.fixture
def manager_factory(monkeypatch: pytest.MonkeyPatch, tmp_path: Any):
    persist_dir = tmp_path / "chroma"
    persistent_client = chromadb.PersistentClient
    monkeypatch.setattr(settings, "CHROMA_PERSIST_DIR", str(persist_dir))

    import rag.vector_store as vector_store_module

    monkeypatch.setattr(
        vector_store_module.chromadb,
        "PersistentClient",
        lambda path: EmbeddingClient(path, persistent_client),
    )

    def create(collection_name: str = "odd_21_acceptance") -> Any:
        return vector_store_module.VectorStoreManager(collection_name=collection_name)

    return create


def canonical_chunk(
    chunk_id: str,
    content: str,
    *,
    chunk_index: int,
    chunk_count: int,
) -> dict[str, Any]:
    return {
        "chunk_id": chunk_id,
        "content": content,
        "source_filename": "python-guide.md",
        "document_type": "md",
        "extractor": "utf-8",
        "page_count": 0,
        "chunk_index": chunk_index,
        "chunk_count": chunk_count,
        "chunk_length": len(content),
    }


def test_empty_collection_retrieval_returns_no_results(manager_factory: Any):
    manager = manager_factory()

    assert manager.search_similar("Python", top_k=10) == []


def test_indexing_round_trips_flat_metadata_and_observed_cosine_score(
    manager_factory: Any,
):
    manager = manager_factory()
    chunks = [
        canonical_chunk(
            "python-lists",
            "Python lists preserve insertion order.",
            chunk_index=0,
            chunk_count=2,
        ),
        canonical_chunk(
            "sql-joins",
            "SQL joins combine rows from tables.",
            chunk_index=1,
            chunk_count=2,
        ),
    ]

    manager.add_chunks(chunks)
    result = manager.search_similar("How do Python lists work?", top_k=1)[0]

    assert result["chunk_id"] == "python-lists"
    assert result["content"] == chunks[0]["content"]
    assert result["metadata"] == {
        field: chunks[0][field] for field in RAG_METADATA_FIELDS
    }
    assert result["distance"] == pytest.approx(0.0)
    assert result["similarity_score"] == pytest.approx(1.0 - result["distance"])


def test_top_k_is_capped_and_negative_similarity_is_not_clamped(manager_factory: Any):
    manager = manager_factory()
    chunks = [
        canonical_chunk("python", "Python reference.", chunk_index=0, chunk_count=3),
        canonical_chunk("sql", "SQL reference.", chunk_index=1, chunk_count=3),
        canonical_chunk(
            "opposite",
            "Opposite direction reference.",
            chunk_index=2,
            chunk_count=3,
        ),
    ]
    manager.add_chunks(chunks)

    results = manager.search_similar("Python query", top_k=99)

    assert len(results) == len(chunks)
    opposite = next(result for result in results if result["chunk_id"] == "opposite")
    assert opposite["distance"] == pytest.approx(2.0)
    assert opposite["similarity_score"] == pytest.approx(
        1.0 - opposite["distance"]
    )
    assert opposite["similarity_score"] < 0.0


def test_indexed_chunks_survive_manager_reinstantiation(manager_factory: Any):
    first_manager = manager_factory("persistent_acceptance")
    chunk = canonical_chunk(
        "persistent-python",
        "Python data persists on disk.",
        chunk_index=0,
        chunk_count=1,
    )
    first_manager.add_chunks([chunk])

    restarted_manager = manager_factory("persistent_acceptance")
    results = restarted_manager.search_similar("Python persistence", top_k=5)

    assert [result["chunk_id"] for result in results] == ["persistent-python"]
    assert results[0]["metadata"] == {
        field: chunk[field] for field in RAG_METADATA_FIELDS
    }


def test_retriever_rejects_chunks_without_an_observed_similarity_score(
    manager_factory: Any,
):
    from rag.retriever import RAGRetriever

    class ScorelessVectorStore:
        def search_similar(self, **_kwargs: Any) -> list[dict[str, str]]:
            return [{"chunk_id": "scoreless", "content": "No observed score"}]

    retriever = RAGRetriever(vs=ScorelessVectorStore())

    with pytest.raises(KeyError, match="similarity_score"):
        retriever.retrieve_context("query")
