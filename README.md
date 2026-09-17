# NewMind Learning — Monorepo

Este repositorio está organizado como monorepo para separar el backend y el frontend del proyecto.

## Estructura

| Directorio | Propósito |
| --- | --- |
| `newmind-learning-backend/` | Backend Python con `main.py`, módulos `ingestion/`, `rag/`, `llm/`, `storage/`, `models/`, configuración, tests y dependencias. |
| `newmind-learning-frontend/` | Frontend React/Vite/Tailwind. |


## Inicio rápido con Docker

Desde la raíz del repositorio:

```bash
docker compose up --build app
```

El backend queda disponible en:

```text
http://localhost:8000/health
```

El servicio `app` construye el backend usando este contexto:

```text
./newmind-learning-backend
```

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

El frontend vive en `newmind-learning-frontend/` y se mantiene separado de la imagen Docker del backend. La configuración Docker del frontend se trabajará en una Issue independiente.
