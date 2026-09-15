"""
Esquemas Pydantic y Contratos de Datos para NuevaMente.
Cumple estrictamente con la especificación del Hackathon ONE G10 (Páginas 4 y 5 del PDF).
"""
from enum import Enum
from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel, Field

# --- Enumeraciones de Entrada ---
class PerfilDestinatario(str, Enum):
    PRINCIPIANTE = "Principiante"
    JUNIOR_MID = "Desarrollador Junior / Semi Senior"
    ARQUITECTO = "Líder Técnico / Arquitecto"
    EJECUTIVO = "Gestor / Ejecutivo (No Técnico)"

class FormatoSalida(str, Enum):
    FLASHCARDS = "Flashcards"
    QUIZ = "Quiz Interactivo"
    TUTORIAL = "Guía Práctica Paso a Paso (Tutorial)"
    RESUMEN = "Resumen Ejecutivo (TL;DR)"
    GUION = "Guion de Clase / Video"

class NichoSector(str, Enum):
    FINTECH = "Fintech"
    SALUD = "Salud"
    ECOMMERCE = "E-commerce"
    GENERAL = "General"

class NivelDetalle(str, Enum):
    DIDACTICO = "Didactico"
    TECNICO = "Tecnico"
    EJECUTIVO = "Ejecutivo"

# --- Modelo de Solicitud (Entrada) ---
class SolicitudAdaptacion(BaseModel):
    documento_titulo: str = Field(..., description="Título del documento técnico")
    documento_contenido: str = Field(..., description="Contenido en texto del documento técnico")
    perfil_destinatario: PerfilDestinatario = Field(default=PerfilDestinatario.PRINCIPIANTE)
    formato_salida: FormatoSalida = Field(default=FormatoSalida.FLASHCARDS)
    nicho_sector: NichoSector = Field(default=NichoSector.GENERAL)
    nivel_detalle: NivelDetalle = Field(default=NivelDetalle.DIDACTICO)

# --- Modelos de Elementos Pedagógicos (Items) ---
class FlashcardItem(BaseModel):
    frente: str = Field(..., description="Pregunta o concepto clave")
    dorso: str = Field(..., description="Explicación adaptada pedagógicamente")
    pista_didactica: Optional[str] = Field(None, description="Analogía o pista para facilitar memorización")

class QuizItem(BaseModel):
    pregunta: str = Field(..., description="Pregunta de evaluación")
    opciones: List[str] = Field(..., description="Lista de opciones de respuesta")
    respuesta_correcta: str = Field(..., description="Opción correcta")
    justificacion_didactica: str = Field(..., description="Fundamentación de la respuesta basada en el texto fuente")
    pista_didactica: Optional[str] = Field(None, description="Pista conceptual")

class TutorialStepItem(BaseModel):
    paso: int = Field(..., description="Número de paso")
    titulo_paso: str = Field(..., description="Nombre del paso")
    descripcion: str = Field(..., description="Instrucciones detalladas")
    comando_o_codigo: Optional[str] = Field(None, description="Snippet o comando si aplica")
    verificacion: str = Field(..., description="Cómo verificar que el paso se completó con éxito")

# --- Metadatos y Contenido ---
class MetadatosAprendizaje(BaseModel):
    perfil_aplicado: str = Field(..., description="Perfil del estudiante aplicado")
    formato_generado: str = Field(..., description="Formato pedagógico generado")
    tiempo_estimado_estudio_minutos: int = Field(..., description="Tiempo estimado en minutos")
    conceptos_clave: List[str] = Field(..., description="Conceptos clave extraídos")

class ContenidoAdaptado(BaseModel):
    titulo: str = Field(..., description="Título pedagógico adaptado")
    introduccion_contextualizada: str = Field(..., description="Introducción con analogía acorde al perfil y nicho")
    items: List[Dict[str, Any]] = Field(..., description="Lista de elementos pedagógicos (flashcards, quiz, pasos)")

class EvaluacionCalidad(BaseModel):
    anclaje_fuente_score: float = Field(..., ge=0.0, le=1.0, description="Puntuación de fidelidad al documento (0 a 1)")
    claridad_pedagogica: str = Field(..., description="Nivel de claridad (Alta, Media, Regular)")
    observaciones: str = Field(..., description="Comentarios sobre la adaptación y prevención de alucinaciones")

class AlmacenamientoOCI(BaseModel):
    bucket: str = Field(..., description="Nombre del bucket en OCI Object Storage")
    objeto_id: str = Field(..., description="Nombre del archivo JSON almacenado en OCI")
    status_upload: str = Field(default="completado", description="Estado de la persistencia (completado/emulado)")

# --- Modelo de Respuesta Final (Salida Estructurada) ---
class RespuestaAdaptacion(BaseModel):
    status: str = Field(default="exito", description="Estado de la operación")
    metadatos: MetadatosAprendizaje
    contenido_adaptado: ContenidoAdaptado
    evaluacion_calidad: EvaluacionCalidad
    almacenamiento_oci: AlmacenamientoOCI
