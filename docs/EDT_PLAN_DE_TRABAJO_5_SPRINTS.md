# Estructura Desglosada de Trabajo (EDT / WBS) — Proyecto NuevaMente
## Hackathon No Country — Oracle Next Education (ONE G10)
**Marco Metodológico:** Scrum Ágil · 5 Sprints (1 semana por Sprint)

**Fecha de Inicio propuesta:** 14 de septiembre de 2026

**Fecha de Finalización (Demo Day) propuesta:** 18 de octubre de 2026; confirmar fechas aprobadas por la plataforma.

---

## 📌 Dimensiones Técnicas y de Gestión (Áreas de Trabajo)

1. **Gestión de Proyecto & Producto (PM & Scrum):** Alineación, seguimiento de hitos, ceremonias y entregables en plataforma.
2. **Arquitectura & Nube (OCI Always Free):** Diseño del sistema, provisión propuesta en Oracle Cloud y seguridad de credenciales; distinguir OCI real de emulación local.
3. **Ingestión & Pipeline RAG (Data & Retrieval):** Extracción PDF/Markdown/TXT, segmentación, embeddings y base vectorial ChromaDB.
4. **IA Generativa & Orquestación Pedagógica (LLM & Prompts):** Motor de adaptación, prompts, validación JSON y control de contenido no respaldado; LangGraph multiagente queda como diferencial.
5. **Frontend & Experiencia de Usuario (UI React/Vite):** Carga, parametrización, seguimiento y visualización de resultados mediante API FastAPI (no Streamlit).
6. **DevOps, Calidad & Pruebas (QA & Testing):** Pruebas, documentación, configuración y eventual despliegue público.

---

## 📅 Matriz de Planificación por Sprints

```text
===================================================================================================
SPRINT 1 (14 Sep - 20 Sep) │ Configuración de Entorno, Arquitectura Base y Contratos de Datos
SPRINT 2 (21 Sep - 27 Sep) │ Ingestión de Documentos, Persistencia OCI o Local y Motor RAG Core
SPRINT 3 (28 Sep - 04 Oct) │ Motor LLM, Adaptación Pedagógica y Validación JSON Pydantic
SPRINT 4 (05 Oct - 11 Oct) │ Interfaz React/Vite, Integración E2E y 3 Escenarios de Prueba
SPRINT 5 (12 Oct - 18 Oct) │ Diferenciales (LangGraph/Anki), Video Demo y Entregables de Plataforma
===================================================================================================
```

Las fechas son las del plan original, no certifican ejecución ni constituyen plazos aprobados sin confirmación. Las casillas siguientes son paquetes previstos; permanecerán sin marcar hasta que existan evidencias de cumplimiento.

---

## 🚀 Desglose Detallado por Sprint

### SPRINT 1: Setup del Ecosistema, Arquitectura y Definición de Contratos
**Periodo propuesto:** 14 al 20 de septiembre de 2026

**Meta del Sprint (Sprint Goal):** Establecer repositorio, políticas del equipo, modelo de datos de entrada/salida e infraestructura base local y, si se confirma, OCI.

#### 1. Gestión de Proyecto & Producto
- [ ] **EDT-1.1.1** Configurar tablero Kanban/Scrum (GitHub Projects o Trello) con columnas de ciclo de vida; confirmar tablero utilizado.
- [ ] **EDT-1.1.2** Acordar cadencia de Dailies, Sprint Planning y Sprint Review semanal con el equipo.
- [ ] **EDT-1.1.3** Formalizar alcance del MVP y Definition of Done (DoD); no atribuir aprobación sin acta o acuerdo.

