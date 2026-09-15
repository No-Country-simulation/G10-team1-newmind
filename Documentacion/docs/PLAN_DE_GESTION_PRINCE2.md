# DOCUMENTO DE INICIACIÓN Y GESTIÓN DEL PROYECTO (PID / PROJECT BRIEF)
## METODOLOGÍA PRINCE2 / PRINCE2 AGILE — PROYECTO NUEVAMENTE
### ENTREGABLE OFICIAL — TAREA 1: DOCUMENTACIÓN DEL PROYECTO (NO COUNTRY / HACKATHON ONE G10)

---

> ### AVISO FORMAL: CLÁUSULA DE "LETRA VIVA" (LIVING DOCUMENT)
> Este documento se formula bajo los principios del estándar PRINCE2 Agile como una **"LETRA VIVA"**. No es un documento rígido, definitivo ni estático; se encuentra sujeto a refinamiento, ajuste y mejora continua conforme evoluciona el proyecto a lo largo de sus 5 fases de gestión (Sprints). La junta colegiada del proyecto evaluará y actualizará sus componentes al cierre de cada ciclo.

---

## 1. ENLACES OFICIALES DEL PROYECTO (TAREA 1)

A continuación se relacionan los accesos directos al ecosistema técnico del proyecto:

- **Repositorio Oficial en GitHub:**
  https://github.com/mmorfe-engineer/nuevamente_g10_latam
- **Carpeta de Trabajo Compartida en Google Drive:**
  Carpeta remota: `NuevaMente_Hackathon_ONE_G10`
  (Incluye briefing original en PDF, documentación metodológica y código fuente)
- **Despliegue Local / Aplicación Web:**
  Acceso en servidor local: `http://localhost:8501` (Ejecutable mediante `./run_app.sh`)
- **Documentación de Requerimientos Oficiales ONE G10:**
  https://github.com/mmorfe-engineer/nuevamente_g10_latam/blob/main/docs/HACKATHON_ONE_G10_INDICACIONES.md
- **Estructura Desglosada de Trabajo (EDT en 5 Sprints):**
  https://github.com/mmorfe-engineer/nuevamente_g10_latam/blob/main/docs/EDT_PLAN_DE_TRABAJO_5_SPRINTS.md

---

## 2. DEFINICIÓN DEL PROYECTO (PROJECT DEFINITION)

### 2.1 Antecedentes (Background)
En la industria tecnológica y educativa (EdTech), la documentación técnica, manuales de arquitectura y especificaciones de software crecen a un ritmo acelerado. Estos materiales suelen ser densos y abstractos, dificultando el aprendizaje para diferentes perfiles, desde principiantes en transición laboral hasta arquitectos y ejecutivos. Adaptar manualmente este contenido exige semanas de trabajo de diseñadores instruccionales y expertos técnicos.

### 2.2 Objetivos del Proyecto (Project Objectives)
- Construir un Producto Mínimo Viable (MVP) modular capaz de ingerir documentos técnicos (PDF, Markdown, Texto plano).
- Implementar una canalización RAG (Retrieval-Augmented Generation) con fragmentación semántica y búsqueda vectorial en ChromaDB para fundamentar las respuestas en fuentes reales y evitar alucinaciones.
- Orquestar modelos de lenguaje fundacionales (Google Gemini / OpenAI) con técnicas de role prompting pedagógico basadas en la Taxonomía de Bloom.
- Generar salidas estructuradas en formato JSON estricto validadas mediante modelos Pydantic.
- Disponer de una interfaz interactiva e intuitiva construida sobre Streamlit.
- Integrar la persistencia de documentos originales y paquetes educativos en Oracle Cloud Infrastructure (OCI) Object Storage bajo la capa Always Free.

### 2.3 Alcance del Proyecto (Project Scope)
- Ingestión de documentos técnicos sin necesidad de preprocesamiento manual.
- Parametrización en 4 perfiles de destinatario: Principiante, Desarrollador Junior/Semi Senior, Líder Técnico/Arquitecto y Gestor/Ejecutivo (No Técnico).
- Parametrización en 5 formatos pedagógicos: Flashcards de Memorización, Quizzes Interactivos con retroalimentación, Guías Prácticas Paso a Paso (Tutoriales), Resúmenes Ejecutivos (TL;DR) y Guiones de Clase/Video.
- Contextualización por nichos de aplicación: Fintech, Salud, E-commerce y General.
- Persistencia de origen y destino en OCI Always Free.
- Validación de al menos 3 escenarios reales o simulados.

