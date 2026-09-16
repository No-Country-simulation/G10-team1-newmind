"""
Módulo de Recuperación y Contextualización RAG.
Orquesta la consulta vectorial y construye el bloque de contexto anclado a fuentes para el LLM.
"""
from typing import List, Dict, Any, Tuple
from rag.vector_store import vector_store

class RAGRetriever:
    def __init__(self, vs=None):
        self.vector_store = vs or vector_store

    def retrieve_context(self, query: str, top_k: int = 4) -> Tuple[str, List[Dict[str, Any]], float]:
        """
        Recupera los fragmentos más pertinentes para la consulta.
        Retorna:
          - Texto consolidado del contexto para inyectar en el prompt
          - Lista de chunks recuperados
          - Puntuación promedio de similitud / anclaje a fuente
        """
        chunks = self.vector_store.search_similar(query=query, top_k=top_k)
        if not chunks:
            return "", [], 0.0

        context_blocks = []
        scores = []
        for i, chunk in enumerate(chunks):
            scores.append(chunk.get("similarity_score", 0.8))
            context_blocks.append(
                f"[Fragmento {i+1} | ID: {chunk['chunk_id']}]\n{chunk['content']}"
            )

        combined_context = "\n\n".join(context_blocks)
        avg_score = round(sum(scores) / len(scores), 3) if scores else 0.85

        return combined_context, chunks, avg_score

rag_retriever = RAGRetriever()
