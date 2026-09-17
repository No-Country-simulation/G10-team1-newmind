"""
Módulo de Vector Store basado en ChromaDB.
Gestiona la indexación, persistencia y recuperación vectorial de fragmentos de documentación técnica.
"""
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from config.settings import settings

logger = logging.getLogger(__name__)

class VectorStoreManager:
    def __init__(self, collection_name: str = "nuevamente_knowledge"):
        self.persist_dir = Path(settings.CHROMA_PERSIST_DIR)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.collection_name = collection_name
        self.client = chromadb.PersistentClient(path=str(self.persist_dir))
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        logger.info(f"ChromaDB inicializado en: {self.persist_dir}. Colección: {self.collection_name}")

    def add_chunks(self, chunks: List[Dict[str, Any]]):
        """Indexa una lista de fragmentos con sus metadatos e IDs."""
        if not chunks:
            return

        documents = [c["content"] for c in chunks]
        metadatas = [
            {
                "source": c.get("source", "doc"),
                "chunk_index": c.get("chunk_index", 0),
                "total_chars": c.get("total_chars", len(c["content"]))
            }
            for c in chunks
        ]
        ids = [c["chunk_id"] for c in chunks]

        # Upsert en ChromaDB
        self.collection.upsert(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        logger.info(f"Se indexaron {len(chunks)} fragmentos en ChromaDB.")

    def search_similar(self, query: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """Realiza una búsqueda semántica y retorna los fragmentos más relevantes."""
        k = top_k or settings.TOP_K_RETRIEVAL
        count = self.collection.count()
        if count == 0:
            return []

        actual_k = min(k, count)
        results = self.collection.query(
            query_texts=[query],
            n_results=actual_k
        )

        retrieved_docs = []
        if results and results.get("documents") and len(results["documents"]) > 0:
            docs = results["documents"][0]
            metas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(docs)
            distances = results["distances"][0] if results.get("distances") else [0.0] * len(docs)
            ids = results["ids"][0] if results.get("ids") else [f"doc_{i}" for i in range(len(docs))]

            for doc_id, doc, meta, dist in zip(ids, docs, metas, distances):
                # En distancia coseno de chroma: similitud = 1.0 - distancia
                similarity = max(0.0, min(1.0, 1.0 - dist))
                retrieved_docs.append({
                    "chunk_id": doc_id,
                    "content": doc,
                    "metadata": meta,
                    "similarity_score": round(similarity, 4)
                })

        return retrieved_docs

    def clear(self):
        """Limpia la colección actual."""
        try:
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
        except Exception as e:
            logger.warning(f"Error reiniciando colección: {e}")

vector_store = VectorStoreManager()
