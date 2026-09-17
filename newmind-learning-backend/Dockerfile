FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

ARG INSTALL_EMBEDDINGS=false

COPY requirements.txt .
COPY requirements-embeddings.txt .
RUN python -m pip install --upgrade pip \
    && python -m pip install -r requirements.txt \
    && if [ "$INSTALL_EMBEDDINGS" = "true" ]; then \
        python -m pip install -r requirements-embeddings.txt; \
    fi

COPY . .

RUN mkdir -p data/chroma_db data/oci_local_storage \
    && useradd --create-home --uid 10001 appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=3)"

CMD ["python", "-m", "main"]