#### 2. Arquitectura & Nube (OCI)
- [ ] **EDT-1.2.1** Diseñar y validar el diagrama integral (C4 / Mermaid) para React/Vite, FastAPI, RAG y almacenamiento.
- [ ] **EDT-1.2.2** Configurar compartimento y políticas IAM en OCI Always Free si existe acceso autorizado; no se acredita provisión real aquí.
- [ ] **EDT-1.2.3** Preparar los dos buckets de OCI Object Storage y verificar su existencia real antes de dar este paquete por cumplido:
  - `nuevamente-documentos-origen` (documentos originales).
  - `nuevamente-contenidos-educativos` (artefactos JSON); los directorios homónimos locales no son buckets OCI.
- [ ] **EDT-1.2.4** Gestionar API Signing Key (`.pem`), fingerprint, tenancy OCID y user OCID sin incorporar secretos al repositorio.

#### 3. Ingestión & Pipeline RAG
- [ ] **EDT-1.3.1** Elegir bibliotecas de extracción PDF, Markdown y TXT (`pypdf` y cargadores disponibles); verificar con archivos representativos.
- [ ] **EDT-1.3.2** Definir tamaño inicial `chunk_size=1000` y solapamiento `chunk_overlap=150`; son valores configurados por defecto, sujetos a pruebas.
- [ ] **EDT-1.3.3** Seleccionar y medir embeddings (`all-MiniLM-L6-v2` por defecto o alternativa evaluada).

#### 4. IA Generativa & Orquestación
- [ ] **EDT-1.4.1** Definir esquemas Pydantic para contrato de dominio y transporte: API de carga de archivo y `AdaptationCreateRequest` con `documentId`, `profile`, `format`, `industry`, `detailLevel`; salida `AdaptationResponse` con `officialResponse` al completar.
- [ ] **EDT-1.4.2** Diseñar prompts pedagógicos para los perfiles del plan, evaluando si la Taxonomía de Bloom se refleja efectivamente en su contenido.
- [ ] **EDT-1.4.3** Configurar Gemini u OpenAI y probar el orden de intento del motor; sin respuesta de proveedores utiliza un generador heurístico de demostración, que no acredita uso de LLM.

#### 5. Frontend & UI
- [ ] **EDT-1.5.1** Diseñar el recorrido Carga → Parametrización → Procesamiento → Visualización con estados de error y espera.
- [ ] **EDT-1.5.2** Establecer componentes de React/Vite en `newmind-learning-frontend/src/` en lugar del directorio histórico `ui/components/` de Streamlit.

#### 6. DevOps, Calidad & Testing
- [ ] **EDT-1.6.1** Configurar repositorio GitHub y verificar políticas de ramas antes de declarar protección de `main` o existencia de `develop`.
- [ ] **EDT-1.6.2** Mantener plantillas de entorno, `.gitignore` y dependencias del backend/frontend; no publicar credenciales OCI.
- [ ] **EDT-1.6.3** Preparar pruebas `pytest` del backend y dependencias locales; confirmar resultados en una ejecución concreta.

---

### SPRINT 2: Ingestión Documental, Persistencia OCI y Motor RAG Core
**Periodo propuesto:** 21 al 27 de septiembre de 2026

**Meta del Sprint (Sprint Goal):** Extraer texto, almacenar documentos y recuperar contexto semántico desde ChromaDB; verificar por separado la conexión real a OCI.

#### 1. Gestión de Proyecto & Producto
- [ ] **EDT-2.1.1** Revisar el backlog del Sprint 2 con el equipo y registrar decisiones.
- [ ] **EDT-2.1.2** Recopilar tres documentos de prueba PDF, Markdown y TXT de temas OCI/Cloud con permisos de uso.

#### 2. Arquitectura & Nube (OCI)
- [ ] **EDT-2.2.1** Implementar y probar `newmind-learning-backend/storage/oci_client.py` con el SDK `oci` y modo emulado local explícito.
- [ ] **EDT-2.2.2** Cargar archivos originales mediante `POST /api/v1/documents`; validar en qué modo se guardaron. La descarga desde el bucket no forma parte del contrato REST de documentos actual.
- [ ] **EDT-2.2.3** Definir manejo de errores OCI y fallback local; no presumir reintentos o sincronización posterior sin implementación verificada.

