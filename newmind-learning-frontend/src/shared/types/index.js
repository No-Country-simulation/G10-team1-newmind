/**
 * @typedef {'Principiante' | 'Junior' | 'Senior' | 'Lider' | 'Gestor'} Profile
 * @typedef {'Flashcards' | 'Tutorial' | 'Quiz' | 'Resumen Ejecutivo' | 'Guion'} ContentFormat
 * @typedef {'Fintech' | 'Salud' | 'E-commerce' | 'General'} Industry
 * @typedef {'Basico' | 'Intermedio' | 'Didactico' | 'Detallado'} DetailLevel
 * @typedef {'pdf' | 'md' | 'txt'} DocumentType
 * @typedef {'pending' | 'processing' | 'completed' | 'failed'} AdaptationStatus
 */

/**
 * @typedef {Object} Document
 * @property {number} id
 * @property {string} title
 * @property {DocumentType} type
 * @property {number} size
 * @property {string} createdAt
 */

/**
 * @typedef {Object} AdaptationRequest
 * @property {number} documentId
 * @property {Profile} profile
 * @property {ContentFormat} format
 * @property {Industry} industry
 * @property {DetailLevel} detailLevel
 */

/**
 * @typedef {Object} QualityEvaluation
 * @property {boolean} approved
 * @property {number} score
 * @property {Object} criteria
 * @property {number} criteria.fidelity
 * @property {number} criteria.profile_alignment
 * @property {number} criteria.format_compliance
 * @property {number} criteria.coherence
 * @property {string[]} issues
 */

/**
 * @typedef {Object} Adaptation
 * @property {number} id
 * @property {number} documentId
 * @property {string} documentTitle
 * @property {Profile} profile
 * @property {ContentFormat} format
 * @property {Industry} industry
 * @property {DetailLevel} detailLevel
 * @property {AdaptationStatus} status
 * @property {Object} [content]
 * @property {QualityEvaluation} [evaluation]
 * @property {number} [iteration]
 * @property {string} createdAt
 * @property {string} [completedAt]
 */

export const PROFILES = [
  { value: 'Principiante', label: 'Principiante / Transición de Carrera', description: 'Lenguaje sencillo y progresivo' },
  { value: 'Junior', label: 'Desarrollador Junior / Semi Senior', description: 'Terminología técnica y ejemplos prácticos' },
  { value: 'Lider', label: 'Líder Técnico / Arquitecto', description: 'Arquitectura, trade-offs y escalabilidad' },
  { value: 'Gestor', label: 'Gestor / Ejecutivo', description: 'Impacto, beneficios y riesgos' },
]

export const FORMATS = [
  { value: 'Tutorial', label: 'Tutorial', icon: '📖', description: 'Pasos detallados con ejemplos' },
  { value: 'Flashcards', label: 'Flashcards', icon: '🃏', description: 'Pregunta y respuesta por concepto' },
  { value: 'Quiz', label: 'Quiz Interactivo', icon: '🧠', description: 'Preguntas con opciones y justificación' },
  { value: 'Resumen Ejecutivo', label: 'Resumen Ejecutivo', icon: '📋', description: 'Puntos clave e impacto' },
  { value: 'Guion', label: 'Guion de Clase/Video', icon: '🎬', description: 'Estructura para presentación' },
]

export const INDUSTRIES = [
  { value: 'General', label: 'General' },
  { value: 'Fintech', label: 'Fintech' },
  { value: 'Salud', label: 'Salud' },
  { value: 'E-commerce', label: 'E-commerce' },
]

export const DETAIL_LEVELS = [
  { value: 'Basico', label: 'Básico', description: 'Conceptos esenciales' },
  { value: 'Intermedio', label: 'Intermedio', description: 'Equilibrio entre teoría y práctica' },
  { value: 'Didactico', label: 'Didáctico', description: 'Orientado al aprendizaje guiado' },
  { value: 'Detallado', label: 'Detallado', description: 'Profundidad técnica completa' },
]

