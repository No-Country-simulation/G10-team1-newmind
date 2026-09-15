"""
Módulo de Chunking y Segmentación de Documentos.
Divide textos largos en fragmentos contextuales (chunks) con solapamiento y metadatos.
"""
from typing import List, Dict, Any, Optional
from config.settings import settings

class DocumentChunker:
    def __init__(self, chunk_size: Optional[int] = None, chunk_overlap: Optional[int] = None):
        self.chunk_size = chunk_size or settings.DEFAULT_CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.DEFAULT_CHUNK_OVERLAP

    def split_text(self, text: str, source_id: str = "documento") -> List[Dict[str, Any]]:
        """
        Segmenta el texto de manera recursiva respetando párrafos, oraciones y palabras.
        Retorna una lista de diccionarios con contenido y metadatos de trazabilidad.
        """
        if not text or not text.strip():
            return []

        separators = ["\n\n", "\n", ". ", " ", ""]
        raw_chunks = self._recursive_split(text, separators, self.chunk_size)
        
        # Combinar fragmentos pequeños y aplicar solapamiento
        chunks_with_overlap = []
        current_chunk = ""
        
        for fragment in raw_chunks:
            if len(current_chunk) + len(fragment) <= self.chunk_size:
                current_chunk += fragment
            else:
                if current_chunk.strip():
                    chunks_with_overlap.append(current_chunk.strip())
                # Iniciar nuevo chunk reteniendo el solapamiento del anterior
                overlap_text = current_chunk[-self.chunk_overlap:] if len(current_chunk) > self.chunk_overlap else current_chunk
                current_chunk = overlap_text + fragment

        if current_chunk.strip():
            chunks_with_overlap.append(current_chunk.strip())

        # Enriquecer con metadatos
        result = []
        for idx, chunk_content in enumerate(chunks_with_overlap):
            result.append({
                "chunk_id": f"{source_id}_chunk_{idx:03d}",
                "source": source_id,
                "chunk_index": idx,
                "total_chars": len(chunk_content),
                "content": chunk_content
            })

        return result

    def _recursive_split(self, text: str, separators: List[str], max_size: int) -> List[str]:
        if len(text) <= max_size or not separators:
            return [text]

        sep = separators[0]
        remaining_seps = separators[1:]
        
        if sep == "":
            # División por caracteres directa si no quedan separadores
            return [text[i:i+max_size] for i in range(0, len(text), max_size)]

        splits = text.split(sep)
        result = []
        for s in splits:
            if not s:
                continue
            item = s + sep
            if len(item) <= max_size:
                result.append(item)
            else:
                result.extend(self._recursive_split(item, remaining_seps, max_size))

        return result

doc_chunker = DocumentChunker()
