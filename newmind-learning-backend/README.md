# Backend de NewMind Learning

API REST construida con FastAPI para cargar documentos técnicos y generar
adaptaciones educativas según perfil, formato, industria y nivel de detalle.
El backend extrae e indexa contenido, recupera contexto con ChromaDB y genera
una adaptación mediante Gemini, OpenAI o una alternativa heurística local.

> Este documento describe el estado implementado actualmente. La arquitectura
> completa y sus reglas de dependencia se encuentran en
> [ARCHITECTURE.md](./ARCHITECTURE.md).

## Inicio rápido local

### Requisitos

- Python 3.11.
- `pip` y un entorno virtual de Python.
- Credenciales de LLM y OCI solo si se desean usar servicios externos. El
  proyecto dispone de alternativas locales para desarrollo.

Desde `newmind-learning-backend/`:

```bash
python -m venv .venv
```

Active el entorno virtual según su sistema operativo:

```bash
# Linux o macOS
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

Instale las dependencias y ejecute la API:

```bash
python -m pip install -r requirements.txt
python -m main
```

El servidor escucha en `0.0.0.0:8000` de forma predeterminada. Una vez
iniciado, están disponibles:

- salud: <http://localhost:8000/health>;
- documentación interactiva: <http://localhost:8000/docs>;
- contrato OpenAPI: <http://localhost:8000/openapi.json>.

La aplicación carga automáticamente un archivo `.env` ubicado en este
directorio. Puede tomar `.env.example` como referencia y mantener las claves
reales fuera del control de versiones. Sin `.env`, se aplican los valores
predeterminados declarados en `config/settings.py`.

## Capacidades implementadas

### Ingestión de documentos

El flujo de carga:

1. acepta un archivo multipart en formato PDF, Markdown (`.md`) o texto
   (`.txt`);
2. limita el contenido a **20 MiB** (`20 * 1024 * 1024` bytes);
3. normaliza el nombre y rechaza archivos vacíos, tipos no admitidos o texto no
   extraíble;
4. extrae el texto y lo divide en fragmentos;
5. indexa los fragmentos en una colección persistente de ChromaDB;
6. guarda el archivo original en OCI Object Storage o en su emulación local;
7. conserva los metadatos del documento en memoria durante la vida del proceso.

### Adaptación educativa

Una adaptación combina el documento con los valores admitidos por el contrato:

- perfiles: `Principiante`, `Junior`, `Senior`, `Lider` y `Gestor`;
- formatos: `Flashcards`, `Tutorial`, `Quiz`, `Resumen Ejecutivo` y `Guion`;
- industrias: `Fintech`, `Salud`, `E-commerce` y `General`;
- niveles: `Basico`, `Intermedio`, `Didactico` y `Detallado`.

La creación registra un trabajo con estado `pending` y responde antes de
procesarlo. FastAPI ejecuta el trabajo mediante `BackgroundTasks`; después pasa
por `processing` y termina como `completed` o `failed`. El cliente puede sondear
el endpoint de estado mientras se ejecutan la recuperación RAG, la generación y
la persistencia del resultado.

La selección de generación actual intenta, en este orden:

1. Gemini, si existe `GEMINI_API_KEY`, con `gemini-1.5-flash`;
2. OpenAI, si existe `OPENAI_API_KEY`, con `gpt-4o-mini`;
3. el generador heurístico local si no hay claves o fallan ambos proveedores.

Los resultados educativos se guardan como JSON en OCI Object Storage o en el
almacenamiento local emulado.

## API HTTP

Todos los endpoints funcionales están versionados bajo `/api/v1`, excepto la
salud y la documentación automática.

### Documentos

| Método | Ruta | Respuesta principal | Errores relevantes |
| --- | --- | --- | --- |
| `POST` | `/api/v1/documents` | `201`, documento creado | `413` si supera 20 MiB; `422` para tipo, contenido, extracción, indexación o almacenamiento inválidos |
| `GET` | `/api/v1/documents` | `200`, lista de documentos | — |
| `GET` | `/api/v1/documents/{document_id}` | `200`, documento | `404` si no existe |
| `DELETE` | `/api/v1/documents/{document_id}` | `204`, sin cuerpo | `404` si no existe |

Ejemplo de carga:

```bash
curl --fail \
  -F "file=@./data/samples/documento.txt" \
  http://localhost:8000/api/v1/documents
