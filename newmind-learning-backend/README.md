# Backend de NewMind Learning

API REST construida con FastAPI para cargar documentos técnicos y generar
adaptaciones educativas según perfil, formato, industria y nivel de detalle.
El backend extrae e indexa contenido, recupera contexto con ChromaDB y genera
una adaptación mediante Gemini, Grok, OpenAI o una alternativa heurística local.

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

Para habilitar Grok en ejecución local, agregue `GROK_API_KEY=<clave_de_xai>`
al `.env` privado del backend o expórtela como variable de entorno. Con Docker
Compose, defina `GROK_API_KEY` en el entorno de Compose (por ejemplo, en el
`.env` privado de la raíz); ambos perfiles de backend la reciben. No incluya
claves reales en archivos versionados ni en el frontend.

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

1. Gemini, si existe `GEMINI_API_KEY`, con `gemini-3.1-flash-lite`;
2. Grok, si existe `GROK_API_KEY`, con `grok-4.7` mediante la API compatible
   con OpenAI de xAI (`https://api.x.ai/v1`);
3. OpenAI, si existe `OPENAI_API_KEY`, con `gpt-4o-mini`;
4. el generador heurístico local si no hay claves o fallan los proveedores.

Las respuestas de proveedores se solicitan en modo JSON. Si una llamada falla,
devuelve JSON mal formado o no cumple la estructura requerida (incluidos los
elementos de flashcards, quiz y tutorial), se intenta el siguiente proveedor
sin registrar credenciales ni detalles de excepciones. Los formatos resumen y
guion admiten elementos flexibles; no se valida la exactitud pedagógica ni el
anclaje factual del texto generado. La respuesta final se valida antes de
persistirse en OCI.

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

### Evidencia de almacenamiento de originales (CLO-02)

Las respuestas de carga, listado y detalle incluyen `filename` (nombre original)
y `storage`: `mode`, `status`, `bucket`, `objectId`, `etag` y `errorCode`.
La clave usa UUID y un nombre saneado; no es una ruta local ni el nombre original.
Los bytes originales y el tipo MIME se conservan al escribir el objeto.

| Resultado | Interpretación |
| --- | --- |
| `local_emulation` / `completed` | Emulación local inicial; no demuestra persistencia en OCI. |
| `local_emulation` / `local_fallback` | Falló la escritura OCI; `errorCode=oci_write_failed`; solo hay copia local. |
| `oci` / `completed` | La escritura OCI respondió; aún se necesita lectura independiente. |

`storage.verify_document_storage` no carga configuración
ni crea clientes. Recibe el resultado, los bytes originales, el bucket y la clave
esperados. Para emulación requiere `local_root` explícito y devuelve `LOCAL`
solo si el archivo existe y coincide byte a byte. Para OCI requiere cliente y
namespace explícitos, comprueba `head_object` (estado y tamaño), `get_object`
(estado y bytes) y ETag si existe. `require_oci=True` rechaza toda emulación o
fallback. Cualquier comprobación fallida genera `VerificationError`, sin detalles
privados del proveedor. No busque el objeto usando únicamente el nombre original.

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
| `GEMINI_API_KEY` | Habilita el primer intento con Gemini. |
| `GROK_API_KEY` | Habilita Grok como segundo intento. |
| `OPENAI_API_KEY` | Habilita OpenAI como tercer intento. |
| `ANTHROPIC_API_KEY` | Está declarada y se pasa por Compose, pero Anthropic **no está implementado** en el motor. |
| `DEFAULT_LLM_PROVIDER` | Está declarada, pero actualmente **no controla** la selección; el orden Gemini → Grok → OpenAI → heurístico está codificado. |
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

`DEFAULT_CHUNK_SIZE` y `DEFAULT_CHUNK_OVERLAP` se miden con el conteo de
caracteres de Python (`len` y cortes de cadenas), no en bytes, tokens ni grafemas.
Cada fragmento contiene como máximo `DEFAULT_CHUNK_SIZE` caracteres. Dentro de
esa ventana, el fragmentador prefiere el último separador de párrafo completo
(`\n\n`) que aporte contenido nuevo; el separador queda incluido al final del
fragmento. El fragmento siguiente comienza exactamente
`DEFAULT_CHUNK_OVERLAP` caracteres antes del extremo seleccionado.

