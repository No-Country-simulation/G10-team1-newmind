#!/bin/bash
# ==============================================================================
# Script de Inicio Rápido para NuevaMente (Hackathon ONE G10)
# ==============================================================================

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR" || exit 1

if [ ! -d "venv" ]; then
    echo "⚠️ Entorno virtual no encontrado. Creando entorno con uv..."
    uv venv --python 3.11 venv
    uv pip install -r requirements.txt --python ./venv/bin/python
fi

echo "🚀 Iniciando NuevaMente Streamlit UI..."
./venv/bin/streamlit run ui/app.py --server.port 8501 --server.address 0.0.0.0
