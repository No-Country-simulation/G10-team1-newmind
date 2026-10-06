# DOCUMENTO DE INICIACIÓN Y GESTIÓN DEL PROYECTO (PID / PROJECT BRIEF)
## METODOLOGÍA PRINCE2 / PRINCE2 AGILE — PROYECTO NUEVAMENTE
### ENTREGABLE OFICIAL — TAREA 1: DOCUMENTACIÓN DEL PROYECTO (NO COUNTRY / HACKATHON ONE G10)

---

> ### AVISO FORMAL: CLÁUSULA DE "LETRA VIVA" (LIVING DOCUMENT)
> Este documento se formula bajo los principios de PRINCE2 Agile como una **"LETRA VIVA"**: está sujeto a refinamiento durante las cinco fases de gestión (Sprints). La revisión por parte de una junta colegiada es una propuesta de gobernanza; sus integrantes, acuerdos y aprobaciones requieren confirmación del equipo. El título histórico de «entregable oficial» no acredita que el texto se haya presentado en No Country.

---

## 1. ENLACES OFICIALES DEL PROYECTO (TAREA 1)

Los accesos siguientes corresponden a referencias del plan original; verificar su disponibilidad y vigencia antes de tratarlos como entregas oficiales:

- **Repositorio Oficial en GitHub:**
  https://github.com/mmorfe-engineer/nuevamente_g10_latam (dirección histórica; confirmar repositorio vigente).
- **Carpeta de Trabajo Compartida en Google Drive:**
  Carpeta remota: `NuevaMente_Hackathon_ONE_G10` (referencia histórica a briefing, metodología y código; acceso y contenidos no verificados).
- **Despliegue Local / Aplicación Web:**
  Con Docker Compose, interfaz en `http://localhost:5173`, API en `http://localhost:8000` y documentación interactiva en `http://localhost:8000/docs`. Son direcciones locales, no un despliegue público; `http://localhost:8501` y `./run_app.sh` eran referencias a Streamlit que no corresponden a la aplicación vigente.
- **Documentación de Requerimientos Oficiales ONE G10:**
  [Indicaciones del proyecto](HACKATHON_ONE_G10_INDICACIONES.md) (adaptación de los requisitos históricos; confirmar convocatoria vigente).
- **Estructura Desglosada de Trabajo (EDT en 5 Sprints):**
  [Plan de trabajo en cinco sprints](EDT_PLAN_DE_TRABAJO_5_SPRINTS.md) (plan, no certificado de ejecución).

---

## 2. DEFINICIÓN DEL PROYECTO (PROJECT DEFINITION)

### 2.1 Antecedentes (Background)
En EdTech, la documentación técnica, manuales de arquitectura y especificaciones crecen rápidamente. Los materiales densos dificultan el aprendizaje para perfiles diversos, desde principiantes hasta arquitectos y ejecutivos. Su adaptación manual requiere tiempo de especialistas y diseñadores instruccionales.

### 2.2 Objetivos del Proyecto (Project Objectives)
- Construir un MVP modular que ingiera documentos técnicos PDF, Markdown y texto plano. La API vigente admite estas extensiones con un máximo de 20 MB y requiere texto extraíble.
- Implementar RAG con segmentación y búsqueda vectorial en ChromaDB para fundamentar respuestas en fuentes; la recuperación no elimina por sí sola las alucinaciones.
- Adaptar el contenido mediante un motor LLM con instrucciones pedagógicas. El diseño multiagente o la aplicación formal de la Taxonomía de Bloom deben validarse antes de declararlos implementados.
- Generar JSON estructurado validado con Pydantic; la API FastAPI incluye el resultado oficial en `officialResponse` cuando el procesamiento finaliza.
- Disponer de una interfaz interactiva React/Vite conectada a la API FastAPI; Streamlit figuraba en el objetivo original, no es la interfaz vigente.
- Integrar persistencia de documentos originales y paquetes educativos mediante el cliente de OCI Object Storage, distinguiendo OCI real del modo emulado local. La operación real en Always Free debe verificarse.

