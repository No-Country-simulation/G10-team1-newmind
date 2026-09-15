# Estructura Desglosada de Trabajo (EDT / WBS) — Proyecto NuevaMente
## Hackathon No Country — Oracle Next Education (ONE G10)
**Marco Metodológico:** Scrum Ágil · 5 Sprints (1 semana por Sprint)  
**Fecha de Inicio:** 14 de Septiembre de 2026  
**Fecha de Finalización (Demo Day):** 18 de Octubre de 2026  

---

## 📌 Dimensiones Técnicas y de Gestión (Áreas de Trabajo)

1. **Gestión de Proyecto & Producto (PM & Scrum):** Alineación, seguimiento de hitos, ceremonias y entregables en plataforma.
2. **Arquitectura & Nube (OCI Always Free):** Diseño del sistema, provisión de recursos en Oracle Cloud y seguridad de credenciales.
3. **Ingestión & Pipeline RAG (Data & Retrieval):** Extracción multiformato, chunking jerárquico, embeddings y base de datos vectorial.
4. **IA Generativa & Orquestación Pedagógica (LLM & Prompts):** Modelado de prompts pedagógicos, validación de esquemas JSON estructurados y control de alucinaciones.
5. **Frontend & Experiencia de Usuario (UI Streamlit):** Interfaces reactivas, flujos de carga, parametrización didáctica y renderizado de resultados.
6. **DevOps, Calidad & Pruebas (QA & Testing):** Automatización de pruebas unitarias, integración continua, documentación y despliegue.

---

## 📅 Matriz de Planificación por Sprints

```text
===================================================================================================
SPRINT 1 (14 Sep - 20 Sep) │ Configuración de Entorno, Arquitectura Base y Contratos de Datos
SPRINT 2 (21 Sep - 27 Sep) │ Ingestión de Documentos, Persistencia OCI y Motor RAG Core
SPRINT 3 (28 Sep - 04 Oct) │ Orquestación LLM, Adaptación Pedagógica y Validación JSON Pydantic
SPRINT 4 (05 Oct - 11 Oct) │ Interfaz Interactiva Streamlit, Integración E2E y 3 Escenarios de Prueba
SPRINT 5 (12 Oct - 18 Oct) │ Diferenciales (LangGraph/Anki), Video Demo y Entregables de Plataforma
===================================================================================================
```

---

## 🚀 Desglose Detallado por Sprint

### SPRINT 1: Setup del Ecosistema, Arquitectura y Definición de Contratos
**Periodo:** 14 de Septiembre al 20 de Septiembre de 2026  
**Meta del Sprint (Sprint Goal):** Establecer el repositorio, las políticas de trabajo del equipo, el modelo de datos de entrada/salida y la infraestructura base local y en OCI.

#### 1. Gestión de Proyecto & Producto
- [ ] **EDT-1.1.1** Setup del tablero Kanban/Scrum (GitHub Projects o Trello) con columnas de ciclo de vida.
- [ ] **EDT-1.1.2** Definición de la cadencia de ceremonias: Dailies asíncronas, Sprint Planning y Sprint Review semanal.
- [ ] **EDT-1.1.3** Formalización del alcance del MVP y acuerdo de Definition of Done (DoD) para el equipo.

#### 2. Arquitectura & Nube (OCI)
- [ ] **EDT-1.2.1** Diseño y validación del diagrama de arquitectura integral (C4 / Mermaid) del sistema.
- [ ] **EDT-1.2.2** Creación y configuración del Compartimento y Políticas IAM en el tenancy de OCI Always Free.
- [ ] **EDT-1.2.3** Provisión de los dos Buckets obligatorios en OCI Object Storage:
  - `nuevamente-documentos-origen` (almacén de documentos originales).
  - `nuevamente-contenidos-educativos` (almacén de artefactos JSON generados).
- [ ] **EDT-1.2.4** Generación de API Signing Key de OCI (`.pem`), obtención de fingerprint, tenancy OCID y user OCID.

#### 3. Ingestión & Pipeline RAG
- [ ] **EDT-1.3.1** Selección de bibliotecas base para parsing documental (`pypdf`, `pymupdf`, `markdown`).
- [ ] **EDT-1.3.2** Definición de la estrategia de chunking inicial: tamaño de fragmento (`chunk_size=1000`) y solapamiento (`chunk_overlap=150`).
- [ ] **EDT-1.3.3** Selección y benchmarking del modelo de embeddings local o API (`all-MiniLM-L6-v2` o Google Embeddings).

