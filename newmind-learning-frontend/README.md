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

> Interfaz visual del sistema NuevaMente.
> Permite cargar documentos técnicos, configurar la adaptación educativa
> y visualizar el contenido generado por el backend.

<br/>

</div>

---

## 📋 Tabla de contenidos

- [📖 Descripción general](#-descripción-general)
- [🚀 Instalación y arranque](#-instalación-y-arranque)
- [🏗️ Arquitectura — Feature-Sliced Design](#-arquitectura--feature-sliced-design)
- [📁 Estructura de carpetas](#-estructura-de-carpetas)
- [📺 Pantallas de la aplicación](#-pantallas-de-la-aplicación)
- [🤖 Progreso ilustrativo](#-progreso-ilustrativo)
- [🧩 Widgets](#-widgets)
- [🗂️ Entities](#-entities)
- [📦 Shared — código reutilizable](#-shared--código-reutilizable)
- [🔌 Conexión con el backend](#-conexión-con-el-backend)
- [📐 Convenciones de código](#-convenciones-de-código)
- [🎨 Sistema de diseño](#-sistema-de-diseño)

---

## 📖 Descripción general

NuevaMente transforma documentos técnicos en contenido educativo adaptado a distintos perfiles. El frontend es la capa de interfaz — no contiene lógica de IA.

<br/>

<table>
<tr>
<td width="50%" valign="top">

**✅ Responsabilidades del frontend**

- Cargar y validar documentos (PDF, MD, TXT)
- Recolectar la configuración de la adaptación
- Consultar el estado del trabajo y mostrar una animación ilustrativa, sin telemetría de agentes
- Renderizar el contenido generado por formato
- Gestionar el historial de adaptaciones con filtros

</td>
<td width="50%" valign="top">

**❌ Lo que el frontend NO hace**

- No tiene lógica de IA ni modelos de lenguaje
- No se comunica con Gemini, ChromaDB ni PostgreSQL
- No accede al sistema de archivos directamente
- No conoce la implementación interna del backend

</td>
</tr>
</table>

---

## 🚀 Instalación y arranque

### Requisitos

- **Node.js** 22, o una versión compatible con Vite 8: `^20.19.0 || >=22.12.0`
- **npm** 9 o superior

### Pasos

```bash
# 1. Clonar el repositorio (si aún no está disponible localmente)
git clone https://github.com/No-Country-simulation/G10-team1-newmind.git
cd G10-team1-newmind/newmind-learning-frontend

# 2. Instalar dependencias
npm install

# 3. Crear el archivo de entorno
cp .env.example .env
```

Editar `.env` y configurar la URL del backend:

```env
VITE_API_URL=http://localhost:8000
```

### Arranque con Docker

La imagen incluida está pensada únicamente para desarrollo local: ejecuta el servidor de Vite con hot reload y no es una imagen lista para producción. Este flujo no requiere instalar Node.js en el host.

Desde la raíz del repositorio, inicie el frontend y el backend:

```bash
docker compose up --build app frontend
```

El frontend queda disponible en `http://localhost:5173`, el backend en `http://localhost:8000` y su endpoint de salud en `http://localhost:8000/health`.

Para iniciar solamente el frontend desde la raíz:

```bash
docker compose up --build frontend
```

Compose configura `VITE_API_URL=http://localhost:8000`. Esta variable se usa en el código que corre en el navegador, así que debe apuntar a una URL accesible desde el host. El nombre de servicio `app` solo funciona como DNS entre contenedores y el navegador no puede resolverlo.

Para detener los servicios:

```bash
docker compose down
```

> La carga, la adaptación, el resultado, el historial y las estadísticas del panel consultan la API. Las tarjetas de ejemplos y la animación de etapas son ilustrativas; iniciar ambos servicios no sustituye una prueba funcional de extremo a extremo.

### Comandos disponibles

<br/>

<table>
<thead>
<tr>
<th width="30%">Comando</th>
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
<td>Build de producción optimizado en la carpeta <code>dist/</code></td>
</tr>
<tr>
<td><code>npm run preview</code></td>
<td>Sirve el build de producción localmente para verificarlo antes de desplegar</td>
</tr>
<tr>
<td><code>npm run lint</code></td>
<td>Ejecuta el linter (Oxlint) sobre todos los archivos del proyecto</td>
</tr>
</tbody>
</table>

---

## 🏗️ Arquitectura — Feature-Sliced Design

El proyecto sigue **Feature-Sliced Design (FSD)**, una arquitectura por capas donde **cada capa solo puede importar desde las capas que están debajo de ella**.

```mermaid
graph TD
    subgraph FSD["Feature-Sliced Design — Regla de capas"]
        A["🔧 app\nConfiguración global, providers, router"]
        B["📄 pages\nPantallas completas — una por ruta"]
        C["🧩 widgets\nBloques funcionales complejos"]
        D["🗂️ entities\nRepresentación visual del dominio"]
        E["📦 shared\nUI base, API client, hooks, utils"]
    end

    A -->|puede importar de| B
    B -->|puede importar de| C
    C -->|puede importar de| D
    D -->|puede importar de| E

    style A fill:#4f46e5,color:#fff,stroke:#4338ca
    style B fill:#0891b2,color:#fff,stroke:#0e7490
    style C fill:#059669,color:#fff,stroke:#047857
    style D fill:#d97706,color:#fff,stroke:#b45309
    style E fill:#7c3aed,color:#fff,stroke:#6d28d9
```

<br/>

<table>
<thead>
<tr>
<th>¿Es válido?</th>
<th>Ejemplo</th>
</tr>
</thead>
<tbody>
<tr>
<td>✅ Correcto</td>
<td>Una <code>page</code> importa un <code>widget</code> o algo de <code>shared</code></td>
</tr>
<tr>
<td>✅ Correcto</td>
<td>Un <code>widget</code> importa un <code>entity</code> o algo de <code>shared</code></td>
</tr>
<tr>
<td>❌ Incorrecto</td>
<td>Un <code>widget</code> importa algo de <code>pages</code></td>
</tr>
<tr>
<td>❌ Incorrecto</td>
<td>Un <code>entity</code> importa un <code>widget</code></td>
</tr>
</tbody>
</table>

---

## 📁 Estructura de carpetas

```
newmind-learning-frontend/
│
├── 📄 index.html                        Punto de montaje HTML de React
├── ⚙️  vite.config.js                   Configuración de Vite (alias @→src, plugin React)
├── 🎨 tailwind.config.js                Paleta de colores, fuentes y animaciones
├── 📦 package.json                      Dependencias y scripts del proyecto
├── 🔒 .env.example                      Variables de entorno necesarias (sin valores reales)
│
└── src/
    ├── App.jsx                          Componente raíz: Sidebar + área de contenido
    ├── main.jsx                         Entry point: monta React en el DOM
    │
    ├── app/                             ── Capa: app ──────────────────────────────────
    │   ├── providers/index.jsx          BrowserRouter y futuros providers globales
    │   ├── router/index.jsx             Definición de las 4 rutas de la aplicación
    │   └── styles/globals.css          Tailwind + fuente Inter + clases reutilizables
    │
    ├── pages/                           ── Capa: pages ────────────────────────────────
    │   ├── dashboard/DashboardPage.jsx  Ruta /          → Inicio del sistema
    │   ├── new-adaptation/
    │   │   └── NewAdaptationPage.jsx    Ruta /new       → Crear nueva adaptación
    │   ├── result/ResultPage.jsx        Ruta /result/:id → Ver resultado generado
    │   └── history/HistoryPage.jsx      Ruta /history   → Historial con filtros
    │
    ├── widgets/                         ── Capa: widgets ──────────────────────────────
    │   ├── adaptation-form/
    │   │   └── AdaptationForm.jsx       Formulario multi-paso de configuración
    │   ├── content-viewer/
    │   │   └── ContentViewer.jsx        Muestra el contenido generado por formato
    │   ├── document-uploader/
    │   │   └── DocumentUploader.jsx     Zona drag-and-drop para cargar archivos
    │   └── generation-status/
    │       └── GenerationStatus.jsx     Progreso ilustrativo con etapas animadas
    │
    ├── entities/                        ── Capa: entities ─────────────────────────────
    │   ├── adaptation/ui/
    │   │   └── AdaptationCard.jsx       Tarjeta resumen de una adaptación
    │   └── document/ui/
    │       └── DocumentCard.jsx         Tarjeta resumen de un documento
    │
    └── shared/                          ── Capa: shared ───────────────────────────────
        ├── api/index.js                 Cliente Axios + todos los endpoints del backend
        ├── hooks/
        │   ├── useApi.js                Hook genérico para llamadas async
        │   └── useLocalStorage.js       Estado sincronizado con localStorage
        ├── types/index.js               Tipos JSDoc del dominio + constantes de opciones
        ├── ui/                          Sistema de diseño completo
        │   ├── Alert.jsx               Alert · EmptyState · ScoreRing
        │   ├── Badge.jsx               Etiquetas pill con 7 variantes de color
        │   ├── Button.jsx              5 variantes · 3 tamaños · estado loading
        │   ├── Card.jsx                Card · CardHeader
        │   ├── Input.jsx               Input · Select con label, hint y error
        │   ├── Sidebar.jsx             Barra lateral fija con navegación
        │   └── Spinner.jsx             Spinner · PageLoader · Skeleton
        └── utils/index.js               cn, formatDate, formatFileSize, truncate...
```

---

## 📺 Pantallas de la aplicación

La aplicación tiene **4 pantallas** conectadas por el sidebar y la navegación.

```mermaid
graph LR
    subgraph NAV["🔗 Navegación"]
        D["🏠 Dashboard\n/"]
        N["➕ Nueva Adaptación\n/new"]
        R["📊 Resultado\n/result/:id"]
        H["🕓 Historial\n/history"]
    end

    D -->|"Nueva Adaptación"| N
    N -->|"Generar contenido"| R
    R -->|"Ver historial"| H
    H -->|"Clic en card"| R
    D -->|"Clic en card"| R

    style D fill:#4f46e5,color:#fff,stroke:#4338ca
    style N fill:#0891b2,color:#fff,stroke:#0e7490
    style R fill:#059669,color:#fff,stroke:#047857
    style H fill:#7c3aed,color:#fff,stroke:#6d28d9
```

<br/>

<details>
<summary><strong>📌 Dashboard — <code>/</code></strong></summary>
<br/>

Pantalla de inicio y primer punto de contacto del usuario.

<table>
<thead>
<tr><th>Sección</th><th>Qué muestra</th><th>Estado</th></tr>
</thead>
<tbody>
<tr>
<td>Hero</td>
<td>Título del sistema + badge "Sistema activo" + botón "Nueva Adaptación"</td>
<td>Estático</td>
</tr>
<tr>
<td>Estadísticas (4 tarjetas)</td>
<td>Documentos cargados · Adaptaciones completadas · Formatos distintos · Promedio de puntuación de evaluación</td>
<td>Calculadas a partir de listas de la API; no existe un endpoint específico de estadísticas</td>
</tr>
<tr>
<td>Adaptaciones recientes</td>
<td>Últimas 3 adaptaciones con <code>AdaptationCard</code></td>
<td>Lista de la API</td>
</tr>
<tr>
<td>Inicio rápido</td>
<td>Accesos directos a crear adaptación y ver historial</td>
<td>Estático</td>
</tr>
<tr>
<td>Demos del proyecto</td>
<td>Tres ejemplos estáticos; no son resultados generados ni prueba de entrega</td>
<td>Estático</td>
</tr>
</tbody>
</table>

</details>

<details>
<summary><strong>📌 Nueva Adaptación — <code>/new</code></strong></summary>
<br/>

Flujo de creación en dos pasos secuenciales que se habilitan en orden.

<table>
<thead>
<tr><th>Paso</th><th>Widget</th><th>Descripción</th></tr>
</thead>
<tbody>
<tr>
<td><strong>① Cargar documento</strong></td>
<td><code>DocumentUploader</code></td>
<td>Arrastre o seleccione un archivo PDF, MD o TXT. Se valida localmente (tipo y tamaño ≤ 20 MiB) y se sube al backend.</td>
</tr>
<tr>
<td><strong>② Configurar adaptación</strong></td>
<td><code>AdaptationForm</code></td>
<td>Se habilita cuando el documento está cargado. El usuario elige perfil, formato, nicho y nivel de detalle. Al confirmar navega a <code>/result/:id</code>.</td>
</tr>
</tbody>
</table>

</details>

<details>
<summary><strong>📌 Resultado — <code>/result/:id</code></strong></summary>
<br/>

Muestra el resultado de una adaptación. Cambia de vista según el estado.

<table>
<thead>
<tr><th>Estado</th><th>Vista</th></tr>
</thead>
<tbody>
<tr>
<td><code>processing</code> · <code>pending</code></td>
<td><code>GenerationStatus</code> muestra etapas animadas ilustrativas; el estado real se consulta por la API</td>
</tr>
<tr>
<td><code>completed</code></td>
<td><code>ContentViewer</code> muestra el contenido generado y los datos de evaluación del backend</td>
</tr>
<tr>
<td><code>failed</code></td>
<td>Banner de error con botón para reintentar desde <code>/new</code></td>
</tr>
</tbody>
</table>

</details>

<details>
<summary><strong>📌 Historial — <code>/history</code></strong></summary>
<br/>

Lista de adaptaciones con 4 filtros combinables en tiempo real.

<table>
<thead>
<tr><th>Filtro</th><th>Tipo</th><th>Opciones</th></tr>
</thead>
<tbody>
<tr><td>Búsqueda</td><td>Texto libre</td><td>Filtra por título del documento</td></tr>
<tr><td>Perfil</td><td>Selector</td><td>Principiante · Junior · Lider · Gestor</td></tr>
<tr><td>Formato</td><td>Selector</td><td>Flashcards · Tutorial · Quiz · Resumen Ejecutivo · Guion</td></tr>
<tr><td>Estado</td><td>Selector</td><td>completed · processing · pending · failed</td></tr>
</tbody>
</table>

Los filtros activos se muestran como badges con botón para limpiar todo. La lógica de filtrado está encapsulada en el hook `useHistoryFilters()`.

</details>

---

## 🤖 Progreso ilustrativo

`GenerationStatus` presenta cinco etapas visuales animadas. La página de resultados consulta al backend los estados `pending`, `processing`, `completed` y `failed`; la etapa resaltada avanza mediante un temporizador del navegador, no por eventos enviados por agentes. Los nombres de las etapas describen una representación visual, no componentes autónomos implementados.

El backend usa un solo motor de adaptación: recupera contexto RAG, genera contenido y calcula la puntuación de anclaje a partir de la similitud de recuperación. No existe un grafo LangGraph de cinco agentes, un agente crítico independiente ni un ciclo de regeneración guiado por su evaluación. El valor de evaluación mostrado en la interfaz no certifica calidad pedagógica independiente.

Consulte el [flujo completo del sistema](../README.md#flujo-completo-del-sistema) para la carga, el almacenamiento del original y la adaptación.

---

## 🧩 Widgets

Los widgets son bloques funcionales complejos con lógica propia. Cada uno tiene su propia carpeta dentro de `src/widgets/`.

---

### `AdaptationForm` — Formulario multi-paso

```mermaid
stateDiagram-v2
    [*] --> Perfil : inicia el formulario
    Perfil --> Formato : seleccionó perfil
    Formato --> Nicho : seleccionó formato
    Nicho --> Detalle : seleccionó nicho
    Detalle --> [*] : clic "Generar contenido"

    Perfil : 👤 Perfil\nPrincipiante · Junior · Lider · Gestor
    Formato : 📄 Formato\nFlashcards · Tutorial · Quiz · Resumen · Guion
    Nicho : 🏢 Nicho\nGeneral · Fintech · Salud · E-commerce
    Detalle : ⚙️ Detalle\nBásico · Intermedio · Didáctico · Detallado
```

**Props:**

```js
onSubmit(values)   // { profile, format, industry, detailLevel }
loading            // boolean — spinner en "Generar contenido" mientras procesa
```

**Sub-componentes internos:** `StepIndicator` · `OptionGrid` · `ProfileStep` · `FormatStep` · `IndustryStep` · `DetailStep`

---

### `ContentViewer` — Visualizador de resultados

Renderiza el contenido generado según el `format` de la adaptación. Cada formato tiene su propia vista especializada.

<table>
<thead>
<tr><th>Formato</th><th>Componente interno</th><th>Qué renderiza</th></tr>
</thead>
<tbody>
<tr>
<td>🃏 <strong>Flashcards</strong></td>
<td><code>FlashcardsView</code></td>
<td>Grid de 2 columnas — concepto (badge), pregunta, respuesta y fuente por tarjeta</td>
</tr>
<tr>
<td>📖 <strong>Tutorial</strong></td>
<td><code>TutorialView</code></td>
<td>Introducción destacada → pasos numerados con bloques de código → conclusión</td>
</tr>
<tr>
<td>📋 <strong>Resumen Ejecutivo</strong></td>
<td><code>ExecutiveSummaryView</code></td>
<td>Resumen → puntos clave con bullets → lista de riesgos en ámbar</td>
</tr>
<tr>
<td>🧠 <strong>Quiz</strong></td>
<td><code>QuizView</code></td>
<td>Preguntas con opciones A/B/C/D — respuesta correcta en verde + justificación</td>
</tr>
<tr>
<td>🎬 <strong>Guion</strong></td>
<td><code>GuionView</code></td>
<td>JSON formateado (vista provisional — schema pendiente de definir)</td>
</tr>
</tbody>
</table>

La interfaz presenta la puntuación y los criterios de evaluación recibidos del backend cuando están disponibles. Los cuatro criterios reutilizan la puntuación de anclaje; no son mediciones independientes ni el resultado de un agente crítico.

**Sub-componente:** `EvaluationBreakdown` — fidelidad · alineación al perfil · cumplimiento del formato · coherencia

---

### `DocumentUploader` — Zona de carga

Zona de carga con drag-and-drop. Valida el archivo localmente antes de enviarlo al backend.

**Validaciones locales:** extensión (`.pdf` · `.md` · `.txt`) · tamaño máximo 20 MB

<table>
<thead>
<tr><th>Estado</th><th>Borde</th><th>Ícono</th><th>Mensaje</th></tr>
</thead>
<tbody>
<tr><td>En espera</td><td>Punteado gris</td><td>☁️</td><td>Indicaciones para seleccionar el archivo</td></tr>
<tr><td>Dragging</td><td>Punteado brand</td><td>☁️ azul</td><td>"Suelta el archivo aquí"</td></tr>
<tr><td>Success</td><td>Verde sólido</td><td>✅</td><td>"¡Archivo cargado correctamente!"</td></tr>
<tr><td>Error</td><td>Rojo sólido</td><td>⚠️</td><td>Mensaje de error específico</td></tr>
</tbody>
</table>

**Props:**

```js
onFileSelect(file)  // llamado cuando el archivo pasa la validación local
uploading           // boolean — deshabilita la zona y muestra spinner
error               // string — error externo del backend
success             // boolean — marca la zona como exitosa
```

---

### `GenerationStatus` — Progreso ilustrativo

Muestra cinco etapas animadas ilustrativas, sin eventos de agentes del backend. Consulte [Progreso ilustrativo](#-progreso-ilustrativo).

**Props:**

```js
status          // 'pending' | 'processing' | 'completed' | 'failed'
currentAgent    // 'orchestrator' | 'researcher' | 'context' | 'generator' | 'critic'
iteration       // valor visual; la página de resultados usa 0 por defecto
maxIterations   // máximo visual configurado (por defecto: 3)
```

---

## 🗂️ Entities

Representaciones visuales de los objetos del dominio. Solo muestran datos, sin lógica de negocio.

---

### `AdaptationCard`

Tarjeta compacta de una adaptación. Usada en el dashboard y el historial.

**Muestra:** título del documento · etiquetas de perfil/formato/industria · estado con color semántico · fecha · puntuación de evaluación del backend

**Accesibilidad:** `role="button"` · `tabIndex={0}` · soporte teclado con `Enter` · `focus-ring`

**Props:**

```js
adaptation    // objeto Adaptation del dominio
onClick()     // función opcional — si se pasa, la tarjeta se vuelve interactiva
```

---

### `DocumentCard`

Tarjeta compacta de un documento cargado. También exporta `DocumentTypeIcon` para uso independiente.

<table>
<thead>
<tr><th>Tipo</th><th>Ícono</th><th>Color</th></tr>
</thead>
<tbody>
<tr><td>PDF</td><td>FileText</td><td>Rojo</td></tr>
<tr><td>Markdown</td><td>FileCode</td><td>Azul</td></tr>
<tr><td>TXT</td><td>File</td><td>Gris</td></tr>
</tbody>
</table>

**Props:**

```js
document        // objeto Document del dominio
onSelect(doc)   // función opcional — habilita el modo de selección
selected        // boolean — muestra checkmark brand cuando es true
```

---

## 📦 Shared — código reutilizable

Todo lo que puede ser importado desde cualquier capa sin lógica de negocio.

---

### `shared/ui/` — Sistema de diseño

<table>
<thead>
<tr><th>Componente</th><th>Variantes / Props clave</th><th>Descripción</th></tr>
</thead>
<tbody>
<tr>
<td><code>Button</code></td>
<td><code>primary · secondary · ghost · danger · success</code><br/><code>sm · md · lg</code> · <code>loading</code> · <code>fullWidth</code></td>
<td>Con <code>loading=true</code> muestra spinner y deshabilita automáticamente</td>
</tr>
<tr>
<td><code>Card</code></td>
<td><code>glass</code> (default: true) · <code>hover</code></td>
<td>Contenedor con glassmorphism. <code>hover=true</code> agrega cursor y efecto interactivo</td>
</tr>
<tr>
<td><code>CardHeader</code></td>
<td><code>title</code> · <code>action</code></td>
<td>Fila con título a la izquierda y acción a la derecha — se compone con <code>Card</code></td>
</tr>
<tr>
<td><code>Badge</code></td>
<td><code>default · brand · success · warning · danger · info · violet</code><br/><code>sm · md · lg</code> · <code>dot</code></td>
<td>Etiqueta pill-shaped. <code>dot=true</code> agrega círculo de color como indicador</td>
</tr>
<tr>
<td><code>Alert</code></td>
<td><code>success · error · warning · info</code> · <code>title</code></td>
<td>Banner con <code>role="alert"</code> para lectores de pantalla</td>
</tr>
<tr>
<td><code>EmptyState</code></td>
<td><code>icon · title · description · action</code></td>
<td>Estado vacío de listas con slot de acción personalizable</td>
</tr>
<tr>
<td><code>ScoreRing</code></td>
<td><code>score</code> (0–1) · <code>size</code> (px)</td>
<td>SVG circular de progreso. Verde ≥80% · Ámbar ≥60% · Rojo &lt;60%</td>
</tr>
<tr>
<td><code>Input</code></td>
<td><code>label · hint · error · leftIcon · rightIcon</code></td>
<td>Campo con <code>aria-invalid</code>, <code>aria-describedby</code> e id derivado del label</td>
</tr>
<tr>
<td><code>Select</code></td>
<td>Misma API que <code>Input</code></td>
<td>Renderiza <code>&lt;select&gt;</code> nativo con el mismo sistema de label/error</td>
</tr>
<tr>
<td><code>Spinner</code></td>
<td><code>sm · md · lg</code></td>
<td>Spinner animado con <code>role="status"</code> y <code>aria-label</code></td>
</tr>
<tr>
<td><code>PageLoader</code></td>
<td><code>message</code></td>
<td>Spinner centrado en pantalla completa con mensaje de carga</td>
</tr>
<tr>
<td><code>Skeleton</code></td>
<td><code>className</code> (define w/h con Tailwind)</td>
<td>Placeholder animado con pulse para contenido que está cargando</td>
</tr>
<tr>
<td><code>Sidebar</code></td>
<td>Sin props</td>
<td>Barra fija de 256px. Lee la ruta activa con <code>NavLink</code> automáticamente</td>
</tr>
</tbody>
</table>

---

### `shared/api/index.js` — Cliente HTTP

<table>
<thead>
<tr><th>Método</th><th>HTTP</th><th>Endpoint</th><th>Descripción</th></tr>
</thead>
<tbody>
<tr><td><code>documentsApi.upload(file)</code></td><td><code>POST</code></td><td><code>/api/v1/documents</code></td><td>Sube un archivo (multipart/form-data)</td></tr>
<tr><td><code>documentsApi.list()</code></td><td><code>GET</code></td><td><code>/api/v1/documents</code></td><td>Lista todos los documentos</td></tr>
<tr><td><code>documentsApi.get(id)</code></td><td><code>GET</code></td><td><code>/api/v1/documents/:id</code></td><td>Obtiene un documento por ID</td></tr>
<tr><td><code>documentsApi.delete(id)</code></td><td><code>DELETE</code></td><td><code>/api/v1/documents/:id</code></td><td>Elimina un documento</td></tr>
<tr><td><code>adaptationsApi.create(payload)</code></td><td><code>POST</code></td><td><code>/api/v1/adaptations</code></td><td>Inicia el proceso de generación</td></tr>
<tr><td><code>adaptationsApi.list(params)</code></td><td><code>GET</code></td><td><code>/api/v1/adaptations</code></td><td>Lista adaptaciones con filtros opcionales</td></tr>
<tr><td><code>adaptationsApi.get(id)</code></td><td><code>GET</code></td><td><code>/api/v1/adaptations/:id</code></td><td>Obtiene una adaptación completa</td></tr>
<tr><td><code>adaptationsApi.getStatus(id)</code></td><td><code>GET</code></td><td><code>/api/v1/adaptations/:id/status</code></td><td>Solo el estado — para polling durante generación</td></tr>
<tr><td><code>healthApi.check()</code></td><td><code>GET</code></td><td><code>/health</code></td><td>Verifica disponibilidad del backend</td></tr>
</tbody>
</table>

---

### `shared/hooks/`

<table>
<thead>
<tr><th>Hook</th><th>Retorna</th><th>Descripción</th></tr>
</thead>
<tbody>
<tr>
<td><code>useApi(apiFn)</code></td>
<td><code>{ data, loading, error, execute }</code></td>
<td>Wrapper genérico para funciones async. Elimina el boilerplate de loading/error en cada componente.</td>
</tr>
<tr>
<td><code>useLocalStorage(key, init)</code></td>
<td><code>[value, setValue]</code></td>
<td>Igual que <code>useState</code> pero persiste el valor en <code>localStorage</code> via JSON entre sesiones.</td>
</tr>
</tbody>
</table>

---

### `shared/utils/index.js`

<table>
<thead>
<tr><th>Función</th><th>Descripción</th><th>Ejemplo de salida</th></tr>
</thead>
<tbody>
<tr><td><code>cn(...classes)</code></td><td>Merge seguro de clases Tailwind via clsx + tailwind-merge</td><td><code>"px-4 bg-brand-600"</code></td></tr>
<tr><td><code>formatDate(date)</code></td><td>Fecha legible en español con hora</td><td><code>"15 sep 2026, 10:00"</code></td></tr>
<tr><td><code>formatFileSize(bytes)</code></td><td>Tamaño de archivo legible</td><td><code>"2.4 MB"</code></td></tr>
<tr><td><code>getProfileColor(profile)</code></td><td>Clases Tailwind de color según perfil</td><td><code>"text-emerald-400 bg-emerald-400/10"</code></td></tr>
<tr><td><code>getFormatColor(format)</code></td><td>Clases Tailwind de color según formato</td><td><code>"text-cyan-400 bg-cyan-400/10"</code></td></tr>
<tr><td><code>truncate(text, max)</code></td><td>Corta texto con <code>…</code> al superar el límite (default 60)</td><td><code>"Introducción a la Arq…"</code></td></tr>
</tbody>
</table>

---

## 🔌 Conexión con el backend

El frontend usa `VITE_API_URL` y el cliente compartido `src/shared/api/index.js` como frontera HTTP. La carga, el resultado y el historial consumen los endpoints versionados; el panel calcula estadísticas a partir de las listas de documentos y adaptaciones de la API, sin un endpoint específico de estadísticas. Solo las tarjetas de ejemplos permanecen estáticas.

<br/>

<table>
<thead>
<tr><th>Archivo</th><th>Estado actual</th><th>Endpoint compartido</th></tr>
</thead>
<tbody>
<tr>
<td><code>NewAdaptationPage.jsx</code></td>
<td>Carga real de documentos</td>
<td><code>documentsApi.upload(file)</code></td>
</tr>
<tr>
<td><code>NewAdaptationPage.jsx</code></td>
<td>Creación real de adaptaciones</td>
<td><code>adaptationsApi.create(payload)</code></td>
</tr>
<tr>
<td><code>ResultPage.jsx</code></td>
<td>Polling real de estado y carga del resultado completo</td>
<td><code>adaptationsApi.getStatus(id)</code> + <code>adaptationsApi.get(id)</code></td>
</tr>
<tr>
<td><code>DashboardPage.jsx</code></td>
<td>Estadísticas y adaptaciones recientes calculadas a partir de listas de la API; tarjetas de ejemplos estáticas</td>
<td><code>documentsApi.list()</code> + <code>adaptationsApi.list()</code></td>
</tr>
<tr>
<td><code>HistoryPage.jsx</code></td>
<td>Listado real con filtros de backend y búsqueda local por título</td>
<td><code>adaptationsApi.list(params)</code> con filtros</td>
</tr>
</tbody>
</table>

---

## 📐 Convenciones de código

<table>
<thead>
<tr><th>Área</th><th>Regla</th><th>Ejemplo</th></tr>
</thead>
<tbody>
<tr>
<td><strong>Exports</strong></td>
<td>Siempre named exports — nunca <code>export default</code></td>
<td><code>export function DashboardPage()</code></td>
</tr>
<tr>
<td><strong>Constantes</strong></td>
<td>UPPER_CASE al nivel del módulo</td>
<td><code>const AGENT_STEPS = [...]</code></td>
</tr>
<tr>
<td><strong>Sub-componentes</strong></td>
<td>JSX complejo → extraer con nombre descriptivo en el mismo archivo</td>
<td><code>function StatCard({ ... })</code></td>
</tr>
<tr>
<td><strong>Hooks custom</strong></td>
<td>Extraer cuando la lógica supera ~10 líneas</td>
<td><code>useDocumentUpload()</code>, <code>useHistoryFilters()</code></td>
</tr>
<tr>
<td><strong>Lookup maps</strong></td>
<td>Reemplazar ternarios encadenados con objetos de configuración</td>
<td><code>const VARIANT_CLASSES = { primary: '...' }</code></td>
</tr>
<tr>
<td><strong>Tailwind</strong></td>
<td>Siempre usar <code>cn()</code> — nunca template literals</td>
<td><code>cn('base', active && 'extra')</code></td>
</tr>
<tr>
<td><strong>Accesibilidad</strong></td>
<td><code>div</code> clickeables necesitan <code>role</code>, <code>tabIndex</code> y <code>onKeyDown</code></td>
<td><code>role="button" tabIndex={0}</code></td>
</tr>
<tr>
<td><strong>JSDoc</strong></td>
<td>Documentar props en todos los componentes exportados</td>
<td><code>@param {Adaptation} props.adaptation</code></td>
</tr>
</tbody>
</table>

---

## 🎨 Sistema de diseño

La aplicación usa **tema oscuro** como base. La paleta completa está definida en `tailwind.config.js`.

### Paleta de colores

```mermaid
graph LR
    subgraph PRIMARY["Colores primarios"]
        B["brand\n Índigo\n Acciones y navegación"]
        A["accent\n Violeta\n Gradientes y badges"]
    end

    subgraph SURFACE["Superficies — de más oscuro a más claro"]
        S1["slate-950\nFondo base"]
        S2["slate-900\nSidebar"]
        S3["slate-800\nCards"]
        S4["slate-700\nBordes"]
        S5["slate-600\nBordes hover"]
    end

    subgraph SEMANTIC["Colores semánticos"]
        SE1["🟢 emerald\nÉxito / Completado"]
        SE2["🟡 amber\nAdvertencia / Pendiente"]
        SE3["🔴 red\nError / Fallido"]
        SE4["🔵 blue\nInformación / Procesando"]
        SE5["🟣 violet\nFormato del contenido"]
    end

    style PRIMARY fill:#1e293b,stroke:#4f46e5,color:#e2e8f0
    style SURFACE fill:#1e293b,stroke:#334155,color:#e2e8f0
    style SEMANTIC fill:#1e293b,stroke:#059669,color:#e2e8f0
```

### Tipografía

**Fuente:** Inter — Google Fonts · Pesos usados: 300, 400, 500, 600, 700, 800

### Animaciones disponibles

<table>
<thead>
<tr><th>Clase Tailwind</th><th>Efecto</th><th>Duración</th><th>Dónde se usa</th></tr>
</thead>
<tbody>
<tr>
<td><code>animate-fade-in</code></td>
<td>Opacidad 0 → 1</td>
<td>0.3s ease-in-out</td>
<td>Páginas al cargar, contenido al aparecer</td>
</tr>
<tr>
<td><code>animate-slide-up</code></td>
<td>Sube 16px + fade-in</td>
<td>0.3s ease-out</td>
<td>Modales y elementos emergentes</td>
</tr>
<tr>
<td><code>animate-pulse-slow</code></td>
<td>Pulse suave</td>
<td>3s infinito</td>
<td>Indicadores de estado en progreso</td>
</tr>
</tbody>
</table>

---

<div align="center">

*NuevaMente · Programa ONE · Grupo 10*

</div>