Si no cabe un separador de párrafo utilizable —incluidos los párrafos que por
sí solos superan el tamaño configurado—, el extremo se fija mediante un corte
duro de `DEFAULT_CHUNK_SIZE` caracteres. El último fragmento se emite una sola
vez con todo el contenido restante: nunca se agrega un fragmento terminal que
contenga únicamente solapamiento ya emitido.

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

### Evidencia de proveedores

**Primero ejecute la matriz sin red.** Desde `newmind-learning-backend/`:

```bash
python -B -m pytest -p no:cacheprovider tests/test_llm_engine.py tests/test_llm_provider_smoke.py -q
```

Estas pruebas aíslan `config.settings`, RAG y OCI **antes** de importar el motor:
no cargan `.env`, no inicializan Chroma ni almacenamiento y usan dobles de SDK.
Restauran los módulos al terminar. Las claves ambientales no habilitan llamadas
reales por sí solas. Una prueba omitida no demuestra ejecución de un proveedor.

| Configuración mínima del motor | Selección esperada si responde con JSON válido |
| --- | --- |
| Ninguna clave LLM | Heurístico local; sin importación de SDK. |
| Solo `GEMINI_API_KEY` | Gemini, `gemini-3.1-flash-lite`. |
| Solo `GROK_API_KEY` | Grok, `grok-4.7`, destino `https://api.x.ai/v1`. |
| Solo `OPENAI_API_KEY` | OpenAI, `gpt-4o-mini`. |
| Varias claves | Primer éxito válido en orden Gemini → Grok → OpenAI; luego heurístico. |

No se necesita una clave OCI para estas pruebas. Mantenga las claves no elegidas
sin configurar en una prueba real. `DEFAULT_LLM_PROVIDER` y `DEFAULT_LLM_MODEL`
no cambian este orden ni los modelos codificados. Si un modelo no está disponible
para la cuenta, registre el bloqueo: no lo sustituya para obtener evidencia.

| Caso de regresión | Prueba identificable en `tests/test_llm_engine.py` |
| --- | --- |
| Sin claves, sin SDK | `test_no_keys_uses_heuristic_without_importing_providers` |
| Primer proveedor disponible | `test_gemini_wins_when_both_keys_are_configured`, `test_no_gemini_key_uses_grok_endpoint_and_json_mode`, `test_only_openai_key_selects_openai_and_hardcoded_model` |
| Error o JSON mal formado | `test_gemini_failure_falls_through_to_grok_then_openai`, `test_invalid_grok_uses_next_available_openai` |
| Esquema incompatible | `test_invalid_gemini_payload_falls_through_to_grok_without_leaking_details`, `test_invalid_openai_payload_uses_heuristic_before_upload` |
| Proveedores agotados | `test_all_providers_fail_and_heuristic_remains_available` |

La lista `items=[]` sigue siendo válida según el contrato actual. Esta matriz
demuestra selección y validación deterministas, no calidad factual ni acceso real.

#### Smoke real controlado

La [evidencia sanitizada de la issue 56](../docs/issue-56-gemini-smoke-evidence.json)
registra en `latest_attempt` una respuesta real de Gemini validada por el motor el
2026-10-12 a las 20:22:42 UTC, con una invocación y sin reintentos. No contiene
credenciales ni el contenido de la respuesta. Cada ejecución posterior requiere
una nueva autorización; este resultado no prueba toda la infraestructura ni audita
la facturación.

No ejecute este paso sin autorización explícita del responsable para **un**
proveedor/modelo, destino, origen de credenciales y presupuesto. Gemini usa la
API de Google mediante `google.generativeai`; OpenAI usa `https://api.openai.com/v1`
mediante su SDK. Grok no está habilitado para este smoke.

Después de esa autorización, configure en un proceso dedicado, sin cargar `.env`:

- `NEWMIND_SMOKE_GATE=authorized` (cualquier otro valor falla);
- `NEWMIND_SMOKE_PROVIDER=gemini` **o** `openai`;
- `NEWMIND_SMOKE_ENVIRONMENT=env-01234567`: reemplace el sufijo por un identificador
  opaco de 8–16 caracteres `[a-z0-9]`, sin nombres, rutas ni datos personales;
- únicamente la clave correspondiente, suministrada por el origen autorizado,
  sin escribirla en comandos, historial, registros ni archivos versionados.

```bash
python -B -m pytest -p no:cacheprovider tests/test_llm_provider_smoke.py::test_real_provider_smoke -q -s
```

El gate se valida antes de acceder a la clave o importar SDK. Controles parciales,
alias inválido o credencial ausente fallan de forma segura. El smoke usa texto
sintético y `_call_llm` real, deshabilita las otras claves y rechaza el heurístico;
aplica la validación del motor sin recuperación RAG ni persistencia. Un fallo de
proveedor o esquema no se acepta como éxito. No cambia SDK ni contrato.

#### Excepción de modelo y límites de Gemini (issue 56)

El usuario autorizó explícitamente reemplazar el modelo retirado `gemini-1.5-flash`
por `gemini-3.1-flash-lite` en producción y en la evidencia de este smoke, como
excepción al alcance original. No hay sustitución automática posterior. Se mantienen
el orden Gemini → Grok → OpenAI → heurístico, los otros modelos y el SDK existente.

Solo el smoke Gemini limita la generación a **una invocación de alto nivel**:
`request_options={"retry": None, "timeout": 30}`, `max_output_tokens=1024` y
`candidate_count=1`. Conserva `response_mime_type="application/json"` y solicita
una única flashcard breve con texto sintético. Los parches de fábrica y método
se restauran al salir, incluso ante errores; no se modifica la configuración de
generación de producción. El timeout limita la solicitud del SDK, no garantiza
un límite total de todas las operaciones de red del sistema operativo. Si la firma
del SDK no admite estas opciones, el smoke falla antes de generar. Un error de
cuota bloquea la evidencia: no se reintenta automáticamente ni se cambia de modelo.

El usuario declara que la cuenta usa el nivel gratuito; esto **no demuestra** el
estado de facturación ni constituye un límite monetario verificable localmente.
No se activa facturación ni se ejecuta una API como parte de este cambio local.
La tarifa gratuita incluye entrada y salida (también tokens de razonamiento),
pero los datos del nivel gratuito pueden utilizarse para mejorar productos de Google.
Se necesita autorización remota separada y confirmación de presupuesto pagado cero.

Fuentes primarias verificadas para esta decisión:

- [Changelog](https://ai.google.dev/gemini-api/docs/changelog): disponibilidad general
  de `gemini-3.1-flash-lite` desde el 7 de mayo de 2026.
- [Deprecaciones](https://ai.google.dev/gemini-api/docs/deprecations): cierre previsto
  el 7 de mayo de 2027.
- [Precios](https://ai.google.dev/gemini-api/docs/pricing): condiciones del nivel gratuito.
- [Modelo](https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-lite):
  soporte de JSON y `generate_content`.

El SDK acepta nombres de modelo sin lista cerrada: existe compatibilidad estructural,
no evidencia de compatibilidad instalada ni de ejecución real exitosa. El smoke
permanece deshabilitado sin todos los controles explícitos, incluso si hay claves.

Con `-s`, un éxito emite solo JSON con `provider`, `model`, `utc`, `environment`
y `validation`. No incluya respuestas, excepciones, claves, entorno completo ni
rutas privadas en la evidencia. Los errores se reducen a mensajes constantes,
sin traceback de proveedor; la salida y los registros del SDK se descartan.
Una ejecución real todavía pendiente no se reemplaza por resultados de dobles.

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
- **Selección LLM parcialmente codificada:** el orden y los modelos de Grok,
  Gemini y OpenAI no obedecen todavía a `DEFAULT_LLM_PROVIDER` ni
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