### 2.3 Alcance del Proyecto (Project Scope)
- Ingestión de PDF, Markdown y TXT sin preprocesamiento manual cuando contienen texto extraíble; los PDF escaneados sin OCR quedan fuera del flujo actual.
- Parametrización de perfiles Principiante, Junior, Senior, Lider y Gestor (valores de la API; corresponden a los cuatro grupos pedagógicos previstos).
- Parametrización de Flashcards, Quiz, Tutorial, Resumen Ejecutivo y Guion; comprobar la interacción evaluable en la interfaz por separado de la generación de preguntas.
- Contextualización por nichos Fintech, Salud, E-commerce y General.
- Persistencia de origen y destino: el cliente prevé OCI y emulación local; demostrar operación real antes de atribuirla a Always Free.
- Validación de al menos tres escenarios reales o simulados como meta; no consta aquí evidencia de entrega de los tres.

### 2.4 Exclusiones del Alcance (Scope Exclusions)
- No se prevé contratar infraestructura con costos recurrentes fuera de la capa gratuita sin una decisión explícita del equipo.
- No se desarrollará una app nativa para móviles (iOS/Android) en este MVP.
- No se procesarán materiales protegidos por derechos de autor sin autorización.

### 2.5 Restricciones del Proyecto (Constraints)
- Restricción presupuestaria: objetivo histórico de infraestructura sin costos; no se dispone aquí de presupuesto aprobado ni comprobantes de consumo de OCI.
- Restricción temporal: plan original de cinco semanas entre el 14 de septiembre y el 18 de octubre de 2026; confirmar con la plataforma los plazos aprobados antes de presentarlos como límite oficial.
- Restricción de calidad: meta histórica de anclaje a fuentes de al menos 85%; el score actual procede de similitud de recuperación, no de una auditoría independiente de fidelidad.

### 2.6 Supuestos (Assumptions)
- Los integrantes necesitan conectividad y estaciones compatibles para desarrollar y probar los componentes.
- El uso de OCI real presupone una cuenta, namespace, buckets y credenciales válidas; sin ellos el cliente utiliza almacenamiento local emulado.
- El acceso a proveedores LLM y sus cuotas depende de la configuración de cada entorno; no se presupone disponibilidad gratuita universal.

---

## 3. CASO DE NEGOCIO (OUTLINE BUSINESS CASE)

### 3.1 Justificación
NuevaMente busca reducir el tiempo de elaboración de materiales didácticos técnicos y facilitar el aprendizaje de documentación compleja. La reducción concreta de semanas a segundos es una hipótesis que requiere medición en escenarios comparables.

### 3.2 Opciones Analizadas (Business Options)
- Opción 1: No hacer nada. Conservar la adaptación manual, con sus costos y cuellos de botella.
- Opción 2: IA genérica sin RAG. Evita indexar documentos, pero aumenta el riesgo de contenido no respaldado y dificulta la trazabilidad.
- Opción 3 (Seleccionada en el plan): RAG + LLM + salida tipada con opción de OCI Object Storage. La arquitectura vigente incorpora un cliente con emulación local; costo cero, fidelidad y eficacia pedagógica requieren comprobación, no se infieren del diseño.

### 3.3 Tolerancias del Proyecto (Project Tolerances)
- Tolerancia de costo: propuesta histórica de $0 USD de infraestructura; confirmar presupuesto, consumo y autorización antes de considerarla aprobada.
- Tolerancia de tiempo: propuesta original sin retrasos respecto de la semana 5; confirmar el plazo aplicable en No Country.
- Tolerancia de alcance: propuesta histórica de cubrir los ocho requisitos mínimos; revisar la rúbrica vigente y comprobar cada requisito con evidencia.

---

## 4. ESTRUCTURA DE GOBERNANZA Y EQUIPO (PRINCE2 MANAGEMENT TEAM)

La estructura siguiente recoge la distribución colegiada propuesta originalmente. Los nombres y responsabilidades no sustituyen la confirmación de roles por el equipo ni prueban aceptación formal de un Project Board.

### 4.1 Cúspide de Coordinación y Gobierno
- **MARTIN MORFE — Project Manager (rol propuesto en el plan original)**
  Facilitación de ceremonias, coordinación de hitos, tolerancias y entregables de No Country; confirmar atribución actual y quién efectuó cada envío.

### 4.2 Project Board Colegiado y Democrático por Dimensiones
El plan propone referentes por dimensión y decisiones consensuadas; la composición efectiva y su mandato requieren ratificación:

- **Dimensión 1: Arquitectura de Software y Solución**
  Referente propuesto: **Esteban Guillermo Morales Velazquez (Solution Architect)**. Custodia de arquitectura, integración RAG, patrones, calidad técnica y deuda técnica.