### 2.4 Exclusiones del Alcance (Scope Exclusions)
- No se contempla el uso de servicios en la nube con costos recurrentes o fuera de la capa Always Free.
- No se desarrollará una app nativa para móviles (iOS/Android) en esta etapa de MVP.
- No se procesarán archivos que contengan material protegido por derechos de autor sin autorización.

### 2.5 Restricciones del Proyecto (Constraints)
- Restricción Presupuestaria: Costo total de infraestructura de $0.00 USD (estricto cumplimiento del programa social ONE).
- Restricción Temporal: 5 semanas calendario (5 Sprints de 1 semana cada uno), con fecha límite el 18 de Octubre de 2026.
- Restricción de Calidad: Métrica de anclaje a fuentes técnicas superior o igual al 85%.

### 2.6 Supuestos (Assumptions)
- Los integrantes del equipo cuentan con conectividad a Internet y estaciones de trabajo con Linux o compatibles.
- Se dispone de una cuenta de OCI activa para el aprovisionamiento de Object Storage en la región asignada.
- Se cuenta con acceso a las cuotas gratuitas de Google AI Studio (Gemini 1.5 Flash) o OpenAI API.

---

## 3. CASO DE NEGOCIO (OUTLINE BUSINESS CASE)

### 3.1 Justificación
La plataforma NuevaMente reduce el ciclo de elaboración de materiales didácticos técnicos de semanas a escasos segundos, democratizando el acceso a documentación compleja y acelerando el upskilling de talentos tecnológicos.

### 3.2 Opciones Analizadas (Business Options)
- Opción 1: No hacer nada. Mantener la adaptación manual de contenidos, perpetuando cuellos de botella y altos costos de consultoría.
- Opción 2: Solución basada en IA genérica (Prompt simple sin RAG). Descartada por alto riesgo de alucinación técnica y falta de trazabilidad.
- Opción 3 (Seleccionada): Arquitectura híbrida RAG + OCI Always Free + LLM con estructuración tipada. Ofrece rigor técnico, costo cero de infraestructura y adaptabilidad pedagógica comprobada.

### 3.3 Tolerancias del Proyecto (Project Tolerances)
- Tolerancia de Costo: +$0.00 USD / -$0.00 USD. Prohibido cualquier gasto monetario.
- Tolerancia de Tiempo: +0 días de retraso en la entrega final de la Semana 5.
- Tolerancia de Alcance: ±0% sobre los 8 requisitos mínimos de la rúbrica oficial.

---

## 4. ESTRUCTURA DE GOBERNANZA Y EQUIPO (PRINCE2 MANAGEMENT TEAM)

La estructura de gobernanza adopta un modelo colegiado y democrático dividido en 5 dimensiones técnicas coordinadas por la facilitación del Project Manager:

### 4.1 Cúspide de Coordinación y Gobierno
- **MARTIN MORFE — Project Manager**
  Responsable de la dirección estratégica, facilitación de ceremonias ágiles, control de tolerancias de tiempo y costo, entrega de los 4 entregables en la plataforma de No Country y resolución de impedimentos de alto nivel.

### 4.2 Project Board Colegiado y Democrático por Dimensiones
El Project Board está conformado democráticamente por los referentes de cada dimensión técnica, asegurando que las decisiones de arquitectura, desarrollo y experiencia de usuario sean consensuadas:

- **Dimensión 1: Arquitectura de Software y Solución**
  Referente: **Esteban Guillermo Morales Velazquez (Solution Architect)**
  Custodio de la arquitectura integral, estándares de integración RAG, selección de patrones de software, control de calidad técnica y mitigación de deuda técnica.

- **Dimensión 2: Backend e Ingestión de Datos**
  Referente: **Juan David Villegas Anaya (Backend Developer)**
  Diseño y construcción de los extractores de documentos técnicos (PDF, Markdown, Texto), sanitización de datos y canalización de fragmentación (chunking).