```

### Adaptaciones

| Método | Ruta | Respuesta principal | Errores relevantes |
| --- | --- | --- | --- |
| `POST` | `/api/v1/adaptations` | `202`, trabajo aceptado en estado inicial | `404` si el documento no existe; `422` para un cuerpo inválido |
| `GET` | `/api/v1/adaptations` | `200`, lista filtrable | `422` para un valor de filtro inválido |
| `GET` | `/api/v1/adaptations/{adaptation_id}` | `200`, estado y resultado completo | `404` si no existe |
| `GET` | `/api/v1/adaptations/{adaptation_id}/status` | `200`, estado mínimo para sondeo | `404` si no existe |

La lista admite los filtros opcionales `profile`, `format` y `status`. Los
estados válidos son `pending`, `processing`, `completed` y `failed`.

Ejemplo de creación, después de cargar el documento con identificador `1`:

```bash
curl --fail \
  -H "Content-Type: application/json" \
  -d '{
    "documentId": 1,
    "profile": "Principiante",
    "format": "Flashcards",
    "industry": "General",
    "detailLevel": "Basico"
  }' \
  http://localhost:8000/api/v1/adaptations
```

Consulte el estado con el identificador devuelto:

```bash
curl --fail http://localhost:8000/api/v1/adaptations/1/status
```

## Arquitectura y estructura

La regla principal de dependencias es **API → aplicación → dominio/capacidades
→ infraestructura**. Los routers gestionan HTTP y delegan la coordinación a
servicios de aplicación; los DTO públicos y los modelos del dominio se mantienen
separados mediante mapeadores explícitos.

```text
newmind-learning-backend/
├── api/                  # Routers v1, DTO, dependencias y mapeadores
├── application/          # Casos de uso y repositorios en memoria
├── config/               # Configuración basada en entorno y .env
├── ingestion/            # Extracción y fragmentación de documentos
├── llm/                  # Prompts, proveedores y alternativa heurística
├── models/               # Contratos y enumeraciones del dominio
├── rag/                  # ChromaDB y recuperación de contexto
├── storage/              # OCI Object Storage y emulación local
├── tests/                # Pruebas de API, dominio e integraciones locales
├── ARCHITECTURE.md       # Diseño, fronteras y decisiones detalladas
├── Dockerfile            # Imagen Python 3.11 sin usuario root
├── main.py               # Composición y punto de entrada FastAPI
├── requirements.txt      # Dependencias base y de pruebas
└── requirements-embeddings.txt # Perfil opcional de embeddings locales
```

Consulte [Arquitectura del backend](./ARCHITECTURE.md) para los diagramas, el
mapeo API-dominio, las responsabilidades por capa y las reglas de evolución.

## Configuración

### Ejecución

| Variable | Valor predeterminado | Uso actual |
| --- | --- | --- |
| `APP_ENV` | `development` | Etiqueta el entorno expuesto por salud. |
| `LOG_LEVEL` | `INFO` | Configura el nivel de logging al ejecutar `python -m main`. |
| `CORS_ORIGINS` | `http://localhost:5173` | Lista de orígenes permitidos, separada por comas. |
| `BACKEND_HOST` | `0.0.0.0` | Host de Uvicorn; se consulta directamente al iniciar. |
| `BACKEND_PORT` | `8000` | Puerto de Uvicorn; se consulta directamente al iniciar. |

### Proveedores LLM

| Variable | Uso actual |
| --- | --- |
| `GEMINI_API_KEY` | Habilita el primer intento de generación con Gemini. |
| `OPENAI_API_KEY` | Habilita OpenAI como segundo intento. |
| `ANTHROPIC_API_KEY` | Está declarada y se pasa por Compose, pero Anthropic **no está implementado** en el motor. |
| `DEFAULT_LLM_PROVIDER` | Está declarada, pero actualmente **no controla** la selección; el orden Gemini → OpenAI → heurístico está codificado. |
| `DEFAULT_LLM_MODEL` | Está declarada, pero actualmente **no controla** los modelos; estos están fijados en el motor. |

### OCI Object Storage

| Variable | Uso |
| --- | --- |
| `OCI_CONFIG_FILE` | Ruta al archivo de configuración; predeterminado `~/.oci/config`. |
| `OCI_CONFIG_PROFILE` | Perfil del archivo; predeterminado `DEFAULT`. |
| `OCI_COMPARTMENT_ID` | OCID de compartment declarado para configuración OCI. |
| `OCI_USER_OCID` | OCID del usuario para autenticación explícita. |
| `OCI_FINGERPRINT` | Huella de la clave API. |
| `OCI_TENANCY_OCID` | OCID del tenancy. |
| `OCI_REGION` | Región; predeterminado `us-ashburn-1`. |
| `OCI_KEY_FILE` | Ruta de la clave privada. |
| `OCI_OBJECT_STORAGE_NAMESPACE` | Namespace de Object Storage. |
| `OCI_BUCKET_DOCS` | Bucket de originales; predeterminado `nuevamente-documentos-origen`. |
| `OCI_BUCKET_OUTPUTS` | Bucket de resultados; predeterminado `nuevamente-contenidos-educativos`. |

Si no hay un archivo OCI utilizable ni una configuración explícita completa,
el cliente utiliza `data/oci_local_storage/` como emulación local.

