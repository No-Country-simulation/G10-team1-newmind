# 🎓 NuevaMente

**Sistema Inteligente de Adaptación y Generación de Contenido Educativo**

Proyecto desarrollado para el **Hackathon ONE G10 — Oracle Next Education & Alura**.

## 📌 Descripción

NuevaMente es una aplicación que utiliza **IA Generativa + RAG** para transformar documentación técnica en contenido educativo adaptado a diferentes perfiles de usuarios.

El sistema permite cargar documentos técnicos y seleccionar:

* 👤 Perfil del destinatario
* 📚 Formato pedagógico
* 🏢 Nicho o contexto de aplicación
* 📊 Nivel de detalle

A partir de estos parámetros, la aplicación procesa el documento y genera contenido educativo estructurado.

## 🎯 Objetivo

Convertir documentación técnica compleja en material educativo **personalizado, estructurado y fundamentado en la fuente original**, reduciendo el tiempo necesario para crear contenidos de aprendizaje.

## 🧠 Funcionamiento

```text
Documento
    ↓
Extracción de texto
    ↓
Chunking
    ↓
Embeddings
    ↓
Vector Store
    ↓
Búsqueda semántica (RAG)
    ↓
LLM
    ↓
Adaptación del contenido
    ↓
Validación
    ↓
JSON educativo
    ↓
OCI Object Storage
```

## 👤 Perfiles

El contenido puede adaptarse a diferentes tipos de usuarios:

* Principiante / Transición de Carrera
* Desarrollador Junior / Semi Senior
* Líder Técnico / Arquitecto
* Gestor / Ejecutivo No Técnico

## 📚 Formatos

NuevaMente puede generar diferentes formatos educativos:

* Guía práctica paso a paso
* Flashcards
* Quiz interactivo
* Resumen ejecutivo (TL;DR)
* Guion de clase / video

## 🏢 Contextos

* Fintech
* Salud
* E-commerce
* General

## 🤖 IA y RAG

El proyecto utiliza una arquitectura RAG para recuperar información relevante desde la documentación original antes de generar el contenido.

Componentes principales:

* Extracción de documentos
* Chunking
* Embeddings
* Búsqueda vectorial
* LLM
* Prompt Engineering
* Validación de respuestas
* Generación estructurada en JSON

## ☁️ OCI

Se utiliza **Oracle Cloud Infrastructure (OCI) Object Storage** para almacenar:

* Documentos originales.
* Contenidos educativos generados.
* Archivos JSON.

El almacenamiento debe utilizar la **capa Always Free de OCI**.

## 🛠️ Stack tecnológico

### Backend

* Python
* FastAPI
* Pydantic

### IA

* RAG
* LangChain
* LangGraph
* LLM
* Embeddings

### Vector Store

* ChromaDB / FAISS

### Frontend

* Streamlit / Gradio

### Cloud

* Oracle Cloud Infrastructure
* OCI Object Storage

### Control de versiones

* Git
* GitHub

## 📁 Estructura del proyecto

```text
newmind-learning/
│
├── backend/
│   ├── api/
│   ├── agents/
│   ├── rag/
│   ├── services/
│   ├── models/
│   └── main.py
│
├── frontend/
│
├── tests/
│
├── docs/
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## 🚀 Objetivo del MVP

El MVP debe permitir:

* Cargar documentos PDF, Markdown o texto.
* Procesar e indexar el contenido.
* Realizar búsqueda mediante RAG.
* Adaptar el contenido según el perfil seleccionado.
* Generar diferentes formatos educativos.
* Retornar información estructurada en JSON.
* Almacenar documentos y resultados en OCI Object Storage.
* Contar con una interfaz web o API funcional.

## 🧪 Demostración

Se deben demostrar al menos **3 escenarios de adaptación** utilizando documentación técnica.

Ejemplo:

```text
Mismo documento
      │
      ├── Principiante → Flashcards
      │
      ├── Desarrollador Junior → Tutorial
      │
      └── Ejecutivo → Resumen Ejecutivo
```

## 👥 Equipo

**Hackathon ONE G10 — NuevaMente**

Proyecto colaborativo desarrollado durante el programa **Oracle Next Education (ONE)**.

---

> 🚀 **NuevaMente:** transforma documentación técnica en aprendizaje personalizado mediante Inteligencia Artificial.