#### 4. IA Generativa & Orquestación
- [ ] **EDT-1.4.1** Definición formal de los esquemas de datos Pydantic para entrada (`AdaptationRequest`) y salida (`AdaptationResponse`).
- [ ] **EDT-1.4.2** Redacción inicial de los system prompts pedagógicos basados en la taxonomía de Bloom y los 4 perfiles requeridos.
- [ ] **EDT-1.4.3** Configuración del adaptador cliente para Google Gemini API y OpenAI API como fallback.

#### 5. Frontend & UI
- [ ] **EDT-1.5.1** Wireframes y especificación del flujo de usuario (User Journey): Carga -> Parametrización -> Procesamiento -> Visualización.
- [ ] **EDT-1.5.2** Estructura base de componentes modulares en Streamlit (`ui/components/`).

#### 6. DevOps, Calidad & Testing
- [ ] **EDT-1.6.1** Setup del repositorio GitHub con ramas protegidas y branching model (`main`, `develop`, `feature/*`).
- [ ] **EDT-1.6.2** Configuración de plantillas `.env.example`, `.gitignore` y estandarización del archivo `requirements.txt`.
- [ ] **EDT-1.6.3** Estructuración de la suite de pruebas unitarias (`pytest`) y validación de entornos virtuales locales.

---

### SPRINT 2: Ingestión Documental, Persistencia OCI y Motor RAG Core
**Periodo:** 21 de Septiembre al 27 de Septiembre de 2026  
**Meta del Sprint (Sprint Goal):** Tener el pipeline de extracción de texto operativo, conectividad activa con OCI Object Storage y búsqueda semántica indexada en ChromaDB.

#### 1. Gestión de Proyecto & Producto
- [ ] **EDT-2.1.1** Revisión y ajuste del backlog del Sprint 2 con el equipo.
- [ ] **EDT-2.1.2** Selección y recopilación de los 3 documentos técnicos oficiales de prueba (PDF, Markdown y Texto) sobre temas reales de OCI/Cloud.

#### 2. Arquitectura & Nube (OCI)
- [ ] **EDT-2.2.1** Implementación del módulo de cliente OCI (`src/storage/oci_client.py`) utilizando `oci-sdk`.
- [ ] **EDT-2.2.2** Función de subida y descarga de archivos de entrada en el bucket de origen de OCI.
- [ ] **EDT-2.2.3** Manejo de reintentos, tiempos de espera y control de excepciones para la API de OCI Object Storage.

#### 3. Ingestión & Pipeline RAG
- [ ] **EDT-2.3.1** Implementación de los extractores de contenido en `src/ingestion/loaders.py` para PDF, Markdown y TXT.
- [ ] **EDT-2.3.2** Implementación de sanitización de texto: eliminación de caracteres no imprimibles, normalización de saltos de línea y cabeceras.
- [ ] **EDT-2.3.3** Desarrollo del segmentador (`src/ingestion/chunker.py`) con metadatos contextuales (página, sección, título de origen).
- [ ] **EDT-2.3.4** Configuración del Vector Store ChromaDB (`src/rag/vector_store.py`) con persistencia local/directorio.
- [ ] **EDT-2.3.5** Implementación del mecanismo de indexación vectorial y búsqueda por similitud coseno (`src/rag/retriever.py`).

#### 4. IA Generativa & Orquestación
- [ ] **EDT-2.4.1** Pruebas preliminares de recuperación de contexto (Top-K Chunks) para alimentar los prompts generativos.
- [ ] **EDT-2.4.2** Afinamiento de la ventana de contexto para evitar saturación de tokens y asegurar fidelidad a la fuente técnica.

#### 5. Frontend & UI
- [ ] **EDT-2.5.1** Desarrollo del componente de carga de archivos (`ui/components/file_uploader.py`) con soporte arrastrar y soltar (drag & drop).
- [ ] **EDT-2.5.2** Barra lateral (Sidebar) con selectores de:
  - Perfil del Destinatario (Principiante, Junior/Mid, Arquitecto, Ejecutivo).
  - Formato Pedagógico (Tutorial, Flashcards, Quiz, Resumen Ejecutivo, Guion de Video).
  - Nicho de Aplicación (Fintech, Salud, E-commerce, General).

#### 6. DevOps, Calidad & Testing
- [ ] **EDT-2.6.1** Pruebas unitarias para extracción de PDFs con tablas y texto en varias columnas.
- [ ] **EDT-2.6.2** Pruebas de integración de conectividad con OCI Object Storage (`tests/test_oci_storage.py`).
- [ ] **EDT-2.6.3** Validación de consistencia en embeddings generados e índices de ChromaDB.

---

