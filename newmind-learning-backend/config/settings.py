"""
Módulo de Configuración Centralizada para NuevaMente.
Maneja variables de entorno, parámetros de OCI Always Free, configuración de LLMs y Vector Store.
"""
from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Entorno y Logging
    APP_ENV: str = Field(default="development", description="Entorno de ejecución")
    LOG_LEVEL: str = Field(default="INFO", description="Nivel de logging")
    CORS_ORIGINS: str = Field(default="http://localhost:5173", description="Orígenes CORS separados por comas")

    # Proveedores de LLM
    GEMINI_API_KEY: Optional[str] = Field(default=None, description="API Key de Google Gemini")
    OPENAI_API_KEY: Optional[str] = Field(default=None, description="API Key de OpenAI")
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None, description="API Key de Anthropic")

    DEFAULT_LLM_PROVIDER: str = Field(default="gemini", description="Proveedor predeterminado (gemini, openai)")
    DEFAULT_LLM_MODEL: str = Field(default="gemini-1.5-flash", description="Modelo LLM predeterminado")

    # Oracle Cloud Infrastructure (OCI Always Free)
    OCI_CONFIG_FILE: str = Field(default="~/.oci/config", description="Ruta al archivo config de OCI")
    OCI_CONFIG_PROFILE: str = Field(default="DEFAULT", description="Perfil del archivo config OCI")
    OCI_COMPARTMENT_ID: Optional[str] = Field(default=None, description="OCID del compartment OCI para aprovisionamiento")
    OCI_USER_OCID: Optional[str] = Field(default=None, description="OCID del usuario OCI")
    OCI_FINGERPRINT: Optional[str] = Field(default=None, description="Fingerprint de la clave API")
    OCI_TENANCY_OCID: Optional[str] = Field(default=None, description="OCID del tenancy OCI")
    OCI_REGION: str = Field(default="us-ashburn-1", description="Región de OCI")
    OCI_KEY_FILE: Optional[str] = Field(default=None, description="Ruta de la clave privada PEM")
    OCI_OBJECT_STORAGE_NAMESPACE: Optional[str] = Field(default=None, description="Namespace de Object Storage")
    OCI_BUCKET_DOCS: str = Field(default="nuevamente-documentos-origen", description="Bucket para documentos originales")
    OCI_BUCKET_OUTPUTS: str = Field(default="nuevamente-contenidos-educativos", description="Bucket para contenidos generados")

    # Vector Store & RAG
    CHROMA_PERSIST_DIR: str = Field(default=str(BASE_DIR / "data" / "chroma_db"), description="Directorio de persistencia de ChromaDB")
    EMBEDDING_MODEL: str = Field(default="all-MiniLM-L6-v2", description="Modelo de embeddings")
    DEFAULT_CHUNK_SIZE: int = Field(default=1000, description="Tamaño del chunk en caracteres")
    DEFAULT_CHUNK_OVERLAP: int = Field(default=150, description="Solapamiento entre chunks")
    TOP_K_RETRIEVAL: int = Field(default=4, description="Número de chunks relevantes a recuperar")

    # Rutas locales auxiliares
    DATA_DIR: Path = BASE_DIR / "data"
    SAMPLES_DIR: Path = BASE_DIR / "data" / "samples"
    LOCAL_STORAGE_DIR: Path = BASE_DIR / "data" / "oci_local_storage"

settings = Settings()