- **Dimensión 2: Backend e Ingestión de Datos**
  Referente propuesto: **Juan David Villegas Anaya (Backend Developer)**. Extractores PDF/Markdown/TXT, sanitización y segmentación; la aplicación expone la carga mediante FastAPI.
- **Dimensión 3: Full Stack y Orquestación de Inteligencia Artificial**
  Referentes propuestos: **Harol Benjamin Medina Zárate y Heiner Jair Godoy Zamora (Full Stack Developers)**. Prompts pedagógicos, motor LLM, validación Pydantic e integración. Existe un motor único; no atribuirle un grafo multiagente.
- **Dimensión 4: Frontend, Experiencia de Usuario y Formatos Pedagógicos**
  Referentes propuestos: **Cristian Contreras y Diana Castaño (Frontend Developers)**. Interfaz React/Vite, visualización de Flashcards, Quiz y Tutoriales; el plan original citaba Streamlit.
- **Dimensión 5: DevOps, Infraestructura Cloud OCI y Aseguramiento de Calidad**
  Referente propuesto: **Ivan Hernandez (DevOps Engineer)**. Seguridad de credenciales, pruebas y despliegue; verificar aprovisionamiento y uso real de OCI antes de declararlos realizados.

---

## 5. PLAN DE COMUNICACIONES INTEGRAL POR DISCORD

Discord fue propuesto como espacio de trabajo centralizado para colaborar sin saturar las notificaciones. Los canales, acuerdos y SLA siguientes son propuestas históricas; confirmar que estén adoptados antes de usarlos como política vigente.

### 5.1 Estructura de Canales de Texto
- Categoría: INFORMACIÓN GENERAL
  - `#📢-anuncios-oficiales`: Hitos, fechas y alertas de la plataforma.
  - `#📌-recursos-y-links`: GitHub, Drive, tablero y documentación.
  - `#📜-reglas-del-equipo`: Definition of Done, convivencia y políticas de ramas.
- Categoría: ENCUENTRO DIARIO & GESTIÓN
  - `#☕-general-daily`: Registro asíncrono y seguimiento del Daily.
  - `#💡-ideas-y-sugerencias`: Propuestas y debate del equipo.
- Categoría: DIMENSIONES DE TRABAJO
  - `#🧠-arquitectura-e-ia`: Arquitectura, backend e IA.
  - `#⚙️-backend-y-datos`: Ingestión, parsing y almacenamiento.
  - `#🎨-frontend-y-ux`: Interfaz React/Vite y componentes.
  - `#🚀-devops-cloud-oci`: Infraestructura, credenciales y pruebas.

### 5.2 Canales de Voz
- `🔊 Sala de Reuniones (Daily)`: Sincronización diaria de hasta 15 minutos.
- `🔊 Pair Programming 1`: Sesiones de programación en parejas y resolución técnica.
- `🔊 Pair Programming 2`: Pruebas, depuración e integración.

### 5.3 Acuerdos de Convivencia y Niveles de Servicio (SLA)
- Uso responsable de menciones: etiquetas de rol (`@PM`, `@Arquitectura`, `@Backend`, `@Frontend`, `@DevOps`) y evitar el uso indiscriminado de `@everyone`.
- Tiempo de respuesta asíncrona: máximo propuesto de cuatro horas diurnas para consultas temáticas; confirmar horario y aprobación antes de exigirlo.
- Cero acuerdos en mensajes privados: registrar decisiones técnicas y funcionales en canales accesibles al equipo, si este acuerdo fue adoptado.

---

## 6. CEREMONIA "DAILY" (ENCUENTRO DIARIO DEL EQUIPO)

El Daily propuesto es un espacio de alineación y desbloqueo, no de supervisión administrativa. Su celebración efectiva depende de los acuerdos del equipo.

### 6.1 Parámetros de la Ceremonia
- Duración máxima propuesta: 15 minutos (timebox).
- Frecuencia propuesta: lunes a viernes, en horario acordado; 20:00 UTC era una sugerencia, no una cita confirmada.
- Modalidad propuesta: voz en `🔊 Sala de Reuniones (Daily)` y registro en `#☕-general-daily`.
- Respaldo asíncrono: quien no pueda asistir responde en `#☕-general-daily` antes de la sesión, sujeto a acuerdo del equipo.