- **Dimensión 3: Full Stack y Orquestación de Inteligencia Artificial**
  Referentes: **Harol Benjamin Medina Zárate & Heiner Jair Godoy Zamora (Full Stack Developers)**
  Diseño de cadenas de prompts pedagógicos (Taxonomía de Bloom), integración de modelos fundacionales LLM, validación estricta de esquemas JSON con Pydantic y lógica de integración end-to-end.

- **Dimensión 4: Frontend, Experiencia de Usuario y Formatos Pedagógicos**
  Referentes: **Cristian Contreras & Diana Castaño (Frontend Developers)**
  Diseño y desarrollo de la interfaz gráfica interactiva en Streamlit, implementación de visualizadores didácticos (Flashcards, Quizzes evaluables en tiempo real, Tutoriales) y experiencia de usuario adaptativa.

- **Dimensión 5: DevOps, Infraestructura Cloud OCI y Aseguramiento de Calidad**
  Referente: **Ivan Hernandez (DevOps Engineer)**
  Aprovisionamiento y administración de OCI Object Storage Always Free, seguridad de credenciales y claves privadas, suite de pruebas automatizadas (pytest), integración continua y despliegue.

---

## 5. PLAN DE COMUNICACIONES INTEGRAL POR DISCORD

Discord se establece como el espacio de trabajo virtual centralizado del proyecto, diseñado para fomentar la colaboración sin saturación de notificaciones:

### 5.1 Estructura de Canales de Texto
- Categoría: INFORMACIÓN GENERAL
  - `#📢-anuncios-oficiales`: Comunicados exclusivos del Project Manager (hitos, fechas de entrega, alertas de plataforma).
  - `#📌-recursos-y-links`: Enlaces permanentes a GitHub, Google Drive, tableros Kanban y documentación.
  - `#📜-reglas-del-equipo`: Criterios de aceptación (Definition of Done), acuerdos de convivencia y políticas de ramas en Git.
- Categoría: ENCUENTRO DIARIO & GESTIÓN
  - `#☕-general-daily`: Canal oficial para el registro asíncrono y seguimiento de la ceremonia Daily.
  - `#💡-ideas-y-sugerencias`: Espacio abierto para propuestas de mejora y debate de equipo.
- Categoría: DIMENSIONES DE TRABAJO
  - `#🧠-arquitectura-e-ia`: Discusión técnica entre Arquitectura, Backend e Inteligencia Artificial.
  - `#⚙️-backend-y-datos`: Coordinación de tareas de ingestión, parsing y almacenamiento.
  - `#🎨-frontend-y-ux`: Coordinación de interfaz de usuario, componentes Streamlit y maquetación.
  - `#🚀-devops-cloud-oci`: Administración de infraestructura OCI, credenciales y pruebas unitarias.

### 5.2 Canales de Voz
- `🔊 Sala de Reuniones (Daily)`: Canal principal para la sincronización diaria de 15 minutos.
- `🔊 Pair Programming 1`: Espacio para sesiones de programación en parejas y resolución técnica colaborativa.
- `🔊 Pair Programming 2`: Espacio de apoyo para pruebas, depuración e integración.

### 5.3 Acuerdos de Convivencia y Niveles de Servicio (SLA)
- Uso responsable de menciones: Se utilizarán etiquetas de rol (`@PM`, `@Arquitectura`, `@Backend`, `@Frontend`, `@DevOps`) y se evitará el uso indiscriminado de `@everyone`.
- Tiempo de respuesta asíncrona: Máximo 4 horas durante el horario diurno para consultas en canales temáticos.
- Cero acuerdos en mensajes privados: Cualquier decisión técnica o funcional debe quedar registrada en el canal de Discord correspondiente para conocimiento de todo el equipo.

---

## 6. CEREMONIA "DAILY" (ENCUENTRO DIARIO DEL EQUIPO)

La ceremonia **Daily** (adaptación de la Daily Scrum) constituye el punto de encuentro diario del equipo. No es una instancia de supervisión o reporte administrativo; es un espacio ágil de alineación, apoyo mutuo y desbloqueo operativo.