### SPRINT 3: Orquestación LLM, Adaptación Pedagógica y Salida JSON
**Periodo:** 28 de Septiembre al 04 de Octubre de 2026  
**Meta del Sprint (Sprint Goal):** Generar contenido educativo adaptado a partir del contexto RAG, validando estrictamente el esquema JSON y almacenando los resultados en OCI.

#### 1. Gestión de Proyecto & Producto
- [ ] **EDT-3.1.1** Evaluación de avance de mitad de proyecto (Mid-term Health Check) y mitigación de riesgos de deuda técnica.
- [ ] **EDT-3.1.2** Coordinación de criterios de evaluación pedagógica con base en la rúbrica del Hackathon ONE.

#### 2. Arquitectura & Nube (OCI)
- [ ] **EDT-3.2.1** Implementación de la función de serialización y persistencia automática del JSON resultante en el bucket `nuevamente-contenidos-educativos`.
- [ ] **EDT-3.2.2** Generación de identificadores únicos de objeto (`objeto_id`) con nomenclatura estándar (ej.: `contenido-vcn-principiante-flashcards-001.json`).

#### 3. Ingestión & Pipeline RAG
- [ ] **EDT-3.3.1** Optimización del retrieval mediante filtrado por metadatos (ej.: filtrar por documento o capítulo específico).
- [ ] **EDT-3.3.2** Implementación de métricas de anclaje a la fuente (*source grounding score*) para mitigar alucinaciones del modelo.

#### 4. IA Generativa & Orquestación
- [ ] **EDT-3.4.1** Implementación del motor orquestador en `src/llm/engine.py` con integración a Google Gemini 1.5 Flash / Pro.
- [ ] **EDT-3.4.2** Implementación de plantillas pedagógicas especializadas:
  - Plantilla para **Principiante**: Foco en analogías del mundo real, explicaciones conceptuales intuitivas y pistas didácticas.
  - Plantilla para **Líder Técnico / Arquitecto**: Foco en trade-offs de arquitectura, mejores prácticas de diseño, seguridad y métricas.
  - Plantilla para **Gestor / Ejecutivo**: Foco en impacto de negocio, ROI, gobernanza y resúmenes de alto nivel.
- [ ] **EDT-3.4.3** Generación de los formatos de salida:
  - Formato **Flashcards**: pares frente/dorso y pistas didácticas.
  - Formato **Quiz Interactivo**: preguntas de opción múltiple, respuesta correcta y justificación pedagógica fundamentada en el texto.
  - Formato **Guía Paso a Paso (Tutorial)**: prerrequisitos, pasos secuenciales y comprobaciones.
- [ ] **EDT-3.4.4** Configuración de Pydantic Output Parser para asegurar un JSON 100% válido y libre de texto markdown circundante.

#### 5. Frontend & UI
- [ ] **EDT-3.5.1** Integración del disparador de generación ("Generar Contenido Educativo") con feedback visual mediante `st.spinner` y progreso.
- [ ] **EDT-3.5.2** Visualizador preliminar del JSON estructurado y métricas de calidad en pantalla.

#### 6. DevOps, Calidad & Testing
- [ ] **EDT-3.6.1** Pruebas automatizadas de validación del esquema JSON con Pydantic (`tests/test_llm_schemas.py`).
- [ ] **EDT-3.6.2** Pruebas de regresión con diferentes temperaturas y parámetros de generación en el LLM.

---

### SPRINT 4: Interfaz Interactiva, Integración E2E y 3 Escenarios de Prueba
**Periodo:** 05 de Octubre al 11 de Octubre de 2026  
**Meta del Sprint (Sprint Goal):** Contar con la aplicación completamente conectada de extremo a extremo, interfaz pulida y los 3 escenarios obligatorios validados y documentados.

#### 1. Gestión de Proyecto & Producto
- [ ] **EDT-4.1.1** Planificación de la grabación del Video Demo y asignación de roles para el guion.
- [ ] **EDT-4.1.2** Verificación del cumplimiento del Checklist de Evaluación del Hackathon (100% de requisitos mínimos completados).

#### 2. Arquitectura & Nube (OCI)
- [ ] **EDT-4.2.1** Auditoría de consumo Always Free en la consola de OCI para asegurar cero costos generados.
- [ ] **EDT-4.2.2** Opcional / Diferencial: Provisión de una máquina virtual (Compute Instance VM.Standard.E2.1.Micro) en OCI Always Free para despliegue.

#### 3. Ingestión & Pipeline RAG
- [ ] **EDT-4.3.1** Pruebas de estrés con documentos técnicos extensos (más de 30 páginas).
- [ ] **EDT-4.3.2** Ajuste de índices y caché de embeddings para acelerar tiempos de respuesta.