### 6.2 Las 3 Preguntas Clave Contextualizadas para NuevaMente
Cada participante respondería brevemente:
1. ¿Qué avance completé ayer en relación con los objetivos del Sprint?
2. ¿Qué paquete de trabajo abordaré hoy?
3. ¿Qué impedimento o duda en RAG, OCI, prompts, interfaz o Git necesita apoyo del equipo?

### 6.3 Regla del "Parking Lot"
Si un debate requiere mayor profundidad y no compete a todos, los involucrados lo trasladan a una sesión específica de Pair Programming para no extender el Daily.

---

## 7. PLAN DE GESTIÓN DE RIESGOS Y MITIGACIONES (RISK REGISTER)

Los riesgos son previsiones del plan; las mitigaciones propuestas requieren verificación operativa:

### Riesgo R-01: Costos Involuntarios en la Nube de Oracle (OCI)
- Severidad: Crítica.
- Causa potencial: Provisión fuera de los límites gratuitos.
- Mitigación preventiva: Definir compartimento, revisar límites Always Free y configurar alertas de presupuesto; no consta aquí una alerta de $0.01 USD ya configurada.
- Plan de contingencia / reacción: Detener y eliminar recursos no autorizados tras confirmar permisos y consecuencias; usar modo local emulado sin describirlo como OCI real.

### Riesgo R-02: Agotamiento de Cuotas en APIs de Inteligencia Artificial (Rate Limits HTTP 429)
- Severidad: Alta.
- Causa potencial: Solicitudes reiteradas durante pruebas o grabación.
- Mitigación preventiva: Reducir llamadas y aplicar control de cuota o reintentos según el proveedor configurado; no se acredita aquí caché de respuestas ni backoff implementados.
- Plan de contingencia / reacción: Revisar cuotas y credenciales; el motor intenta Gemini, luego Grok y después OpenAI, cada uno solo si dispone de su clave configurada; si ninguno obtiene una respuesta válida, utiliza un generador heurístico de demostración. Identificar ese resultado como simulación, no como salida de un LLM ni como conmutación transparente equivalente.

### Riesgo R-03: Alucinaciones o Desviaciones en el Contenido Didáctico Generado
- Severidad: Alta.
- Causa potencial: Salidas no sustentadas en el documento original.
- Mitigación preventiva: Recuperación RAG y revisión de fragmentos fuente; el score de anclaje refleja similitud de recuperación y no certifica exactitud factual ni claridad pedagógica.
- Plan de contingencia / reacción: Revisar manualmente la adaptación y su fuente cuando el anclaje sea bajo; la API marca `approved` a partir de 0.8, pero ello no demuestra un bloqueo automático ni una alerta universal en la interfaz.

### Riesgo R-04: Documentos Técnicos con Formatos Complejos o No Extraíbles
- Severidad: Media.
- Causa potencial: PDF protegidos, escaneados o con columnas complejas.
- Mitigación preventiva: Validar extracción de PDF/Markdown/TXT y rechazar documentos sin texto extraíble; OCR no forma parte del flujo acreditado.
- Plan de contingencia / reacción: Solicitar una versión con texto extraíble o un TXT/MD del mismo contenido; el área de pegado directo de Streamlit era parte del plan original, no de la interfaz vigente.

### Riesgo R-05: Desconexión o Fallos Durante la Grabación del Video Demo
- Severidad: Media.
- Causa potencial: Pérdida de conexión durante la demostración.
- Mitigación preventiva: Preparar tres escenarios reproducibles y comprobar su ejecución y el modo de almacenamiento antes de grabar; no constan tres escenarios precargados como entrega.
- Plan de contingencia / reacción: Utilizar grabaciones locales y edición modular, indicando claramente qué fue demostrado realmente.

---

## 8. MATRIZ DE ALTERNATIVAS TÉCNICAS (ENFOQUE FLEXIBLE Y NO DEFINITIVO)

Las opciones que siguen distinguen implementación vigente de alternativas del plan, sin presentar estas últimas como capacidades entregadas:

### Persistencia en la Nube (OCI Storage)
- Opción primaria: Cliente Python `oci` para Object Storage con configuración válida; confirmar el modo real mediante la respuesta de salud y los objetos persistidos.
- Alternativa A: Compatibilidad S3 mediante `boto3` como propuesta, no integración verificada.
- Alternativa de contingencia: Persistencia local en `newmind-learning-backend/data/oci_local_storage/`; el cliente utiliza esa ruta cuando opera en modo emulado o falla la carga, sin sincronización asíncrona garantizada.

