# NewMind Learning — Monorepo

Este repositorio está organizado como monorepo para separar el backend y el frontend del proyecto.

## Estructura

| Directorio | Propósito |
| --- | --- |
| `newmind-learning-backend/` | Backend Python con `main.py`, módulos `ingestion/`, `rag/`, `llm/`, `storage/`, `models/`, configuración, tests y dependencias. |
| `newmind-learning-frontend/` | Frontend React/Vite/Tailwind. |


## Inicio rápido con Docker

Este flujo es únicamente para desarrollo local; no representa una configuración lista para producción.

Desde la raíz del repositorio, levantá el stack completo:

```bash
docker compose up --build app frontend
```

Los servicios quedan disponibles en:

| Servicio | URL |
| --- | --- |
| Frontend | `http://localhost:5173` |
| Backend | `http://localhost:8000` |
| Salud del backend | `http://localhost:8000/health` |

### Iniciar cada servicio por separado

Todos los comandos se ejecutan desde la raíz del repositorio.

Solo backend:

```bash
docker compose up --build app
```

Solo frontend:

```bash
docker compose up --build frontend
```

Cada servicio usa su propio contexto e imagen:

| Servicio | Contexto de construcción | Imagen local |
| --- | --- | --- |
| `app` | `./newmind-learning-backend` | `newmind-learning-backend:local` |
| `frontend` | `./newmind-learning-frontend` | `newmind-learning-frontend:local` |

El frontend recibe `VITE_API_URL=http://localhost:8000`. Vite expone esa variable al código que se ejecuta en el navegador, por lo que la URL debe ser accesible desde el host. El nombre DNS `app` solo se resuelve dentro de la red de Compose y el navegador no puede usarlo.

> El frontend todavía usa flujos con datos mock. Levantar ambos servicios no demuestra por sí solo que esos flujos estén integrados con el backend.

Para detener los contenedores sin borrar datos persistidos:

```bash
docker compose down
```

Para detenerlos y borrar también los volúmenes locales de desarrollo:

```bash
docker compose down --volumes
```

## Variables de entorno

El backend puede ejecutarse sin credenciales externas usando los modos locales/emulados. Para usar proveedores reales, copiá el ejemplo del backend y completá las claves necesarias:

```bash
cp newmind-learning-backend/.env.example .env
```

Variables principales:

| Variable | Uso |
| --- | --- |
| `GEMINI_API_KEY` | API key opcional para Gemini. |
| `OPENAI_API_KEY` | API key opcional para OpenAI. |
| `ANTHROPIC_API_KEY` | API key opcional para Anthropic. |
| `APP_ENV` | Entorno de ejecución; por defecto `development`. |
| `LOG_LEVEL` | Nivel de logging; por defecto `INFO`. |
| `BACKEND_HOST` | Host interno del entrypoint backend; por defecto `0.0.0.0`. |
| `BACKEND_PORT` | Puerto interno del entrypoint backend; por defecto `8000`. |
| `VITE_API_URL` | URL del backend accesible desde el navegador; en el entorno Docker local usa `http://localhost:8000`. |

### OCI Object Storage real con Docker Compose

Para usar OCI real en Docker local, cada desarrollador debe configurar sus propios secretos fuera de Git. No compartas ni subas archivos `.env`, `docker-compose.override.yml`, OCID reales, fingerprints, namespaces reales ni claves privadas.

#### Identidad recomendada

- Para desarrollo local, cada desarrollador debe usar su propio usuario OCI, pertenecer al grupo `grp-nuevamente-storage` y generar su propia API key. Esto mantiene trazabilidad y evita compartir claves privadas.
- Para runtime, staging, producción o CI/CD, usá una identidad técnica dedicada al backend, por ejemplo `svc-nuevamente-storage`, con los mismos permisos mínimos requeridos.
- No compartas un PEM entre desarrolladores. Si esa clave se filtra, habría que rotarla para todo el equipo y se pierde trazabilidad de acciones.

1. Creá un `.env` en la raíz del repositorio con valores reales locales:

   ```env
   OCI_USER_OCID=
   OCI_FINGERPRINT=
   OCI_TENANCY_OCID=
   OCI_REGION=mx-queretaro-1
   OCI_KEY_FILE=/run/secrets/oci_api_key.pem
   OCI_OBJECT_STORAGE_NAMESPACE=
   OCI_BUCKET_DOCS=nuevamente-documentos-origen
   OCI_BUCKET_OUTPUTS=nuevamente-contenidos-educativos
   OCI_COMPARTMENT_ID=
   ```

2. Copiá el override de ejemplo y apuntalo a tu clave privada local:

   ```bash
   cp docker-compose.override.example.yml docker-compose.override.yml
   ```

   En Windows/PowerShell podés definir la ruta del PEM antes de levantar Compose:

   ```powershell
   $Env:OCI_PRIVATE_KEY_HOST_PATH="$Env:USERPROFILE\.oci\oci_api_key.pem"
   ```

   También podés reemplazar manualmente el lado izquierdo del volumen en `docker-compose.override.yml`. El lado derecho debe quedarse igual porque es la ruta que usa el contenedor:

   ```text
   /run/secrets/oci_api_key.pem
   ```

3. Validá la configuración expandida sin pegar la salida completa en chats o issues:

   ```bash
   docker compose config
   ```

   Debe aparecer el montaje hacia `/run/secrets/oci_api_key.pem`.

4. Levantá el backend y verificá health:

   ```bash
   docker compose up --build app
   curl http://localhost:8000/health
   ```

   Para confirmar que usa OCI real, el payload debe indicar `oci_mode: "oci"`, `real_oci_ready: true` y `local_fallback: false`.

> `OCI_CONFIG_FILE` y `OCI_CONFIG_PROFILE` siguen disponibles para ejecución local sin Docker, pero en Docker Compose se recomienda usar variables explícitas y montar solo el PEM como secreto de solo lectura. Un config file local de OCI normalmente contiene rutas Windows que no existen dentro del contenedor Linux.

## Perfil opcional de embeddings locales

La imagen base del backend mantiene OCI y dependencias necesarias, pero no incluye PyTorch ni `sentence-transformers` para evitar una imagen base pesada.

Para construir la variante con embeddings locales CPU-only:

```bash
docker compose --profile embeddings build app-embeddings
```

Para levantar esa variante:

```bash
docker compose --profile embeddings up app-embeddings
```

La variante de embeddings queda disponible en:

```text
http://localhost:8001/health
```

## Verificaciones útiles

Validar la configuración base:

```bash
docker compose config
```

Validar la configuración con el perfil de embeddings:

```bash
docker compose --profile embeddings config
```

Ejecutar tests del backend dentro del contenedor:

```bash
docker run --rm newmind-learning-backend:local pytest
```

## Frontend

El frontend vive en `newmind-learning-frontend/` y se mantiene separado de la imagen Docker del backend. Su imagen ejecuta el servidor de desarrollo de Vite en `0.0.0.0:5173`; no es una imagen de producción.