#### 3. Ingestión & Pipeline RAG
- [ ] **EDT-2.3.1** Extraer PDF, Markdown y TXT mediante `newmind-learning-backend/ingestion/loaders.py`; rechazar PDF sin texto extraíble.
- [ ] **EDT-2.3.2** Validar codificación, texto vacío y normalización; probar archivos complejos sin prometer OCR.
- [ ] **EDT-2.3.3** Segmentar con `newmind-learning-backend/ingestion/chunker.py` e identificadores por fragmento; verificar metadatos de página y origen cuando existan.
- [ ] **EDT-2.3.4** Persistir índice ChromaDB con `newmind-learning-backend/rag/vector_store.py` en el directorio configurado.
- [ ] **EDT-2.3.5** Recuperar fragmentos mediante `newmind-learning-backend/rag/retriever.py` y comprobar relevancia por documento.

#### 4. IA Generativa & Orquestación
- [ ] **EDT-2.4.1** Probar recuperación Top-K antes de inyectar el contexto al motor de adaptación.
- [ ] **EDT-2.4.2** Ajustar ventana de contexto y comprobar fidelidad, sin asumir que la similitud elimina alucinaciones.

#### 5. Frontend & UI
- [ ] **EDT-2.5.1** Implementar carga con arrastrar y soltar mediante `newmind-learning-frontend/src/widgets/document-uploader/DocumentUploader.jsx`; admitir `.pdf`, `.md` y `.txt` hasta 20 MB.
- [ ] **EDT-2.5.2** Proporcionar selectores de adaptación en la interfaz React/Vite:
  - Perfil (Principiante, Junior, Senior, Lider, Gestor; valores de la API).
  - Formato (Tutorial, Flashcards, Quiz, Resumen Ejecutivo, Guion).
  - Nicho (Fintech, Salud, E-commerce, General).

#### 6. DevOps, Calidad & Testing
- [ ] **EDT-2.6.1** Probar extracción de PDF con tablas, columnas y ausencia de texto extraíble.
- [ ] **EDT-2.6.2** Probar conectividad con OCI real solo en un entorno autorizado y con credenciales; pruebas de emulación local no certifican conexión cloud.
- [ ] **EDT-2.6.3** Comprobar consistencia de embeddings, índices ChromaDB y fragmentos recuperados.

---

### SPRINT 3: Orquestación LLM, Adaptación Pedagógica y Salida JSON
**Periodo propuesto:** 28 de septiembre al 4 de octubre de 2026

**Meta del Sprint (Sprint Goal):** Generar adaptación con contexto RAG, validar JSON y persistir resultados; diferenciar OCI real de almacenamiento local.

#### 1. Gestión de Proyecto & Producto
- [ ] **EDT-3.1.1** Evaluar avance de mitad del proyecto y mitigar riesgos de deuda técnica.
- [ ] **EDT-3.1.2** Acordar criterios de evaluación pedagógica sobre la rúbrica vigente, sin atribuir su aprobación a No Country.

#### 2. Arquitectura & Nube (OCI)
- [ ] **EDT-3.2.1** Serializar el JSON generado y guardarlo con el cliente OCI; comprobar si el destino es bucket real o `data/oci_local_storage/`.
- [ ] **EDT-3.2.2** Generar identificadores de objetos (`objeto_id`) únicos; `contenido-vcn-principiante-flashcards-001.json` es un ejemplo, no prueba de un objeto persistido.

#### 3. Ingestión & Pipeline RAG
- [ ] **EDT-3.3.1** Evaluar filtrado por documento o capítulo para evitar mezclar fragmentos de documentos diferentes; no declararlo activo sin prueba específica.
- [ ] **EDT-3.3.2** Calcular y revisar la métrica de anclaje; actualmente representa similitud media de recuperación, no una evaluación independiente de veracidad.