#### 4. IA Generativa & Orquestación
- [ ] **EDT-4.4.1** Validación de la adaptación pedagógica para los 3 escenarios oficiales de demostración:
  - **Escenario 1:** Manual técnico de OCI VCN -> Perfil *Principiante* -> Formato *Flashcards*.
  - **Escenario 2:** Mismo manual técnico de OCI VCN -> Perfil *Arquitecto de Soluciones* -> Formato *Tutorial Paso a Paso*.
  - **Escenario 3:** Documentación de API o microservicio -> Perfil *Gestor / Ejecutivo* -> Formato *Resumen Ejecutivo (TL;DR)*.

#### 5. Frontend & UI
- [ ] **EDT-4.5.1** Componente interactivo de **Flashcards con volteo visual** (CSS flip card).
- [ ] **EDT-4.5.2** Componente de **Quiz Interactivo con evaluación inmediata**: El usuario selecciona opciones y recibe retroalimentación instantánea.
- [ ] **EDT-4.5.3** Botones de exportación: Descarga de JSON estructurado y copia al portapapeles en un clic.
- [ ] **EDT-4.5.4** Inyección de estilos CSS profesionales (`ui/assets/styles.css`) acorde a la paleta de NuevaMente.

#### 6. DevOps, Calidad & Testing
- [ ] **EDT-4.6.1** Ejecución de la suite completa de pruebas unitarias e integración de extremo a extremo (`pytest -v`).
- [ ] **EDT-4.6.2** Despliegue de la aplicación en Streamlit Community Cloud o instancia de OCI con variables de entorno aseguradas.

---

### SPRINT 5: Diferenciales, Video Demo y Entregables Finales
**Periodo:** 12 de Octubre al 18 de Octubre de 2026  
**Meta del Sprint (Sprint Goal):** Congelar código (Code Freeze), producir el video demo de alta calidad, completar los 4 entregables en la plataforma y presentar en el Demo Day.

#### 1. Gestión de Proyecto & Producto
- [ ] **EDT-5.1.1** Carga de la **Tarea 1 (Documentación en Markdown)** en la plataforma No Country.
- [ ] **EDT-5.1.2** Carga de la **Tarea 2 (Enlace del Video Demo en YouTube)** en la plataforma.
- [ ] **EDT-5.1.3** Selección y envío de la **Tarea 3 (Herramientas y Tecnologías)** en la plataforma.
- [ ] **EDT-5.1.4** Registro y verificación de la **Tarea 4 (Enlaces del Proyecto)** en la plataforma.
- [ ] **EDT-5.1.5** Ensayo general del pitch y presentación en vivo para el Demo Day.

#### 2. Arquitectura & Nube (OCI)
- [ ] **EDT-5.2.1** Exportación de evidencias de OCI Object Storage (capturas del bucket y objetos JSON persistidos para la entrega).
- [ ] **EDT-5.2.2** Generación de informe de arquitectura final en el repositorio.

#### 3. IA Generativa & Recursos Opcionales (Diferenciales)
- [ ] **EDT-5.3.1** Diferencial 1: Exportación directa a formato de tarjetas **Anki (.csv)** para estudio espaciado.
- [ ] **EDT-5.3.2** Diferencial 2 (Si el tiempo lo permite): Implementación de grafo de decisión con **LangGraph** (Agente Investigador RAG -> Agente Pedagógico -> Agente Crítico/Evaluador).

#### 4. Frontend & UI
- [ ] **EDT-5.4.1** Pulido final de interfaz gráfica, corrección de bugs visuales y textos de ayuda (tooltips).
- [ ] **EDT-5.4.2** Pestaña de "Acerca de NuevaMente" con créditos y enlaces del equipo.

#### 5. DevOps, Calidad & Testing
- [ ] **EDT-5.5.1** Congelamiento formal del código fuente (Code Freeze) en rama `main`.
- [ ] **EDT-5.5.2** Etiquetado de versión de lanzamiento en Git (`git tag -a v1.0.0-mvp -m "Release MVP Hackathon ONE G10"`).
- [ ] **EDT-5.5.3** Actualización final de `README.md` con enlaces activos de la demo y del video.

#### 6. Multimedia & Comunicación
- [ ] **EDT-5.6.1** Grabación de las tomas de pantalla de la aplicación en funcionamiento siguiendo el guion de 3 minutos.
- [ ] **EDT-5.6.2** Locución y edición de video con subtítulos, música de fondo y placas de presentación.
- [ ] **EDT-5.6.3** Subida a YouTube en modo "Público" o "No Listado" en resolución 1080p.