### Orquestación de Modelos de Lenguaje (LLMs)
- Opción primaria: Motor único de adaptación que intenta Gemini si su clave está configurada; verificar disponibilidad y cuota en una ejecución real.
- Alternativa A: Si Gemini no produce una respuesta válida, el motor intenta Grok con su clave configurada y después OpenAI con la suya; las pruebas con simulaciones no acreditan una llamada externa real a Grok. Verificar cuotas y comportamiento con credenciales autorizadas.
- Alternativa de contingencia: El motor incluye un generador heurístico offline en `newmind-learning-backend/llm/engine.py`; sus respuestas son demostrativas, no prueban generación por LLM ni fidelidad a la fuente.

### Almacén Vectorial (Vector Store)
- Opción primaria: ChromaDB persistente en disco local para embeddings y búsqueda.
- Alternativa A: FAISS CPU en memoria con volcado a disco, propuesta no implementada como reemplazo acreditado.
- Alternativa de contingencia: Búsqueda por similitud de coseno sobre embeddings precalculados, propuesta sujeta a implementación.

### Interfaz Interactiva de Usuario
- Opción primaria: React/Vite conectado a FastAPI; Docker Compose expone localmente la interfaz en `http://localhost:5173` y la API en `http://localhost:8000`.
- Alternativa A: Gradio como propuesta histórica no integrada en la interfaz actual.
- Alternativa de contingencia: API REST FastAPI con esquema interactivo en `http://localhost:8000/docs`; no sustituye todas las interacciones pedagógicas de la interfaz.

---

## 9. PLAN DEL PROYECTO EN 5 SPRINTS (STAGES PRINCE2 AGILE)

El cronograma original prevé cinco semanas; son fechas de planificación y no constancia de hitos cumplidos ni de plazos aprobados por No Country:

- **Sprint 1 (14 Sep – 20 Sep): Setup del Ecosistema y Contratos de Datos**
  Gobierno, repositorio Git, propuesta de OCI Always Free, contratos Pydantic y pruebas de base; validar la provisión de recursos aparte.
- **Sprint 2 (21 Sep – 27 Sep): Ingestión de Documentos y Motor RAG Core**
  Extractores, cliente de OCI Object Storage e indexación ChromaDB; verificar si el cliente operó en modo OCI o emulado.
- **Sprint 3 (28 Sep – 04 Oct): Orquestación Pedagógica y Salida JSON**
  Adaptación por perfiles, validación JSON y persistencia; el motor único no acredita un sistema multiagente.
- **Sprint 4 (05 Oct – 11 Oct): Interfaz React/Vite y 3 Escenarios Oficiales**
  Visualización interactiva y verificación propuesta con tres materiales; confirmar los escenarios realmente ejecutados.
- **Sprint 5 (12 Oct – 18 Oct): Video Demo, Entregables y Demo Day**
  Grabación, cuatro tareas de plataforma y presentación previstos; no se acredita aquí su realización ni una fecha oficial confirmada.

---

## 10. CRITERIOS DE CALIDAD Y ACEPTACIÓN (QUALITY MANAGEMENT)

La aceptación formal por un Project Board es un objetivo sujeto a confirmación; cada criterio necesita evidencia propia:
- Ingestión de PDF, Markdown y TXT con texto extraíble y manejo de errores de decodificación, tamaño y archivos vacíos.
- Segmentación con solapamiento e identificadores de fragmentos; comprobar trazabilidad de los fragmentos utilizados.
- Recuperación contextual con meta histórica de anclaje del 85%; el score de similitud no es una verificación factual independiente.
- Demostración del mismo documento en al menos dos perfiles y dos formatos; documentar entradas y salidas.
- JSON oficial con `status`, `metadatos`, `contenido_adaptado`, `evaluacion_calidad` y `almacenamiento_oci`, disponible como `officialResponse` en el recurso de adaptación completada.
- Almacenamiento comprobado de archivo original y JSON en OCI Object Storage Always Free; un estado de emulación local no satisface la comprobación de OCI real.
- Interfaz React/Vite operativa con FastAPI, estados de carga y manejo de errores; verificar experiencia de usuario en los escenarios definidos.