#### 4. IA Generativa & Orquestación
- [ ] **EDT-3.4.1** Utilizar `newmind-learning-backend/llm/engine.py` como motor único de adaptación con proveedor configurado; LangGraph multiagente no forma parte del flujo vigente.
- [ ] **EDT-3.4.2** Revisar plantillas pedagógicas por perfil:
  - **Principiante:** Analogías y explicaciones accesibles sin alterar datos técnicos.
  - **Líder Técnico / Arquitecto:** Decisiones, seguridad, compromisos de diseño y métricas.
  - **Gestor / Ejecutivo:** Impacto de negocio, riesgos y síntesis.
- [ ] **EDT-3.4.3** Validar generación y estructura de los formatos:
  - **Flashcards:** Frente, dorso y pistas didácticas.
  - **Quiz:** Opciones, respuesta y justificación; evaluar la retroalimentación interactiva por separado.
  - **Tutorial:** Prerrequisitos, pasos y comprobaciones.
- [ ] **EDT-3.4.4** Validar respuesta estructurada con Pydantic y gestionar fallos de salida; no atribuir un `Pydantic Output Parser` específico sin verificarlo.

#### 5. Frontend & UI
- [ ] **EDT-3.5.1** Conectar el botón de generación React/Vite con `POST /api/v1/adaptations` y consultar el estado; `st.spinner` pertenecía al plan Streamlit.
- [ ] **EDT-3.5.2** Mostrar contenido JSON y evaluación; identificar el alcance limitado de los criterios calculados a partir del mismo score.

#### 6. DevOps, Calidad & Testing
- [ ] **EDT-3.6.1** Probar esquemas Pydantic y contrato API de adaptaciones con los tests disponibles; registrar resultados al ejecutar la suite.
- [ ] **EDT-3.6.2** Probar regresiones con proveedores y parámetros LLM realmente configurados; no presuponer cobertura de temperaturas.

---

### SPRINT 4: Interfaz Interactiva, Integración E2E y 3 Escenarios de Prueba
**Periodo propuesto:** 5 al 11 de octubre de 2026

**Meta del Sprint (Sprint Goal):** Integrar React/Vite y FastAPI y documentar tres escenarios reproducibles; no dar la integración por validada sin ejecución.

#### 1. Gestión de Proyecto & Producto
- [ ] **EDT-4.1.1** Planificar grabación de video y confirmar responsables del guion.
- [ ] **EDT-4.1.2** Comprobar cada requisito de la evaluación con evidencia; el 100% es una meta, no un resultado acreditado.

#### 2. Arquitectura & Nube (OCI)
- [ ] **EDT-4.2.1** Revisar consumo y límites Always Free en consola OCI si se utiliza OCI real; no inferir costo cero desde el modo local.
- [ ] **EDT-4.2.2** Opcional / diferencial: Evaluar instancia OCI Compute Always Free; no se acredita VM ni despliegue.

#### 3. Ingestión & Pipeline RAG
- [ ] **EDT-4.3.1** Probar documentos extensos (más de 30 páginas) y registrar límites de tiempo y memoria.
- [ ] **EDT-4.3.2** Ajustar índices y evaluar caché de embeddings; no dar por existente una caché sin prueba.

#### 4. IA Generativa & Orquestación
- [ ] **EDT-4.4.1** Demostrar tres escenarios sobre documentos con contenido autorizado:
  - **Escenario 1:** Manual OCI VCN → Principiante → Flashcards.
  - **Escenario 2:** Mismo manual OCI VCN → perfil técnico (valor API `Lider`) → Tutorial.
  - **Escenario 3:** Documentación de API o microservicio → Gestor → Resumen Ejecutivo.

