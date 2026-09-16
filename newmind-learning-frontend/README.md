<div align="center">

# NuevaMente — Frontend

**Sistema Inteligente de Adaptación y Generación de Contenido Educativo**

Programa ONE · Grupo 10 · Proyecto 1

<br/>

![React](https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-8-646CFF?style=flat-square&logo=vite&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-3-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white)
![React Router](https://img.shields.io/badge/React_Router-7-CA4245?style=flat-square&logo=reactrouter&logoColor=white)
![Axios](https://img.shields.io/badge/Axios-1.x-5A29E4?style=flat-square&logo=axios&logoColor=white)

</div>

---

## Tabla de contenidos

- [Descripción general](#descripción-general)
- [Instalación y arranque](#instalación-y-arranque)
- [Arquitectura — Feature-Sliced Design](#arquitectura--feature-sliced-design)
- [Estructura de carpetas](#estructura-de-carpetas)
- [Capa `app`](#capa-app)
- [Capa `pages`](#capa-pages)
- [Capa `widgets`](#capa-widgets)
- [Capa `entities`](#capa-entities)
- [Capa `shared`](#capa-shared)
- [Flujo de usuario](#flujo-de-usuario)
- [Conexión con el backend](#conexión-con-el-backend)
- [Convenciones de código](#convenciones-de-código)
- [Diseño y estilos](#diseño-y-estilos)

---

## Descripción general

El frontend de NuevaMente es la interfaz visual del sistema. Permite cargar documentos técnicos, configurar cómo se va a adaptar el contenido y visualizar el resultado generado por el pipeline multiagente.

**Responsabilidades del frontend:**
- Cargar y validar documentos (PDF, Markdown, TXT)
- Recolectar la configuración de la adaptación (perfil, formato, nicho, nivel de detalle)
- Visualizar el progreso del pipeline de agentes en tiempo real
- Renderizar el contenido generado según su formato (flashcards, tutorial, quiz, etc.)
- Mostrar el historial de adaptaciones con filtros

**Lo que el frontend NO hace:**
- No tiene lógica de IA — eso vive en el backend
- No se comunica directamente con Gemini, ChromaDB ni PostgreSQL
- No accede al sistema de archivos más allá del input de carga

> El frontend funciona completamente con datos simulados mientras el backend no esté disponible. Ver sección [Conexión con el backend](#conexión-con-el-backend).

---

## Instalación y arranque

### Requisitos

- Node.js 18 o superior
- npm 9 o superior

### Pasos

```bash
# 1. Instalar dependencias
npm install

# 2. Crear el archivo de entorno a partir del ejemplo
cp .env.example .env
```

Editar `.env` y configurar la URL del backend:

```env
VITE_API_URL=http://localhost:8000
```

### Comandos disponibles

| Comando | Descripción |
|---|---|
| `npm run dev` | Servidor de desarrollo con hot reload en `localhost:5173` |
| `npm run build` | Build de producción en `dist/` |
| `npm run preview` | Sirve el build de producción localmente |
| `npm run lint` | Ejecuta el linter (Oxlint) |

---

## Arquitectura — Feature-Sliced Design

El proyecto sigue **Feature-Sliced Design (FSD)**, una metodología de arquitectura por capas para aplicaciones frontend. La regla central es que **una capa solo puede importar desde capas inferiores**, nunca de las superiores.

```
┌──────────────────────────────────────────────────────────┐
│  app        Configuración global, providers y router     │
├──────────────────────────────────────────────────────────┤
│  pages      Pantallas completas (una por ruta)           │
├──────────────────────────────────────────────────────────┤
│  widgets    Bloques funcionales complejos                 │
├──────────────────────────────────────────────────────────┤
│  entities   Representación visual de objetos del dominio │
├──────────────────────────────────────────────────────────┤
│  shared     UI base, hooks, API client y utilidades      │
└──────────────────────────────────────────────────────────┘
         Cada capa solo importa desde las que están debajo
```

**Ejemplo correcto:** una `page` importa un `widget` o algo de `shared`.  
**Ejemplo incorrecto:** un `widget` importa algo de `pages` — esto rompe la arquitectura.

Esta regla evita dependencias circulares y hace que cada módulo sea comprensible de forma aislada.

---

## Estructura de carpetas

```
src/
│
├── App.jsx                          Componente raíz: layout (Sidebar + área principal)
├── main.jsx                         Punto de entrada: monta React en el DOM
│
├── app/
│   ├── providers/
│   │   └── index.jsx                BrowserRouter y futuros providers globales
│   ├── router/
│   │   └── index.jsx                Definición de las 4 rutas de la aplicación
│   └── styles/
│       └── globals.css              Tailwind, fuente Inter y clases CSS reutilizables
│
├── pages/
│   ├── dashboard/
│   │   └── DashboardPage.jsx        Ruta /          — Inicio, stats y adaptaciones recientes
│   ├── new-adaptation/
│   │   └── NewAdaptationPage.jsx    Ruta /new       — Carga de documento y configuración
│   ├── result/
│   │   └── ResultPage.jsx           Ruta /result/:id — Pipeline en vivo y resultado
│   └── history/
│       └── HistoryPage.jsx          Ruta /history   — Historial con filtros
│
├── widgets/
│   ├── adaptation-form/
│   │   └── AdaptationForm.jsx       Formulario multi-paso (perfil → formato → nicho → detalle)
│   ├── content-viewer/
│   │   └── ContentViewer.jsx        Visualizador del contenido generado por formato
│   ├── document-uploader/
│   │   └── DocumentUploader.jsx     Zona drag-and-drop para cargar archivos
│   └── generation-status/
│       └── GenerationStatus.jsx     Pipeline multiagente animado en tiempo real
│
├── entities/
│   ├── adaptation/
│   │   └── ui/
│   │       └── AdaptationCard.jsx   Tarjeta resumen de una adaptación
│   └── document/
│       └── ui/
│           └── DocumentCard.jsx     Tarjeta resumen de un documento
│
└── shared/
    ├── api/
    │   └── index.js                 Cliente Axios y todos los endpoints del backend
    ├── hooks/
    │   ├── useApi.js                Hook genérico para llamadas async con loading/error
    │   └── useLocalStorage.js       Estado sincronizado con localStorage
    ├── types/
    │   └── index.js                 Tipos JSDoc del dominio y constantes de opciones
    ├── ui/
    │   ├── Alert.jsx                Alert · EmptyState · ScoreRing
    │   ├── Badge.jsx                Etiquetas pill con 7 variantes de color
    │   ├── Button.jsx               Botón con 5 variantes, 3 tamaños y estado loading
    │   ├── Card.jsx                 Card · CardHeader
    │   ├── Input.jsx                Input · Select con label, hint y error
    │   ├── Sidebar.jsx              Barra lateral fija con navegación principal
    │   └── Spinner.jsx              Spinner · PageLoader · Skeleton
    └── utils/
        └── index.js                 cn, formatDate, formatFileSize, truncate, etc.
```

---

## Capa `app`

Configura la aplicación antes de que se renderice cualquier pantalla.

### `app/providers/index.jsx`

Envuelve la app en `BrowserRouter` para habilitar la navegación. Es el lugar donde agregar futuros providers globales (autenticación, React Query, tema, etc.).

### `app/router/index.jsx`

Define las rutas de la aplicación usando React Router v7.

| Ruta | Componente | Descripción |
|---|---|---|
| `/` | `DashboardPage` | Inicio del sistema |
| `/new` | `NewAdaptationPage` | Crear nueva adaptación |
| `/result/:id` | `ResultPage` | Ver resultado de una adaptación |
| `/history` | `HistoryPage` | Historial de adaptaciones |
| `*` | Redirect a `/` | Cualquier ruta no reconocida |

### `app/styles/globals.css`

- Importa la fuente **Inter** desde Google Fonts (pesos 300–800)
- Inicializa Tailwind con `@tailwind base/components/utilities`
- Define el tema oscuro como base (`bg-slate-950`)
- Declara clases reutilizables como `@layer components`: `.btn-primary`, `.input-field`, `.label`, `.page-title`, `.section-title`, `.glass-card`, `.gradient-text`

---

## Capa `pages`

Una página por ruta. Las páginas orquestan widgets y entities, pero no contienen lógica de UI reutilizable.

---

### `DashboardPage` — `/`

Pantalla de inicio. Primer punto de contacto del usuario con el sistema.

**Contenido:**

```
┌─────────────────────────────────────────────────────────────┐
│  NuevaMente  ● Sistema activo          [Nueva Adaptación]   │
├──────────┬──────────┬────────────┬───────────────────────── │
│  12      │  38      │  5         │  91%                     │
│  Docs    │  Adapts  │  Formatos  │  Score Critic            │
├──────────────────────────────────┬──────────────────────────┤
│  Adaptaciones recientes          │  Inicio rápido           │
│  ┌──────────────────────────┐    │  [Crear adaptación]      │
│  │ AdaptationCard           │    │  [Ver historial]         │
│  └──────────────────────────┘    ├──────────────────────────┤
│  ┌──────────────────────────┐    │  Demos del proyecto      │
│  │ AdaptationCard           │    │  Demo 1 · Demo 2 · Demo 3│
│  └──────────────────────────┘    │                          │
└──────────────────────────────────┴──────────────────────────┘
```

**Sub-componentes internos:** `StatCard`, `DemoCase`

**Datos:** `MOCK_STATS`, `MOCK_RECENT_ADAPTATIONS`, `DEMO_CASES` — todos reemplazables por API.

---

### `NewAdaptationPage` — `/new`

Flujo de creación en dos pasos secuenciales.

**Paso 1 — Cargar documento**

- Usa el widget `DocumentUploader`
- El usuario arrastra o selecciona un archivo (PDF, MD, TXT)
- Se valida localmente y se sube al backend
- Al completar, se habilita el paso 2

**Paso 2 — Configurar adaptación**

- Usa el widget `AdaptationForm`
- El usuario elige perfil, formato, nicho y nivel de detalle
- Al confirmar navega a `/result/:id` con el objeto `adaptation` en el state de React Router

**Hooks internos:**

```
useDocumentUpload()   maneja el estado de upload (uploading, uploadedDoc, uploadError)
handleGenerate()      construye el payload y navega al resultado
```

---

### `ResultPage` — `/result/:id`

Muestra el resultado de una adaptación. Se comporta distinto según el estado.

| Estado | Qué muestra |
|---|---|
| `pending` · `processing` | Widget `GenerationStatus` con el pipeline animado agente por agente |
| `completed` | Widget `ContentViewer` con el contenido generado |
| `failed` | Banner de error con botón para reintentar |

**Hook interno `usePipelineSimulation`:**

Avanza un agente cada 1.8s usando `setInterval`. Al completar los 5 agentes inyecta los datos mock de resultado. Esto es simulación visual — reemplazar con polling a `adaptationsApi.getStatus(id)`.

**Sub-componentes internos:** `PageHeader`, `AdaptationMeta`

---

### `HistoryPage` — `/history`

Lista de todas las adaptaciones con filtros client-side.

**Filtros disponibles:**

| Filtro | Tipo | Opciones |
|---|---|---|
| Búsqueda | Texto libre | Título del documento |
| Perfil | Selector | Principiante · Junior · Lider · Gestor |
| Formato | Selector | Flashcards · Tutorial · Quiz · Resumen Ejecutivo · Guion |
| Estado | Selector | completed · processing · pending · failed |

Los filtros activos se muestran como badges con botón para limpiar todo.

**Hook interno `useHistoryFilters`:** centraliza los 4 estados de filtro y expone el array `filtered` ya procesado.

---

## Capa `widgets`

Bloques de UI complejos con lógica propia. Cada widget tiene una carpeta y un archivo `.jsx`.

---

### `AdaptationForm`

Wizard de 4 pasos para configurar la adaptación.

```
  ① Perfil  →  ② Formato  →  ③ Nicho  →  ④ Detalle
```

| Paso | Opciones |
|---|---|
| **Perfil** | Principiante · Junior · Lider · Gestor |
| **Formato** | Flashcards · Tutorial · Quiz · Resumen Ejecutivo · Guion |
| **Nicho** | General · Fintech · Salud · E-commerce |
| **Detalle** | Básico · Intermedio · Didáctico · Detallado |

- El botón "Siguiente" se habilita solo cuando hay una opción seleccionada
- El último paso muestra "Generar contenido" y llama a `onSubmit(values)`
- Cada paso tiene animación `fade-in` al aparecer

**Sub-componentes:** `StepIndicator` · `OptionGrid` · `ProfileStep` · `FormatStep` · `IndustryStep` · `DetailStep`

**Props:**
```js
onSubmit(values)   // { profile, format, industry, detailLevel }
loading            // boolean — spinner en el botón final durante la generación
```

---

### `ContentViewer`

Renderiza el contenido generado según el formato de la adaptación.

| Formato | Qué renderiza |
|---|---|
| **Flashcards** | Grid 2 columnas — concepto, pregunta, respuesta y fuente por tarjeta |
| **Tutorial** | Introducción → pasos numerados con bloques de código → conclusión |
| **Resumen Ejecutivo** | Resumen → puntos clave con bullets → riesgos en ámbar |
| **Quiz** | Preguntas con opciones A/B/C/D — respuesta correcta en verde + justificación |
| **Guion** | JSON formateado (vista provisional hasta definir el schema) |

Siempre incluye:
- Header con formato, perfil e industria + `ScoreRing` con el score del Critic
- `EvaluationBreakdown`: los 4 criterios del Critic (fidelidad, alineación, cumplimiento, coherencia)

**Props:**
```js
adaptation   // objeto Adaptation completo — debe tener status === 'completed' y content definido
```

---

### `DocumentUploader`

Zona de carga con drag-and-drop. Valida localmente antes de llamar al backend.

**Validaciones:**
- Extensión permitida: `.pdf` · `.md` · `.txt`
- Tamaño máximo: 20 MB

**Estados visuales:**

| Estado | Borde | Texto |
|---|---|---|
| Idle | Punteado gris | "Arrastrá o hacé clic para subir" |
| Dragging | Punteado brand azul | "Suelta el archivo aquí" |
| Success | Verde | "¡Archivo cargado correctamente!" |
| Error | Rojo | Mensaje de error específico |

**Sub-componentes:** `DropZoneIcon` · `DropZoneLabel` · `SelectedFileRow`

**Props:**
```js
onFileSelect(file)  // se llama cuando el archivo pasa validación local
uploading           // boolean — deshabilita la zona y muestra spinner
error               // string — error externo del backend
success             // boolean — marca la zona como exitosa
```

---

### `GenerationStatus`

Visualiza el pipeline de 5 agentes en tiempo real.

```
  ① Orchestrator Agent      Analiza la solicitud y define la ruta
  ② RAG Researcher Agent    Recupera fragmentos relevantes del documento
  ③ Context/Profile Agent   Adapta al perfil con instrucciones pedagógicas
  ④ Educational Generator   Genera el contenido educativo estructurado
  ⑤ Critic Agent            Evalúa calidad, fidelidad y coherencia
```

| Estado del paso | Ícono | Estilo |
|---|---|---|
| `done` | ✅ verde | Opacidad reducida |
| `active` | ⏳ spinner brand | Fondo brand resaltado |
| `idle` | ○ gris | Muy transparente |
| `error` | ⚠️ rojo | Fondo rojo tenue |

Si el Critic rechaza el contenido y hay regeneración en curso, muestra el contador "Iteración N/M".

**Sub-componentes:** `AgentStep`

**Props:**
```js
status          // 'pending' | 'processing' | 'completed' | 'failed'
currentAgent    // id del agente activo: 'orchestrator' | 'researcher' | 'context' | 'generator' | 'critic'
iteration       // número de iteración del Critic (default: 0)
maxIterations   // límite de iteraciones (default: 3)
```

---

## Capa `entities`

Representaciones visuales de los objetos del dominio. Son más simples que los widgets — solo muestran datos, no tienen lógica de negocio.

---

### `AdaptationCard`

Tarjeta compacta de una adaptación. Se usa en el dashboard y en el historial.

```
┌──────────────────────────────────────────────────────┐
│  Introducción a la Arquitectura de Redes VCN en OCI  │
│  [Principiante]  [Flashcards]  [General]             │
├──────────────────────────────────────────────────────┤
│  15 sep 2026, 10:00                      Score 92%   │
│                                     ● Completado     │
└──────────────────────────────────────────────────────┘
```

Es un elemento accesible: tiene `role="button"`, `tabIndex={0}`, soporte de teclado (`Enter`) y `focus ring`.

**Props:**
```js
adaptation    // objeto Adaptation
onClick()     // función opcional — si se pasa, la tarjeta es clickeable
```

---

### `DocumentCard`

Tarjeta compacta de un documento cargado. También exporta `DocumentTypeIcon` para uso independiente.

```
┌──────────────────────────────────────────────────────┐
│  📄  Guía de PostgreSQL para aplicaciones FastAPI    │
│      [PDF]  2.4 MB  ·  14 sep 2026, 09:00           │
└──────────────────────────────────────────────────────┘
```

El ícono cambia según el tipo: 📄 rojo para PDF · `</>` azul para Markdown · 📃 gris para TXT.

**Props:**
```js
document        // objeto Document
onSelect(doc)   // función opcional — habilita modo selección
selected        // boolean — muestra checkmark brand
```

---

## Capa `shared`

Código reutilizable sin lógica de negocio del dominio. Puede ser importado desde cualquier capa.

---

### `shared/ui/` — Sistema de diseño

#### `Button`

```jsx
<Button variant="primary" size="md" loading={false} leftIcon={<Icon />}>
  Generar contenido
</Button>
```

| Prop | Valores | Default |
|---|---|---|
| `variant` | `primary` · `secondary` · `ghost` · `danger` · `success` | `primary` |
| `size` | `sm` · `md` · `lg` | `md` |
| `loading` | `boolean` | `false` |
| `fullWidth` | `boolean` | `false` |
| `leftIcon` / `rightIcon` | `ReactNode` | — |

Con `loading=true` reemplaza el contenido por un spinner y deshabilita el botón automáticamente.

#### `Card` y `CardHeader`

```jsx
<Card glass hover>
  <CardHeader
    title="Adaptaciones recientes"
    action={<Link to="/history">Ver todas →</Link>}
  />
  {/* contenido */}
</Card>
```

`Card` es un contenedor surface. `glass=true` (default) aplica glassmorphism con `backdrop-blur`. `CardHeader` es una fila independiente con título y acción — no envuelve en Card, se compone.

#### `Badge`

```jsx
<Badge variant="success" size="sm" dot>Completado</Badge>
```

| Variante | Color |
|---|---|
| `default` | Gris neutro |
| `brand` | Índigo |
| `success` | Esmeralda |
| `warning` | Ámbar |
| `danger` | Rojo |
| `info` | Azul |
| `violet` | Violeta |

La prop `dot` agrega un círculo de color como indicador visual antes del texto.

#### `Alert`

```jsx
<Alert variant="error" title="Título opcional">
  Descripción del problema.
</Alert>
```

Variantes: `success` · `error` · `warning` · `info`. Incluye `role="alert"` para lectores de pantalla.

#### `EmptyState` (exportado desde `Alert.jsx`)

```jsx
<EmptyState
  icon={History}
  title="No hay adaptaciones"
  description="Probá ajustando los filtros."
  action={<Button>Nueva adaptación</Button>}
/>
```

#### `ScoreRing` (exportado desde `Alert.jsx`)

```jsx
<ScoreRing score={0.92} size={64} />
```

SVG circular que muestra un porcentaje. Color automático: verde ≥ 80% · ámbar ≥ 60% · rojo < 60%.

#### `Input` y `Select`

```jsx
<Input
  label="Buscar"
  hint="Texto de ayuda"
  error="Campo requerido"
  leftIcon={<Search />}
/>

<Select label="Perfil">
  <option value="Junior">Junior</option>
</Select>
```

El `id` del campo se deriva del `label` automáticamente. Incluyen `aria-invalid` y `aria-describedby`.

#### `Spinner` · `PageLoader` · `Skeleton`

```jsx
<Spinner size="md" />
<PageLoader message="Generando contenido..." />
<Skeleton className="h-4 w-32" />
```

#### `Sidebar`

Barra lateral fija de 256px. Lee la ruta activa con `NavLink` y aplica estilos automáticamente. Los ítems de navegación están en la constante `NAV_ITEMS` dentro del mismo archivo.

---

### `shared/api/index.js`

Cliente HTTP centralizado basado en Axios.

**Configuración:**
- Base URL: `VITE_API_URL` (fallback: `http://localhost:8000`)
- Timeout: 60 segundos
- Interceptor de request: inyecta el token JWT desde `localStorage`
- Interceptor de response: extrae `response.data` en éxito · normaliza errores de FastAPI a `Error`

**Métodos:**

```js
// Documentos
documentsApi.upload(file)       POST   /api/v1/documents          multipart/form-data
documentsApi.list()             GET    /api/v1/documents
documentsApi.get(id)            GET    /api/v1/documents/:id
documentsApi.delete(id)         DELETE /api/v1/documents/:id

// Adaptaciones
adaptationsApi.create(payload)  POST   /api/v1/adaptations
adaptationsApi.list(params)     GET    /api/v1/adaptations         acepta filtros
adaptationsApi.get(id)          GET    /api/v1/adaptations/:id
adaptationsApi.getStatus(id)    GET    /api/v1/adaptations/:id/status   para polling

// Sistema
healthApi.check()               GET    /health
```

---

### `shared/hooks/`

#### `useApi(apiFn)`

Wrapper genérico para llamadas async. Elimina el boilerplate de loading/error.

```js
const { data, loading, error, execute } = useApi(adaptationsApi.list)

// Ejecutar:
await execute({ profile: 'Junior', format: 'Tutorial' })
// data    → resultado si tuvo éxito
// loading → true mientras espera
// error   → mensaje si falló
```

#### `useLocalStorage(key, initialValue)`

Igual que `useState` pero persiste el valor en `localStorage` via JSON.

---

### `shared/types/index.js`

**Tipos JSDoc del dominio** para autocompletado:

```js
/**
 * @typedef {Object} Adaptation
 * @property {number}  id
 * @property {string}  documentTitle
 * @property {Profile} profile
 * @property {ContentFormat} format
 * @property {AdaptationStatus} status
 * @property {Object} [content]
 * @property {QualityEvaluation} [evaluation]
 */
```

**Constantes de opciones** para formularios y filtros:

```js
PROFILES       // [{ value, label, description }]         4 perfiles
FORMATS        // [{ value, label, icon, description }]   5 formatos
INDUSTRIES     // [{ value, label }]                      4 industrias
DETAIL_LEVELS  // [{ value, label, description }]         4 niveles
```

---

### `shared/utils/index.js`

| Función | Descripción | Ejemplo de salida |
|---|---|---|
| `cn(...classes)` | Merge seguro de clases Tailwind | `"px-4 bg-brand-600"` |
| `formatDate(date)` | Fecha legible en español | `"15 sep 2026, 10:00"` |
| `formatFileSize(bytes)` | Tamaño legible | `"2.4 MB"` |
| `getProfileColor(profile)` | Clases de color por perfil | `"text-emerald-400 bg-emerald-400/10"` |
| `getFormatColor(format)` | Clases de color por formato | `"text-cyan-400 bg-cyan-400/10"` |
| `truncate(text, max)` | Corta texto con `…` | `"Introducción a la Arq…"` |

---

## Flujo de usuario

```
  Abre la app
       │
       ▼
  ┌─────────────────────────────┐
  │         Dashboard  /        │
  │  Stats · Recientes · Demos  │
  └─────────────────────────────┘
       │
       │  Clic "Nueva Adaptación"
       ▼
  ┌─────────────────────────────┐
  │     Nueva Adaptación  /new  │
  │                             │
  │  Paso 1: Sube el documento  │
  │  Paso 2: Elige parámetros   │
  │          Perfil → Formato   │
  │          Nicho  → Detalle   │
  └─────────────────────────────┘
       │
       │  Clic "Generar contenido"
       ▼
  ┌─────────────────────────────┐
  │     Resultado  /result/:id  │
  │                             │
  │  Pipeline animado en vivo   │
  │  Orchestrator → Researcher  │
  │  → Context → Generator      │
  │  → Critic (con score)       │
  │            ↓                │
  │    Contenido generado       │
  └─────────────────────────────┘
       │
       │  Sidebar → Historial
       ▼
  ┌─────────────────────────────┐
  │      Historial  /history    │
  │  Filtros · Grid de cards    │
  │  Clic en card → /result/:id │
  └─────────────────────────────┘
```

---

## Conexión con el backend

El frontend funciona completamente con datos mock. Cuando el backend esté disponible, hay **5 puntos específicos** donde conectar la API real, todos marcados con `// TODO:` en el código:

| Archivo | Mock actual | API real |
|---|---|---|
| `NewAdaptationPage.jsx` | `setTimeout` 1.2s | `documentsApi.upload(file)` |
| `NewAdaptationPage.jsx` | `setTimeout` 1.5s | `adaptationsApi.create(payload)` |
| `ResultPage.jsx` | `setInterval` 1.8s por agente | polling a `adaptationsApi.getStatus(id)` |
| `DashboardPage.jsx` | Arrays hardcodeados | `adaptationsApi.list()` + endpoint de stats |
| `HistoryPage.jsx` | Array hardcodeado | `adaptationsApi.list(params)` |

---

## Convenciones de código

### Exports

- Siempre named exports: `export function NombreComponente()` — nunca `export default`
- Las constantes de módulo van en UPPER_CASE: `const AGENT_STEPS = [...]`

### Componentes

- JSX complejo → extraer sub-componentes con nombres descriptivos
- Un archivo = un componente principal exportado + sus sub-componentes internos sin exportar
- JSDoc en todos los componentes exportados

### Lógica

- Las funciones de validación y derivación van fuera del componente como funciones puras
- Los hooks custom se extraen cuando la lógica tiene más de ~10 líneas: `useDocumentUpload`, `useHistoryFilters`, `usePipelineSimulation`
- Los lookup maps reemplazan los `if/else` o ternarios encadenados: `const VARIANT_CLASSES = {}`

### Tailwind

- Siempre usar `cn()` para combinar clases — nunca template literals
- Clases condicionales dentro de `cn()`: `cn('base', condition && 'extra')`

### Accesibilidad

- Elementos `div` clickeables: `role="button"` · `tabIndex={0}` · `onKeyDown` con `Enter`
- Inputs: `aria-invalid` · `aria-describedby` apuntando al mensaje de error
- Íconos decorativos: `aria-hidden="true"`
- Spinners: `role="status"` · `aria-label`
- Progress bars: `role="progressbar"` · `aria-valuenow`

---

## Diseño y estilos

### Tema

La aplicación usa **tema oscuro** como base. El fondo raíz es `slate-950` y todas las superficies escalan hacia colores más claros de la escala `slate`.

### Paleta de color

| Token | Valor | Uso |
|---|---|---|
| `brand-400 / 500 / 600` | Índigo | Acciones primarias, estados activos, navegación |
| `accent-400 / 500 / 600` | Violeta | Gradientes, badges de formato |
| `slate-950` | `#020617` | Fondo base de la app |
| `slate-900` | `#0f172a` | Sidebar y fondos secundarios |
| `slate-800` | `#1e293b` | Cards, inputs, contenedores |
| `slate-700` | `#334155` | Bordes y separadores |
| `slate-600` | `#475569` | Bordes en hover |
| `slate-400 / 300` | — | Texto secundario y etiquetas |
| `slate-50 / 100` | — | Texto principal |

### Semántica de color para estados

| Color | Estado |
|---|---|
| `emerald` | Éxito · completado · aprobado |
| `amber` | Advertencia · pendiente · iteraciones del Critic |
| `red` | Error · fallido · peligro |
| `blue` | Información · procesando |
| `violet` | Formato del contenido |

### Tipografía

Fuente **Inter** cargada desde Google Fonts. Pesos usados: 300, 400, 500, 600, 700, 800.

### Animaciones

| Clase | Descripción |
|---|---|
| `animate-fade-in` | Opacidad 0→1 en 0.3s — páginas y contenido al aparecer |
| `animate-slide-up` | Sube 16px + fade-in en 0.3s |
| `animate-pulse-slow` | Pulse suave de 3s — indicadores de estado en progreso |

---

<div align="center">

NuevaMente · Programa ONE · Grupo 10

</div>
