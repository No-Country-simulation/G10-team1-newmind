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