### RAG y fragmentación

| Variable | Valor predeterminado | Uso actual |
| --- | --- | --- |
| `CHROMA_PERSIST_DIR` | `data/chroma_db` | Directorio persistente de ChromaDB. |
| `DEFAULT_CHUNK_SIZE` | `1000` | Tamaño de fragmento en caracteres. |
| `DEFAULT_CHUNK_OVERLAP` | `150` | Solapamiento entre fragmentos. |
| `TOP_K_RETRIEVAL` | `4` | Máximo solicitado para recuperación semántica. |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Está declarada, pero actualmente **no se conecta** a la función de embeddings de ChromaDB. |

## Docker

El archivo `docker-compose.yml` de la raíz define solo los servicios actuales del
backend:

- `app`: imagen base, publicada en <http://localhost:8000>;
- `app-embeddings`: perfil opcional `embeddings`, publicado en
  <http://localhost:8001> y construido con dependencias adicionales de CPU.

Desde la raíz del repositorio:

```bash
docker compose up -d --build app
curl --fail http://localhost:8000/health
docker compose down
```

Para construir y ejecutar también el perfil opcional:

```bash
docker compose --profile embeddings up -d --build
```

Ambos servicios montan los volúmenes nombrados `chroma-data` y
`local-storage`. La imagen usa Python 3.11, ejecuta el proceso con el usuario no
privilegiado `appuser`, expone el puerto `8000` y define un `HEALTHCHECK` contra
`/health`.

`requirements-embeddings.txt` agrega PyTorch CPU y `sentence-transformers` para
el perfil opcional. Sin embargo, el código actual no selecciona explícitamente
ese modelo ni usa `EMBEDDING_MODEL`; ChromaDB conserva su función de embeddings
predeterminada. Por ello, el perfil instala capacidades adicionales, pero no
garantiza por sí solo un cambio de implementación de embeddings.

## Pruebas

Desde `newmind-learning-backend/`, ejecute:

```bash
python -m pytest
```

La suite cubre:

- contrato HTTP, salud y OpenAPI;
- carga, listado, consulta y eliminación de documentos;
- saneamiento de nombres, tipos admitidos y límite de tamaño;
- creación, mapeo, filtros y consulta de adaptaciones;
- validación de esquemas del dominio;
- extracción y fragmentación;
- generación heurística del motor LLM;
- persistencia local y diagnóstico de configuración OCI.

El repositorio no configura comandos de lint ni de comprobación estática de
tipos para este backend; no deben asumirse como parte de la verificación actual.

## Limitaciones conocidas

- **Metadatos en memoria:** documentos, trabajos, estados y resultados se
  pierden al reiniciar el proceso y no se comparten entre réplicas.
- **Trabajos no durables:** `BackgroundTasks` no aporta cola persistente,
  reintentos ni recuperación de trabajos interrumpidos.
- **Eliminación incompleta:** `DELETE /documents/{id}` elimina el registro en
  memoria, pero no limpia el objeto almacenado ni sus vectores en ChromaDB.
- **Carga parcialmente transaccional:** si el almacenamiento falla después de
  indexar los fragmentos, se elimina el metadato en memoria, pero pueden quedar
  vectores huérfanos.
- **Salud superficial:** `/health` informa configuración y modo de ejecución,
  pero no realiza operaciones reales contra ChromaDB, OCI ni proveedores LLM.
- **Selección LLM parcialmente codificada:** el orden y los modelos de Gemini y
  OpenAI no obedecen todavía a `DEFAULT_LLM_PROVIDER` ni
  `DEFAULT_LLM_MODEL`.
- **Anthropic no implementado:** la clave existe en configuración y Compose,
  pero no hay un adaptador que la utilice.
- **Perfil de embeddings sin cableado explícito:** instalar
  `requirements-embeddings.txt` no cambia por sí mismo la función usada por
  ChromaDB, y `EMBEDDING_MODEL` no está conectado.
- **Adquisición inicial de modelos:** la función de embeddings predeterminada de
  ChromaDB puede necesitar descargar recursos en el primer uso, según el estado
  del entorno y su caché.
- **Efectos locales:** importar o ejecutar la aplicación y algunas pruebas puede
  crear o modificar `data/chroma_db/` y `data/oci_local_storage/`.

Estas restricciones corresponden al MVP actual; no representan garantías de
persistencia, disponibilidad o escalabilidad productiva.

## Referencias

- [Arquitectura del backend](./ARCHITECTURE.md).
- [Configuración de ejemplo](./.env.example).
- [Dependencias base](./requirements.txt).
- [Dependencias opcionales de embeddings](./requirements-embeddings.txt).
- Contrato ejecutable: `/openapi.json`.
- Explorador interactivo: `/docs`.
