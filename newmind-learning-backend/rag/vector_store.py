
"""Vector store ChromaDB con embeddings de Gemini o función de prueba."""

import logging
from pathlib import Path
from typing import Any, Optional

import chromadb
from google import genai
from google.genai import types

from config.settings import settings
from ingestion.chunker import RAG_METADATA_FIELDS

logger = logging.getLogger(__name__)

EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIMENSIONS = 768
BATCH_SIZE = 16


class VectorStoreManager:
    def __init__(
        self,
        collection_name: str = "nuevamente_knowledge_gemini",
        embedding_function: Any = None,
    ):
        self.persist_dir = Path(settings.CHROMA_PERSIST_DIR)
        self.persist_dir.mkdir(parents=True, exist_ok=True)

        self.collection_name = collection_name
        self.embedding_function = embedding_function
        self.embedding_client = None

        self.client = chromadb.PersistentClient(
            path=str(self.persist_dir)
        )

        collection_args = {
            "name": self.collection_name,
            "metadata": {"hnsw:space": "cosine"},
        }

        if self.embedding_function is not None:
            collection_args["embedding_function"] = (
                self.embedding_function
            )

        self.collection = self.client.get_or_create_collection(
            **collection_args
        )

        logger.info(
            "ChromaDB inicializado en: %s. Colección: %s",
            self.persist_dir,
            self.collection_name,
        )

    def _get_embedding_client(self):
        if getattr(self, "embedding_client", None) is None:
            if not settings.GEMINI_API_KEY:
                raise RuntimeError(
                    "GEMINI_API_KEY no está configurada."
                )
            self.embedding_client = genai.Client(
                api_key=settings.GEMINI_API_KEY
            )
        return self.embedding_client

    def _embed_texts(
        self,
        texts: list[str],
        task_type: str,
    ) -> list[list[float]]:
        if not texts:
            return []

        client = self._get_embedding_client()
        vectors = []

        for start in range(0, len(texts), BATCH_SIZE):
            batch = texts[start:start + BATCH_SIZE]

            response = client.models.embed_content(
                model=EMBEDDING_MODEL,
                contents=batch,
                config=types.EmbedContentConfig(
                    task_type=task_type,
                    output_dimensionality=EMBEDDING_DIMENSIONS,
                ),
            )

            embeddings = response.embeddings or []
            if len(embeddings) != len(batch):
                raise RuntimeError(
                    "Gemini devolvió una cantidad inesperada "
                    "de embeddings."
                )

            vectors.extend(
                [embedding.values for embedding in embeddings]
            )

        return vectors

    def add_chunks(self, chunks: list[dict[str, Any]]):
        """Indexa fragmentos usando la función configurada."""
        for start in range(0, len(chunks), BATCH_SIZE):
            batch = chunks[start:start + BATCH_SIZE]

            documents = [chunk["content"] for chunk in batch]
            ids = [chunk["chunk_id"] for chunk in batch]

            metadatas = []
            for chunk in batch:
                metadata = {
                    field: chunk[field]
                    for field in RAG_METADATA_FIELDS
                }
                if chunk.get("document_id") is not None:
                    metadata["document_id"] = chunk["document_id"]
                metadatas.append(metadata)

            args = {
                "ids": ids,
                "documents": documents,
                "metadatas": metadatas,
            }

            if getattr(self, "embedding_function", None) is None:
                args["embeddings"] = self._embed_texts(
                    documents,
                    "RETRIEVAL_DOCUMENT",
                )

            self.collection.upsert(**args)

            logger.info(
                "Se indexaron %s fragmentos en ChromaDB.",
                len(batch),
            )

    def search_similar(
        self,
        query: str,
        top_k: Optional[int] = None,
        *,
        document_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """Busca fragmentos, opcionalmente limitados a un documento."""
        k = top_k or settings.TOP_K_RETRIEVAL
        if k <= 0:
            return []

        scope = (
            {}
            if document_id is None
            else {"where": {"document_id": document_id}}
        )

        if document_id is not None:
            count = len(
                self.collection.get(**scope, include=[])["ids"]
            )
        else:
            count = self.collection.count()

        if count == 0:
            return []

        query_args = {
            "n_results": min(k, count),
            **scope,
        }

        if self.embedding_function is None:
            query_args["query_embeddings"] = self._embed_texts(
                [query],
                "RETRIEVAL_QUERY",
            )
        else:
            query_args["query_texts"] = [query]

        results = self.collection.query(**query_args)

        retrieved_docs = []
        if results and results.get("documents"):
            docs = results["documents"][0]
            metas = (
                results["metadatas"][0]
                if results.get("metadatas")
                else [{}] * len(docs)
            )
            distances = results["distances"][0]
            ids = results["ids"][0]

            for chunk_id, doc, meta, dist in zip(
                ids, docs, metas, distances
            ):
                retrieved_docs.append({
                    "chunk_id": chunk_id,
                    "content": doc,
                    "metadata": meta,
                    "distance": dist,
                    "similarity_score": 1.0 - dist,
                })

        return retrieved_docs

    def clear(self):
        """Elimina y recrea únicamente la colección activa."""
        try:
            self.client.delete_collection(self.collection_name)

            collection_args = {
                "name": self.collection_name,
                "metadata": {"hnsw:space": "cosine"},
            }
            if self.embedding_function is not None:
                collection_args["embedding_function"] = (
                    self.embedding_function
                )

            self.collection = self.client.get_or_create_collection(
                **collection_args
            )
        except Exception:
            logger.exception(
                "Error reiniciando la colección ChromaDB"
            )
            raise


vector_store = VectorStoreManager()
