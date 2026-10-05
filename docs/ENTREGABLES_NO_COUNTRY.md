# Entregables Oficiales - Plataforma No Country (Hackathon ONE G10)

Este documento describe los cuatro entregables previstos para el proyecto **NuevaMente**.

---

## Tarea 1: Documentación del Proyecto
- **Formato:** Markdown en la plataforma y archivo `README.md` en el repositorio; confirmar el formato exigido en la convocatoria vigente antes de enviar.
- **Contenido Requerido:**
  - Descripción y propuesta de valor del proyecto.
  - Arquitectura RAG + LLM + OCI Object Storage, indicando cuándo el almacenamiento utiliza emulación local y cuándo opera contra OCI real.
  - Guía de instalación y ejecución local para la interfaz React/Vite y la API FastAPI (no para una app Streamlit).
  - Especificación de la API: carga `POST /api/v1/documents` mediante archivo y creación `POST /api/v1/adaptations` mediante `documentId`, `profile`, `format`, `industry` y `detailLevel`; salida estructurada en `officialResponse` al completarse.
  - Equipo y roles, sujetos a confirmación de los integrantes antes de publicarlos como asignaciones oficiales.
- **Responsables:** La planificación histórica nombra a Martin Morfe (PM) y Esteban Morales (Architect); sus asignaciones actuales para el envío deben confirmarse con el equipo.

---

## Tarea 2: Video Demo del Proyecto
- **Formato:** Enlace de YouTube (duración de 2:30 a 3:00 min según el guion original; verificar vigencia del requisito en la plataforma). No consta aquí un video publicado o enviado.
- **Estructura del Guion:**
  1. **0:00 - 0:30:** Introducción, problema y propuesta de NuevaMente.
  2. **0:30 - 1:15:** Carga de un documento técnico desde React/Vite a FastAPI; mostrar persistencia real en OCI solo si se verificó en esa ejecución, o identificar explícitamente la emulación local.
  3. **1:15 - 2:00:** Recuperación RAG y adaptación del mismo documento para perfiles distintos (por ejemplo, Principiante y Líder); no atribuir el trabajo a un sistema multiagente.
  4. **2:00 - 2:30:** Demostración de la respuesta JSON y alcance de la puntuación de anclaje; evitar presentarla como validación pedagógica independiente.
- **Responsables:** El plan original nombra a Cristian Contreras y Diana Castaño (Frontend), Harol Medina y Heiner Godoy (Full Stack); confirmar participación y responsabilidades de grabación antes de atribuir la entrega.

---

## Tarea 3: Herramientas del Equipo
- **Formato:** Selección en la plataforma de No Country; verificar la lista final enviada.
- **Tecnologías Clave:**
  - *IA / RAG:* ChromaDB, Sentence Transformers, cliente de Gemini, PyPDF y Pydantic; LangChain u otros proveedores solo si su uso se verifica en el entorno de la entrega.
  - *Frontend:* React y Vite con HTML/CSS/JavaScript; Streamlit corresponde al plan original, no a la interfaz vigente.
  - *Cloud / Storage:* Cliente OCI Object Storage (`oci`) con modo local emulado; verificar credenciales y objetos en OCI para declarar uso efectivo de Always Free.
  - *DevOps & Colaboración:* Python, FastAPI, Docker Compose, Git, GitHub y pytest; no dar por aprobadas plataformas o despliegues sin evidencias.
- **Responsables:** El plan original nombra a Ivan Hernandez (DevOps) y Esteban Morales (Architect); confirmar las asignaciones actuales antes del envío.

---

## Tarea 4: Enlaces del Proyecto
- **Formato:** Enlaces públicos agregados a la plataforma; no se acredita su registro en este documento.
- **Checklist:**
  - Repositorio GitHub de la solución: verificar URL y permisos antes de publicarla.
  - Enlace al video de YouTube: pendiente de confirmar publicación y accesibilidad.
  - Enlace a la app desplegada: pendiente de confirmar; `http://localhost:5173` (interfaz) y `http://localhost:8000` (API) son accesos locales de desarrollo, no enlaces públicos.
  - Documentación técnica: comprobar que las rutas y referencias publicadas correspondan a la versión entregada.
- **Responsables:** El plan original nombra a Ivan Hernandez (DevOps) y Martin Morfe (PM); confirmar responsables efectivos y registro en la plataforma.