#### 5. Frontend & UI
- [ ] **EDT-4.5.1** Verificar componente de Flashcards con volteo visual y accesibilidad.
- [ ] **EDT-4.5.2** Verificar Quiz interactivo y retroalimentación inmediata, diferenciándola de una nota de anclaje RAG.
- [ ] **EDT-4.5.3** Ofrecer descarga de JSON estructurado y evaluar copia al portapapeles; comprobar cada función antes de anunciarla.
- [ ] **EDT-4.5.4** Pulir estilos React/Vite; `ui/assets/styles.css` era una ruta prevista para Streamlit, no para la interfaz actual.

#### 6. DevOps, Calidad & Testing
- [ ] **EDT-4.6.1** Ejecutar pruebas unitarias y de integración backend (`pytest -v`) y registrar resultado; la existencia de tests no implica ejecución satisfactoria.
- [ ] **EDT-4.6.2** Preparar despliegue público de React/Vite y FastAPI solo si se autoriza y configura; no existe enlace público confirmado aquí.

---

### SPRINT 5: Diferenciales, Video Demo y Entregables Finales
**Periodo propuesto:** 12 al 18 de octubre de 2026

**Meta del Sprint (Sprint Goal):** Preparar cierre de código, video, entregables y presentación; fechas y envíos sujetos a confirmación.

#### 1. Gestión de Proyecto & Producto
- [ ] **EDT-5.1.1** Cargar Tarea 1 (documentación Markdown) en No Country; confirmar contenido realmente enviado.
- [ ] **EDT-5.1.2** Cargar Tarea 2 (enlace al video YouTube) en la plataforma; verificar URL pública.
- [ ] **EDT-5.1.3** Seleccionar y enviar Tarea 3 (herramientas y tecnologías) según uso comprobado.
- [ ] **EDT-5.1.4** Registrar y comprobar Tarea 4 (enlaces del proyecto); localhost no sustituye un despliegue público.
- [ ] **EDT-5.1.5** Ensayar pitch y presentación para el Demo Day, si se confirma su fecha.

#### 2. Arquitectura & Nube (OCI)
- [ ] **EDT-5.2.1** Obtener evidencias de Object Storage real (buckets y objetos) si se configuró OCI; capturas del almacenamiento local no acreditan OCI.
- [ ] **EDT-5.2.2** Documentar arquitectura final de React/Vite, FastAPI, motor RAG y modo de almacenamiento real.

#### 3. IA Generativa & Recursos Opcionales (Diferenciales)
- [ ] **EDT-5.3.1** Diferencial 1: Evaluar exportación de Flashcards a Anki (.csv); no afirmar que ya existe.
- [ ] **EDT-5.3.2** Diferencial 2: Evaluar LangGraph (Investigador RAG → Pedagógico → Crítico); el motor actual es único, no un grafo de agentes.

#### 4. Frontend & UI
- [ ] **EDT-5.4.1** Revisar interfaz React/Vite, errores visuales y textos de ayuda.
- [ ] **EDT-5.4.2** Evaluar sección «Acerca de NuevaMente» y confirmar créditos antes de publicarlos.

#### 5. DevOps, Calidad & Testing
- [ ] **EDT-5.5.1** Acordar Code Freeze en `main` con el equipo; no suponer que ya ocurrió.
- [ ] **EDT-5.5.2** Etiquetar versión de lanzamiento solo tras aceptación; `v1.0.0-mvp` era una etiqueta prevista, no una versión certificada.
- [ ] **EDT-5.5.3** Actualizar `README.md` con enlaces verificados a demo y video cuando existan; este paquete no implica editarlo ahora.

#### 6. Multimedia & Comunicación
- [ ] **EDT-5.6.1** Grabar aplicación React/Vite y API FastAPI con un guion cercano a tres minutos, mostrando resultados reales.
- [ ] **EDT-5.6.2** Editar video con subtítulos y placas según acuerdos de publicación y derechos de uso.
- [ ] **EDT-5.6.3** Publicar en YouTube como «Público» o «No listado» si la plataforma lo admite y verificar enlace y resolución.