### 6.1 Parámetros de la Ceremonia
- Duración Máxima: 15 minutos estrictos (Timeboxed).
- Frecuencia: De lunes a viernes en horario acordado por el equipo (sugerido 20:00 UTC).
- Modalidad: Encuentro síncrono por voz en `🔊 Sala de Reuniones (Daily)` con registro paralelo en `#☕-general-daily`.
- Respaldo Asíncrono: Quienes no puedan conectarse por motivos laborales o personales publicarán sus 3 respuestas en `#☕-general-daily` antes del inicio de la sesión.

### 6.2 Las 3 Preguntas Clave Contextualizadas para NuevaMente
Cada participante interviene brevemente respondiendo:
1. ¿Qué tarea o avance completé ayer que contribuyó a los objetivos del Sprint en NuevaMente?
2. ¿Qué paquete de trabajo específico abordaré durante el día de hoy?
3. ¿Existe algún impedimento, bloqueo o duda técnica (en RAG, OCI, prompts, UI o Git) que requiera la ayuda de otro integrante o del Board?

### 6.3 Regla del "Parking Lot"
Si un debate técnico específico requiere mayor profundización y no compete a todos los asistentes, se detiene la conversación en la Daily y los involucrados pasan a un canal de Pair Programming para resolverlo sin extender los 15 minutos del resto del equipo.

---

## 7. PLAN DE GESTIÓN DE RIESGOS Y MITIGACIONES (RISK REGISTER)

El proyecto prioriza la continuidad operativa y la prevención de costos inesperados. A continuación se detallan las contingencias y sus estrategias:

### Riesgo R-01: Costos Involuntarios en la Nube de Oracle (OCI)
- Severidad: Crítica.
- Causa Potencial: Provisión errónea de instancias o almacenamiento fuera de la capa Always Free.
- Mitigación Preventiva: Configuración de Budgets en OCI con umbral de alerta en $0.01 USD. Creación de un compartimento exclusivo etiquetado para Always Free.
- Plan de Contingencia / Reacción: Destrucción inmediata del recurso mediante OCI CLI o consola web y activación del modo emulado local en el código.

### Riesgo R-02: Agotamiento de Cuotas en APIs de Inteligencia Artificial (Rate Limits HTTP 429)
- Severidad: Alta.
- Causa Potencial: Múltiples solicitudes consecutivas durante pruebas o la grabación de la demo en video.
- Mitigación Preventiva: Implementación de llamadas optimizadas con Gemini 1.5 Flash (capa gratuita de Google AI Studio), caché local de respuestas idénticas y reintentos con backoff exponencial.
- Plan de Contingencia / Reacción: Conmutación transparente en caliente a OpenAI (clave de respaldo) o ejecución mediante el generador heurístico estructurado offline incluido en el código base.

### Riesgo R-03: Alucinaciones o Desviaciones en el Contenido Didáctico Generado
- Severidad: Alta.
- Causa Potencial: Respuestas del LLM no respaldadas en la documentación técnica original.
- Mitigación Preventiva: Canalización RAG con fragmentación semántica contextual, temperatura baja (menor o igual a 0.3), instrucciones estrictas en los prompts y cálculo de puntuación de anclaje (grounding score).
- Plan de Contingencia / Reacción: La interfaz de usuario muestra una alerta destacada cuando el score de anclaje resulta inferior al 80%, impidiendo que el estudiante asuma como verídico un dato no respaldado.

### Riesgo R-04: Documentos Técnicos con Formatos Complejos o No Extraíbles
- Severidad: Media.
- Causa Potencial: PDFs protegidos, escaneados o con diseños en columnas cruzadas.
- Mitigación Preventiva: Motor de extracción dual con pypdf y pymupdf.
- Plan de Contingencia / Reacción: Disponibilidad de un área de texto plano en la interfaz Streamlit para pegar directamente el contenido si el archivo PDF falla.

### Riesgo R-05: Desconexión o Fallos Durante la Grabación del Video Demo
- Severidad: Media.
- Causa Potencial: Caídas de conexión a Internet durante la grabación de la demostración para YouTube.
- Mitigación Preventiva: Grabación estructurada por bloques modulares utilizando los 3 escenarios oficiales pre-cargados localmente en la aplicación.
- Plan de Contingencia / Reacción: Uso de respaldos locales pregrabados y edición modular del video.

