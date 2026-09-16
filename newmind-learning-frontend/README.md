<div align="center">

# 🧠 NuevaMente — Frontend

**Sistema Inteligente de Adaptación y Generación de Contenido Educativo**

*Programa ONE · Grupo 10 · Proyecto 1*

<br/>

[![React](https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-8-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev)
[![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-3-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)](https://tailwindcss.com)
[![React Router](https://img.shields.io/badge/React_Router-7-CA4245?style=for-the-badge&logo=reactrouter&logoColor=white)](https://reactrouter.com)
[![Axios](https://img.shields.io/badge/Axios-1.x-5A29E4?style=for-the-badge&logo=axios&logoColor=white)](https://axios-http.com)

<br/>

> Interfaz visual del sistema NuevaMente. Permite cargar documentos técnicos, configurar la adaptación educativa y visualizar el contenido generado por el pipeline multiagente.

<br/>

</div>

---

## 📋 Tabla de contenidos

- [📖 Descripción general](#-descripción-general)
- [🚀 Instalación y arranque](#-instalación-y-arranque)
- [🏗️ Arquitectura — Feature-Sliced Design](#️-arquitectura--feature-sliced-design)
- [📁 Estructura de carpetas](#-estructura-de-carpetas)
- [⚙️ Capa `app`](#️-capa-app)
- [📄 Capa `pages`](#-capa-pages)
- [🧩 Capa `widgets`](#-capa-widgets)
- [🗂️ Capa `entities`](#️-capa-entities)
- [📦 Capa `shared`](#-capa-shared)
- [🔄 Flujo de usuario](#-flujo-de-usuario)
- [🔌 Conexión con el backend](#-conexión-con-el-backend)
- [📐 Convenciones de código](#-convenciones-de-código)
- [🎨 Diseño y estilos](#-diseño-y-estilos)

---

## 📖 Descripción general

El frontend de NuevaMente es la capa visual del sistema. No contiene lógica de IA — su responsabilidad es la experiencia del usuario.

<br/>

<table>
<tr>
<td width="50%">

**✅ Responsabilidades**

- Cargar y validar documentos (PDF, MD, TXT)
- Configurar la adaptación (perfil, formato, nicho, detalle)
- Visualizar el pipeline multiagente en tiempo real
- Renderizar el contenido generado por formato
- Gestionar el historial de adaptaciones con filtros

</td>
<td width="50%">

**❌ Lo que NO hace**

- No tiene lógica de IA
- No se comunica con Gemini, ChromaDB ni PostgreSQL
- No accede al sistema de archivos directamente
- No conoce los detalles internos del backend

</td>
</tr>
</table>

> **Nota:** El frontend funciona completamente con datos simulados mientras el backend no esté disponible. Ver [Conexión con el backend](#-conexión-con-el-backend).

---

## 🚀 Instalación y arranque

### Requisitos previos

- Node.js **18** o superior
- npm **9** o superior

### Pasos

```bash
# 1. Instalar dependencias
npm install

# 2. Crear el archivo de entorno
cp .env.example .env

# 3. Configurar la URL del backend en .env
VITE_API_URL=http://localhost:8000
```

### Comandos disponibles

<br/>

<table>
<thead>
<tr>
<th>Comando</th>
<th>Descripción</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>npm run dev</code></td>
<td>Servidor de desarrollo con hot reload en <code>localhost:5173</code></td>
</tr>
<tr>
<td><code>npm run build</code></td>
<td>Build de producción optimizado en <code>dist/</code></td>
</tr>
<tr>
<td><code>npm run preview</code></td>
<td>Sirve el build de producción localmente para verificarlo</td>
</tr>
<tr>
<td><code>npm run lint</code></td>
<td>Ejecuta el linter (Oxlint) sobre todos los archivos</td>
</tr>
</tbody>
</table>

---

## 🏗️ Arquitectura — Feature-Sliced Design

El proyecto sigue **Feature-Sliced Design (FSD)**, una metodología de arquitectura por capas. La regla central es que **una capa solo puede importar desde capas inferiores**, nunca de las superiores.

<br/>

```
┌──────────────────────────────────────────────────────────────┐
│   app          Configuración global, providers y router      │
├──────────────────────────────────────────────────────────────┤
│   pages        Pantallas completas — una por ruta            │
├──────────────────────────────────────────────────────────────┤
│   widgets      Bloques funcionales complejos                  │
├──────────────────────────────────────────────────────────────┤
│   entities     Representación visual de objetos del dominio  │
├──────────────────────────────────────────────────────────────┤
│   shared       UI base, hooks, API client y utilidades       │
└──────────────────────────────────────────────────────────────┘
          ↑ cada capa solo importa desde las que están debajo
```

<br/>

<table>
<thead>
<tr>
<th>Situación</th>
<th>¿Permitido?</th>
</tr>
</thead>
<tbody>
<tr>
<td>Una <code>page</code> importa un <code>widget</code></td>
<td>✅ Correcto</td>
</tr>
<tr>
<td>Un <code>widget</code> importa algo de <code>shared</code></td>
<td>✅ Correcto</td>
</tr>
<tr>
<td>Un <code>widget</code> importa algo de <code>pages</code></td>
<td>❌ Rompe la arquitectura</td>
</tr>
<tr>
<td>Un <code>entity</code> importa un <code>widget</code></td>
<td>❌ Rompe la arquitectura</td>
</tr>
</tbody>
</table>

---

## 📁 Estructura de carpetas

```
src/
│
├── App.jsx                              Componente raíz: layout (Sidebar + área principal)
├── main.jsx                             Punto de entrada: monta React en el DOM
│
├── app/
│   ├── providers/index.jsx              BrowserRouter y futuros providers globales
│   ├── router/index.jsx                 Definición de las 4 rutas de la aplicación
│   └── styles/globals.css              Tailwind, fuente Inter y clases CSS reutilizables
│
├── pages/
│   ├── dashboard/DashboardPage.jsx      /          — Inicio, stats y adaptaciones recientes
│   ├── new-adaptation/
│   │   └── NewAdaptationPage.jsx        /new       — Carga de documento y configuración
│   ├── result/ResultPage.jsx            /result/:id — Pipeline en vivo y resultado final
│   └── history/HistoryPage.jsx          /history   — Historial con filtros
│
├── widgets/
│   ├── adaptation-form/
│   │   └── AdaptationForm.jsx           Formulario multi-paso (perfil→formato→nicho→detalle)
│   ├── content-viewer/
│   │   └── ContentViewer.jsx            Visualizador del contenido generado por formato
│   ├── document-uploader/
│   │   └── DocumentUploader.jsx         Zona drag-and-drop para cargar archivos
│   └── generation-status/
│       └── GenerationStatus.jsx         Pipeline multiagente animado en tiempo real
│
├── entities/
│   ├── adaptation/ui/AdaptationCard.jsx Tarjeta resumen de una adaptación
│   └── document/ui/DocumentCard.jsx     Tarjeta resumen de un documento
│
└── shared/
    ├── api/index.js                     Cliente Axios y todos los endpoints del backend
    ├── hooks/
    │   ├── useApi.js                    Hook genérico para llamadas async con loading/error
    │   └── useLocalStorage.js           Estado sincronizado con localStorage
    ├── types/index.js                   Tipos JSDoc del dominio y constantes de opciones
    ├── ui/
    │   ├── Alert.jsx                    Alert · EmptyState · ScoreRing
    │   ├── Badge.jsx                    Etiquetas pill con 7 variantes de color
    │   ├── Button.jsx                   Botón con 5 variantes, 3 tamaños y estado loading
    │   ├── Card.jsx                     Card · CardHeader
    │   ├── Input.jsx                    Input · Select con label, hint y error
    │   ├── Sidebar.jsx                  Barra lateral fija con navegación principal
    │   └── Spinner.jsx                  Spinner · PageLoader · Skeleton
    └── utils/index.js                   cn, formatDate, formatFileSize, truncate, etc.
```

---

## ⚙️ Capa `app`

Configura la aplicación antes de que se renderice cualquier pantalla.

<br/>

<details>
<summary><strong>app/providers/index.jsx</strong></summary>
<br/>

Envuelve la app en `BrowserRouter` para habilitar la navegación. Es el lugar donde agregar futuros providers globales como autenticación, React Query o sistema de tema.

</details>

<details>
<summary><strong>app/router/index.jsx</strong></summary>
<br/>

Define las rutas de la aplicación con React Router v7.

<br/>

<table>
<thead>
<tr><th>Ruta</th><th>Componente</th><th>Descripción</th></tr>
</thead>
<tbody>
<tr><td><code>/</code></td><td><code>DashboardPage</code></td><td>Inicio del sistema</td></tr>
<tr><td><code>/new</code></td><td><code>NewAdaptationPage</code></td><td>Crear nueva adaptación</td></tr>
<tr><td><code>/result/:id</code></td><td><code>ResultPage</code></td><td>Ver resultado de una adaptación</td></tr>
<tr><td><code>/history</code></td><td><code>HistoryPage</code></td><td>Historial de adaptaciones</td></tr>
<tr><td><code>*</code></td><td>Redirect a <code>/</code></td><td>Cualquier ruta no reconocida</td></tr>
</tbody>
</table>

</details>

<details>
<summary><strong>app/styles/globals.css</strong></summary>
<br/>

- Importa la fuente **Inter** desde Google Fonts (pesos 300–800)
- Inicializa Tailwind con `@tailwind base/components/utilities`
- Define el tema oscuro como base (`bg-slate-950`)
- Declara clases utilitarias reutilizables: `.btn-primary`, `.input-field`, `.label`, `.page-title`, `.glass-card`, `.gradient-text`

</details>

---

## 📄 Capa `pages`

Una página por ruta. Orquestan widgets y entities pero no contienen lógica de UI reutilizable.

<br/>

### `DashboardPage` — `/`

Pantalla de inicio y primer punto de contacto del usuario.

<br/>

<table>
<thead>
<tr><th>Sección</th><th>Contenido</th><th>Datos</th></tr>
</thead>
<tbody>
<tr><td>Hero</td><td>Título del sistema + botón "Nueva Adaptación"</td><td>—</td></tr>
<tr><td>Stats</td><td>4 tarjetas: docs cargados, adaptaciones, formatos, score Critic</td><td><code>MOCK_STATS</code></td></tr>
<tr><td>Recientes</td><td>Últimas 3 adaptaciones con <code>AdaptationCard</code></td><td><code>MOCK_RECENT_ADAPTATIONS</code></td></tr>
<tr><td>Inicio rápido</td><td>Accesos directos a crear y ver historial</td><td>—</td></tr>
<tr><td>Demos</td><td>Los 3 casos de demo del proyecto</td><td><code>DEMO_CASES</code></td></tr>
</tbody>
</table>

<br/>

**Sub-componentes:** `StatCard` · `DemoCase`

---

### `NewAdaptationPage` — `/new`

Flujo de creación en dos pasos secuenciales.

<br/>

<table>
<thead>
<tr><th>Paso</th><th>Widget usado</th><th>Descripción</th></tr>
</thead>
<tbody>
<tr>
<td><strong>1 — Cargar documento</strong></td>
<td><code>DocumentUploader</code></td>
<td>Arrastrá o seleccioná un archivo. Se valida localmente y se sube al backend. Habilita el paso 2 al completar.</td>
</tr>
<tr>
<td><strong>2 — Configurar</strong></td>
<td><code>AdaptationForm</code></td>
<td>Selección de perfil, formato, nicho y nivel de detalle. Al confirmar navega a <code>/result/:id</code>.</td>
</tr>
</tbody>
</table>

<br/>

**Hooks internos:** `useDocumentUpload()` · `handleGenerate()`

---

### `ResultPage` — `/result/:id`

Muestra el resultado. Se comporta distinto según el estado de la adaptación.

<br/>

<table>
<thead>
<tr><th>Estado</th><th>Qué muestra</th></tr>
</thead>
<tbody>
<tr><td><code>pending</code> · <code>processing</code></td><td>Widget <code>GenerationStatus</code> con el pipeline animado agente por agente</td></tr>
<tr><td><code>completed</code></td><td>Widget <code>ContentViewer</code> con el contenido generado + evaluación del Critic</td></tr>
<tr><td><code>failed</code></td><td>Banner de error con botón para reintentar</td></tr>
</tbody>
</table>

<br/>

**Hook interno:** `usePipelineSimulation()` — avanza un agente cada 1.8s. Reemplazar con polling a `adaptationsApi.getStatus(id)`.

**Sub-componentes:** `PageHeader` · `AdaptationMeta`

---

### `HistoryPage` — `/history`

Lista de todas las adaptaciones con filtros client-side.

<br/>

<table>
<thead>
<tr><th>Filtro</th><th>Tipo</th><th>Opciones</th></tr>
</thead>
<tbody>
<tr><td>Búsqueda</td><td>Texto libre</td><td>Título del documento</td></tr>
<tr><td>Perfil</td><td>Selector</td><td>Principiante · Junior · Lider · Gestor</td></tr>
<tr><td>Formato</td><td>Selector</td><td>Flashcards · Tutorial · Quiz · Resumen Ejecutivo · Guion</td></tr>
<tr><td>Estado</td><td>Selector</td><td>completed · processing · pending · failed</td></tr>
</tbody>
</table>

<br/>

**Hook interno:** `useHistoryFilters()` — centraliza los 4 estados de filtro y expone el array `filtered` ya procesado.

---

## 🧩 Capa `widgets`

Bloques de UI complejos con lógica propia. Cada widget tiene una carpeta y un único archivo `.jsx`.

<br/>

### `AdaptationForm`

Wizard de 4 pasos para configurar la adaptación.

<br/>

<table>
<thead>
<tr><th>Paso</th><th>Pregunta</th><th>Opciones</th></tr>
</thead>
<tbody>
<tr><td>① Perfil</td><td>¿Quién recibe el contenido?</td><td>Principiante · Junior · Lider · Gestor</td></tr>
<tr><td>② Formato</td><td>¿Qué tipo de contenido?</td><td>Flashcards · Tutorial · Quiz · Resumen Ejecutivo · Guion</td></tr>
<tr><td>③ Nicho</td><td>¿Cuál es el sector?</td><td>General · Fintech · Salud · E-commerce</td></tr>
<tr><td>④ Detalle</td><td>¿Qué nivel de profundidad?</td><td>Básico · Intermedio · Didáctico · Detallado</td></tr>
</tbody>
</table>

<br/>

**Props:**

```js
onSubmit(values)   // { profile, format, industry, detailLevel }
loading            // boolean — spinner en el botón final durante la generación
```

**Sub-componentes:** `StepIndicator` · `OptionGrid` · `ProfileStep` · `FormatStep` · `IndustryStep` · `DetailStep`

---

### `ContentViewer`

Renderiza el contenido generado según el formato de la adaptación.

<br/>

<table>
<thead>
<tr><th>Formato</th><th>Qué renderiza</th></tr>
</thead>
<tbody>
<tr><td><strong>Flashcards</strong></td><td>Grid 2 columnas — concepto, pregunta, respuesta y fuente por tarjeta</td></tr>
<tr><td><strong>Tutorial</strong></td><td>Introducción → pasos numerados con bloques de código → conclusión</td></tr>
<tr><td><strong>Resumen Ejecutivo</strong></td><td>Resumen → puntos clave con bullets → riesgos en ámbar</td></tr>
<tr><td><strong>Quiz</strong></td><td>Preguntas con opciones A/B/C/D — respuesta correcta en verde + justificación</td></tr>
<tr><td><strong>Guion</strong></td><td>JSON formateado (vista provisional hasta definir el schema)</td></tr>
</tbody>
</table>

<br/>

Siempre incluye el `ScoreRing` con el score del Critic y el desglose de los 4 criterios de evaluación.

**Sub-componentes:** `FlashcardsView` · `TutorialView` · `ExecutiveSummaryView` · `QuizView` · `GuionView` · `EvaluationBreakdown`

---

### `DocumentUploader`

Zona de carga con drag-and-drop. Valida localmente antes de llamar al backend.

<br/>

<table>
<thead>
<tr><th>Estado</th><th>Borde</th><th>Mensaje</th></tr>
</thead>
<tbody>
<tr><td>Idle</td><td>Punteado gris</td><td>"Arrastrá o hacé clic para subir"</td></tr>
<tr><td>Dragging</td><td>Punteado brand</td><td>"Suelta el archivo aquí"</td></tr>
<tr><td>Success</td><td>Verde</td><td>"¡Archivo cargado correctamente!"</td></tr>
<tr><td>Error</td><td>Rojo</td><td>Mensaje de error específico</td></tr>
</tbody>
</table>

<br/>

**Validaciones locales:** extensión (`.pdf` · `.md` · `.txt`) y tamaño (≤ 20 MB)

**Props:**

```js
onFileSelect(file)  // llamado cuando el archivo pasa validación local
uploading           // boolean — deshabilita la zona y muestra spinner
error               // string — error externo del backend
success             // boolean — marca la zona como exitosa
```

---

### `GenerationStatus`

Visualiza el pipeline de 5 agentes en tiempo real.

<br/>

<table>
<thead>
<tr><th>#</th><th>Agente</th><th>Responsabilidad</th></tr>
</thead>
<tbody>
<tr><td>①</td><td><strong>Orchestrator Agent</strong></td><td>Analiza la solicitud y define la ruta</td></tr>
<tr><td>②</td><td><strong>RAG Researcher Agent</strong></td><td>Recupera fragmentos relevantes del documento</td></tr>
<tr><td>③</td><td><strong>Context/Profile Agent</strong></td><td>Adapta al perfil con instrucciones pedagógicas</td></tr>
<tr><td>④</td><td><strong>Educational Generator</strong></td><td>Genera el contenido educativo estructurado</td></tr>
<tr><td>⑤</td><td><strong>Critic Agent</strong></td><td>Evalúa calidad, fidelidad y coherencia</td></tr>
</tbody>
</table>

<br/>

<table>
<thead>
<tr><th>Estado del paso</th><th>Ícono</th><th>Estilo visual</th></tr>
</thead>
<tbody>
<tr><td><code>done</code></td><td>✅ verde</td><td>Opacidad reducida</td></tr>
<tr><td><code>active</code></td><td>⏳ spinner brand</td><td>Fondo brand resaltado</td></tr>
<tr><td><code>idle</code></td><td>○ gris</td><td>Muy transparente</td></tr>
<tr><td><code>error</code></td><td>⚠️ rojo</td><td>Fondo rojo tenue</td></tr>
</tbody>
</table>

<br/>

**Props:**

```js
status          // 'pending' | 'processing' | 'completed' | 'failed'
currentAgent    // 'orchestrator' | 'researcher' | 'context' | 'generator' | 'critic'
iteration       // número de iteración del Critic (default: 0)
maxIterations   // límite de iteraciones (default: 3)
```

---

## 🗂️ Capa `entities`

Representaciones visuales de los objetos del dominio. Solo muestran datos, sin lógica de negocio.

<br/>

### `AdaptationCard`

Tarjeta compacta de una adaptación. Se usa en el dashboard y en el historial.

**Muestra:** título del documento · badges de perfil/formato/industria · estado con color semántico · fecha · score del Critic

**Accesibilidad:** `role="button"` · `tabIndex` · soporte de teclado (`Enter`) · `focus ring`

**Props:**

```js
adaptation    // objeto Adaptation
onClick()     // función opcional — si se pasa, la tarjeta es clickeable
```

---

### `DocumentCard`

Tarjeta compacta de un documento. También exporta `DocumentTypeIcon` para uso independiente.

**Muestra:** ícono por tipo (📄 PDF · `</>` MD · 📃 TXT) · título · badge del tipo · tamaño · fecha

**Props:**

```js
document        // objeto Document
onSelect(doc)   // función opcional — habilita modo selección
selected        // boolean — muestra checkmark brand
```

---

## 📦 Capa `shared`

Código reutilizable sin lógica de negocio. Importable desde cualquier capa.

<br/>

### `shared/ui/` — Sistema de diseño

<table>
<thead>
<tr><th>Componente</th><th>Variantes / Props clave</th><th>Descripción</th></tr>
</thead>
<tbody>
<tr>
<td><code>Button</code></td>
<td><code>primary · secondary · ghost · danger · success</code><br/><code>sm · md · lg</code> · <code>loading</code></td>
<td>Con <code>loading=true</code> muestra spinner y deshabilita automáticamente</td>
</tr>
<tr>
<td><code>Card</code></td>
<td><code>glass</code> · <code>hover</code></td>
<td>Contenedor surface con glassmorphism y efecto hover opcional</td>
</tr>
<tr>
<td><code>CardHeader</code></td>
<td><code>title</code> · <code>action</code></td>
<td>Fila con título izquierda y acción derecha — se compone con Card</td>
</tr>
<tr>
<td><code>Badge</code></td>
<td><code>default · brand · success · warning · danger · info · violet</code><br/><code>sm · md · lg</code> · <code>dot</code></td>
<td>Etiqueta pill-shaped con punto de color opcional</td>
</tr>
<tr>
<td><code>Alert</code></td>
<td><code>success · error · warning · info</code></td>
<td>Banner con <code>role="alert"</code> para lectores de pantalla</td>
</tr>
<tr>
<td><code>EmptyState</code></td>
<td><code>icon · title · description · action</code></td>
<td>Estado vacío de listas con slot de acción</td>
</tr>
<tr>
<td><code>ScoreRing</code></td>
<td><code>score (0–1)</code> · <code>size</code></td>
<td>SVG circular de progreso. Verde ≥80% · Ámbar ≥60% · Rojo &lt;60%</td>
</tr>
<tr>
<td><code>Input</code></td>
<td><code>label · hint · error · leftIcon · rightIcon</code></td>
<td>Campo con <code>aria-invalid</code> y <code>aria-describedby</code></td>
</tr>
<tr>
<td><code>Select</code></td>
<td>Misma API que <code>Input</code></td>
<td>Renderiza <code>&lt;select&gt;</code> con el mismo sistema de label/error</td>
</tr>
<tr>
<td><code>Spinner</code></td>
<td><code>sm · md · lg</code></td>
<td>Spinner animado con <code>role="status"</code></td>
</tr>
<tr>
<td><code>PageLoader</code></td>
<td><code>message</code></td>
<td>Spinner centrado para estados de carga de página completa</td>
</tr>
<tr>
<td><code>Skeleton</code></td>
<td><code>className</code> (w/h via Tailwind)</td>
<td>Placeholder animado con pulse para contenido cargando</td>
</tr>
<tr>
<td><code>Sidebar</code></td>
<td>Sin props</td>
<td>Barra fija 256px. Lee ruta activa con <code>NavLink</code> automáticamente</td>
</tr>
</tbody>
</table>

---

### `shared/api/index.js`

Cliente HTTP centralizado basado en Axios.

**Interceptores:**
- **Request** → inyecta el token JWT desde `localStorage`
- **Response** → extrae `response.data` en éxito · normaliza errores de FastAPI a `Error(message)`

<br/>

<table>
<thead>
<tr><th>Método</th><th>HTTP</th><th>Endpoint</th><th>Descripción</th></tr>
</thead>
<tbody>
<tr><td><code>documentsApi.upload(file)</code></td><td>POST</td><td><code>/api/v1/documents</code></td><td>Sube archivo (multipart)</td></tr>
<tr><td><code>documentsApi.list()</code></td><td>GET</td><td><code>/api/v1/documents</code></td><td>Lista todos los documentos</td></tr>
<tr><td><code>documentsApi.get(id)</code></td><td>GET</td><td><code>/api/v1/documents/:id</code></td><td>Obtiene un documento</td></tr>
<tr><td><code>documentsApi.delete(id)</code></td><td>DELETE</td><td><code>/api/v1/documents/:id</code></td><td>Elimina un documento</td></tr>
<tr><td><code>adaptationsApi.create(payload)</code></td><td>POST</td><td><code>/api/v1/adaptations</code></td><td>Inicia la generación</td></tr>
<tr><td><code>adaptationsApi.list(params)</code></td><td>GET</td><td><code>/api/v1/adaptations</code></td><td>Lista con filtros opcionales</td></tr>
<tr><td><code>adaptationsApi.get(id)</code></td><td>GET</td><td><code>/api/v1/adaptations/:id</code></td><td>Obtiene resultado completo</td></tr>
<tr><td><code>adaptationsApi.getStatus(id)</code></td><td>GET</td><td><code>/api/v1/adaptations/:id/status</code></td><td>Solo estado — para polling</td></tr>
<tr><td><code>healthApi.check()</code></td><td>GET</td><td><code>/health</code></td><td>Verifica disponibilidad</td></tr>
</tbody>
</table>

---

### `shared/hooks/`

<table>
<thead>
<tr><th>Hook</th><th>Descripción</th></tr>
</thead>
<tbody>
<tr>
<td><code>useApi(apiFn)</code></td>
<td>Wrapper genérico que expone <code>{ data, loading, error, execute }</code> para cualquier función async</td>
</tr>
<tr>
<td><code>useLocalStorage(key, initialValue)</code></td>
<td>Igual que <code>useState</code> pero persiste el valor en <code>localStorage</code> via JSON</td>
</tr>
</tbody>
</table>

---

### `shared/types/index.js`

Tipos JSDoc del dominio para autocompletado + constantes de opciones para formularios.

<br/>

<table>
<thead>
<tr><th>Constante</th><th>Contenido</th></tr>
</thead>
<tbody>
<tr><td><code>PROFILES</code></td><td>4 perfiles con <code>value</code>, <code>label</code> y <code>description</code></td></tr>
<tr><td><code>FORMATS</code></td><td>5 formatos con <code>value</code>, <code>label</code>, <code>icon</code> (emoji) y <code>description</code></td></tr>
<tr><td><code>INDUSTRIES</code></td><td>4 industrias con <code>value</code> y <code>label</code></td></tr>
<tr><td><code>DETAIL_LEVELS</code></td><td>4 niveles con <code>value</code>, <code>label</code> y <code>description</code></td></tr>
</tbody>
</table>

---

### `shared/utils/index.js`

<table>
<thead>
<tr><th>Función</th><th>Descripción</th><th>Ejemplo</th></tr>
</thead>
<tbody>
<tr><td><code>cn(...classes)</code></td><td>Merge seguro de clases Tailwind via clsx + tailwind-merge</td><td><code>cn('px-4', active && 'bg-brand-600')</code></td></tr>
<tr><td><code>formatDate(date)</code></td><td>Fecha legible en español</td><td><code>"15 sep 2026, 10:00"</code></td></tr>
<tr><td><code>formatFileSize(bytes)</code></td><td>Tamaño legible</td><td><code>"2.4 MB"</code></td></tr>
<tr><td><code>getProfileColor(profile)</code></td><td>Clases Tailwind de color por perfil</td><td><code>"text-emerald-400 bg-emerald-400/10"</code></td></tr>
<tr><td><code>getFormatColor(format)</code></td><td>Clases Tailwind de color por formato</td><td><code>"text-cyan-400 bg-cyan-400/10"</code></td></tr>
<tr><td><code>truncate(text, max)</code></td><td>Corta texto con <code>…</code> al superar el límite</td><td><code>truncate("Texto largo...", 50)</code></td></tr>
</tbody>
</table>

---

## 🔄 Flujo de usuario

```
  Abre la app
       │
       ▼
  ┌─────────────────────────────────┐
  │         Dashboard  /            │
  │  Stats · Recientes · Demos      │
  └─────────────────────────────────┘
       │  clic "Nueva Adaptación"
       ▼
  ┌─────────────────────────────────┐
  │     Nueva Adaptación  /new      │
  │  ① Sube el documento            │
  │  ② Configura: Perfil → Formato  │
  │              Nicho  → Detalle   │
  │  ③ "Generar contenido"          │
  └─────────────────────────────────┘
       │  navega con adaptation en state
       ▼
  ┌─────────────────────────────────┐
  │    Resultado  /result/:id       │
  │  Pipeline animado agente a      │
  │  agente → resultado generado    │
  │  con score del Critic Agent     │
  └─────────────────────────────────┘
       │  sidebar → Historial
       ▼
  ┌─────────────────────────────────┐
  │     Historial  /history         │
  │  Filtros · Grid de cards        │
  │  Clic en card → /result/:id     │
  └─────────────────────────────────┘
```

---

## 🔌 Conexión con el backend

El frontend funciona con datos mock. Cuando el backend esté disponible hay **5 puntos específicos** para conectar la API real. Todos están marcados con `// TODO:` en el código.

<br/>

<table>
<thead>
<tr><th>Archivo</th><th>Mock actual</th><th>API real</th></tr>
</thead>
<tbody>
<tr>
<td><code>NewAdaptationPage.jsx</code></td>
<td><code>setTimeout</code> 1.2s</td>
<td><code>documentsApi.upload(file)</code></td>
</tr>
<tr>
<td><code>NewAdaptationPage.jsx</code></td>
<td><code>setTimeout</code> 1.5s</td>
<td><code>adaptationsApi.create(payload)</code></td>
</tr>
<tr>
<td><code>ResultPage.jsx</code></td>
<td><code>setInterval</code> 1.8s por agente</td>
<td>Polling a <code>adaptationsApi.getStatus(id)</code></td>
</tr>
<tr>
<td><code>DashboardPage.jsx</code></td>
<td>Arrays hardcodeados</td>
<td><code>adaptationsApi.list()</code> + endpoint de stats</td>
</tr>
<tr>
<td><code>HistoryPage.jsx</code></td>
<td>Array hardcodeado</td>
<td><code>adaptationsApi.list(params)</code></td>
</tr>
</tbody>
</table>

---

## 📐 Convenciones de código

<table>
<thead>
<tr><th>Área</th><th>Regla</th></tr>
</thead>
<tbody>
<tr>
<td><strong>Exports</strong></td>
<td>Siempre named exports: <code>export function Componente()</code> — nunca <code>export default</code></td>
</tr>
<tr>
<td><strong>Constantes</strong></td>
<td>UPPER_CASE al nivel del módulo: <code>const AGENT_STEPS = [...]</code></td>
</tr>
<tr>
<td><strong>Sub-componentes</strong></td>
<td>JSX complejo → extraer sub-componentes con nombres descriptivos dentro del mismo archivo</td>
</tr>
<tr>
<td><strong>Hooks custom</strong></td>
<td>Extraer cuando la lógica supera ~10 líneas: <code>useDocumentUpload</code>, <code>useHistoryFilters</code></td>
</tr>
<tr>
<td><strong>Lookup maps</strong></td>
<td>Reemplazar <code>if/else</code> o ternarios encadenados: <code>const VARIANT_CLASSES = {}</code></td>
</tr>
<tr>
<td><strong>Tailwind</strong></td>
<td>Siempre <code>cn()</code> para combinar clases — nunca template literals</td>
</tr>
<tr>
<td><strong>Accesibilidad</strong></td>
<td><code>div</code> clickeables: <code>role="button"</code> · <code>tabIndex</code> · <code>onKeyDown</code> con Enter</td>
</tr>
<tr>
<td><strong>JSDoc</strong></td>
<td>En todos los componentes exportados con sus props documentadas</td>
</tr>
</tbody>
</table>

---

## 🎨 Diseño y estilos

La aplicación usa **tema oscuro** como base. Toda la paleta está definida en `tailwind.config.js`.

<br/>

### Colores principales

<table>
<thead>
<tr><th>Token</th><th>Valor</th><th>Uso</th></tr>
</thead>
<tbody>
<tr><td><code>brand-400/500/600</code></td><td>Índigo</td><td>Botones primarios, navegación activa, estados activos</td></tr>
<tr><td><code>accent-400/500/600</code></td><td>Violeta</td><td>Gradientes del logo, badges de formato</td></tr>
<tr><td><code>slate-950</code></td><td><code>#020617</code></td><td>Fondo base de la app</td></tr>
<tr><td><code>slate-900</code></td><td><code>#0f172a</code></td><td>Sidebar y fondos secundarios</td></tr>
<tr><td><code>slate-800</code></td><td><code>#1e293b</code></td><td>Cards, inputs y contenedores</td></tr>
<tr><td><code>slate-700</code></td><td><code>#334155</code></td><td>Bordes y separadores</td></tr>
</tbody>
</table>

### Colores semánticos

<table>
<thead>
<tr><th>Color</th><th>Estado que representa</th></tr>
</thead>
<tbody>
<tr><td>🟢 <code>emerald</code></td><td>Éxito · completado · aprobado por el Critic</td></tr>
<tr><td>🟡 <code>amber</code></td><td>Advertencia · pendiente · iteraciones del Critic</td></tr>
<tr><td>🔴 <code>red</code></td><td>Error · fallido · peligro</td></tr>
<tr><td>🔵 <code>blue</code></td><td>Información · procesando</td></tr>
<tr><td>🟣 <code>violet</code></td><td>Formato del contenido generado</td></tr>
</tbody>
</table>

### Tipografía y animaciones

**Fuente:** Inter (Google Fonts) · Pesos: 300, 400, 500, 600, 700, 800

<table>
<thead>
<tr><th>Clase</th><th>Descripción</th></tr>
</thead>
<tbody>
<tr><td><code>animate-fade-in</code></td><td>Opacidad 0→1 en 0.3s — páginas y contenido al aparecer</td></tr>
<tr><td><code>animate-slide-up</code></td><td>Sube 16px + fade-in en 0.3s</td></tr>
<tr><td><code>animate-pulse-slow</code></td><td>Pulse suave de 3s — indicadores de estado en progreso</td></tr>
</tbody>
</table>

---

<div align="center">

*NuevaMente · Programa ONE · Grupo 10*

</div>
