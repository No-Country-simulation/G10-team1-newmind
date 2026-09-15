"""
Módulo de Ingestión de Documentos Técnicos.
Extrae texto de archivos PDF, Markdown (.md) y Texto Plano (.txt).
"""
import io
import os
from pathlib import Path
from typing import Union

class DocumentLoader:
    @staticmethod
    def extract_from_bytes(filename: str, content: bytes) -> str:
        """Extrae texto a partir de un flujo de bytes según su extensión."""
        ext = Path(filename).suffix.lower()
        if ext == ".pdf":
            return DocumentLoader._extract_from_pdf_bytes(content)
        elif ext in [".md", ".markdown"]:
            return content.decode("utf-8", errors="replace")
        elif ext in [".txt", ".rst", ".json"]:
            return content.decode("utf-8", errors="replace")
        else:
            # Intentar decodificar como texto plano
            return content.decode("utf-8", errors="replace")

    @staticmethod
    def extract_from_file(file_path: Union[str, Path]) -> str:
        """Lee un archivo del sistema de archivos local y extrae su texto."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"El archivo no existe: {file_path}")

        with open(path, "rb") as f:
            content = f.read()

        return DocumentLoader.extract_from_bytes(path.name, content)

    @staticmethod
    def _extract_from_pdf_bytes(content: bytes) -> str:
        """Extrae texto de un archivo PDF usando pypdf o PyMuPDF."""
        text_parts = []
        try:
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(content))
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(f"--- [Página {i+1}] ---\n" + page_text.strip())
            return "\n\n".join(text_parts)
        except Exception as e:
            # Fallback opcional con fitz (PyMuPDF)
            try:
                import fitz
                doc = fitz.open(stream=content, filetype="pdf")
                for i, page in enumerate(doc):
                    text_parts.append(f"--- [Página {i+1}] ---\n" + page.get_text().strip())
                return "\n\n".join(text_parts)
            except Exception as e2:
                raise RuntimeError(f"Error procesando PDF: {e} / {e2}")

doc_loader = DocumentLoader()