---

## 8. MATRIZ DE ALTERNATIVAS TÉCNICAS (ENFOQUE FLEXIBLE Y NO DEFINITIVO)

Para asegurar que el desarrollo no se detenga ante limitaciones externas, se definen alternativas técnicas viables para cada módulo:

### Persistencia en la Nube (OCI Storage)
- Opción Primaria: OCI SDK para Python (`oci`) apuntando a buckets Always Free.
- Alternativa A: API de OCI compatible con Amazon S3 mediante la biblioteca `boto3`.
- Alternativa de Contingencia: Persistencia en réplica local (`data/oci_local_storage/`) con sincronización asíncrona posterior.

### Orquestación de Modelos de Lenguaje (LLMs)
- Opción Primaria: Google Gemini 1.5 Flash a través del SDK `google-genai` / `google-generativeai` (gratuito).
- Alternativa A: OpenAI `gpt-4o-mini` con structured output.
- Alternativa de Contingencia: Generador heurístico inteligente offline empaquetado en `src/llm/engine.py`.

### Almacén Vectorial (Vector Store)
- Opción Primaria: ChromaDB persistente en almacenamiento local.
- Alternativa A: FAISS CPU (`faiss-cpu`) en memoria con volcado a disco.
- Alternativa de Contingencia: Indexación por similitud de coseno directa sobre embeddings precalculados.

### Interfaz Interactiva de Usuario
- Opción Primaria: Streamlit desplegado localmente o en Streamlit Community Cloud.
- Alternativa A: Interfaz web interactiva construida en Gradio.
- Alternativa de Contingencia: API REST funcional construida con FastAPI y documentación automática en Swagger UI.

---

## 9. PLAN DEL PROYECTO EN 5 SPRINTS (STAGES PRINCE2 AGILE)

El cronograma del proyecto se distribuye en 5 Sprints semanales:

- **Sprint 1 (14 Sep – 20 Sep): Setup del Ecosistema y Contratos de Datos**
  Definición de gobierno, creación del repositorio Git, provisión de OCI Always Free, contratos Pydantic y suite de pruebas base.
- **Sprint 2 (21 Sep – 27 Sep): Ingestión de Documentos y Motor RAG Core**
  Extractores multiformato, cliente funcional de OCI Object Storage e indexación vectorial en ChromaDB.
- **Sprint 3 (28 Sep – 04 Oct): Orquestación Pedagógica y Salida JSON**
  Prompts pedagógicos por perfil (Bloom), validación estructurada JSON y persistencia en OCI.
- **Sprint 4 (05 Oct – 11 Oct): Interfaz Streamlit y 3 Escenarios Oficiales**
  Visualización interactiva (Flashcards, Quizzes con evaluación inmediata, Tutoriales) y verificación con los 3 manuales oficiales.
- **Sprint 5 (12 Oct – 18 Oct): Video Demo, Entregables y Demo Day**
  Grabación del video de 3 minutos para YouTube, cumplimiento de las 4 tareas en la plataforma No Country y presentación final.

---

## 10. CRITERIOS DE CALIDAD Y ACEPTACIÓN (QUALITY MANAGEMENT)

El MVP de NuevaMente será aceptado formalmente por el Project Board al cumplir los siguientes criterios de calidad:
- Ingestión validada en archivos PDF, Markdown y Texto plano sin errores de decodificación.
- Segmentación de documentos con solapamiento y generación de identificadores únicos por fragmento.
- Recuperación contextual RAG con índice de fidelidad a la fuente técnica documentada superior al 85%.
- Adaptación demostrada en al menos 2 perfiles diferentes y 2 formatos pedagógicos distintos sobre un mismo documento base.
- Esquema JSON de salida que cumple con los campos oficiales: status, metadatos, contenido_adaptado, evaluacion_calidad y almacenamiento_oci.
- Almacenamiento comprobado del archivo original y del JSON generado en OCI Object Storage Always Free.
- Interfaz gráfica operativa, fluida y con manejo de errores amigable para el usuario.
