# Proyecto 1 – 🎓 NuevaMente – Sistema Inteligente de Adaptación y Generación de Contenido Educativo
**Programa ONE · Grupo 10 | Hackathon ONE G10 — Oracle Next Education & Alura**

---

## 1. Mapeo de Formaciones ONE (Grupo 10)
- **Formaciones Indispensables:** Inteligencia de Datos y RAG Avanzado y Oracle Cloud Infrastructure (OCI).
- **Formaciones de Refuerzo:** Ingeniería de Agentes y Automatización con IA y Desarrollo y Orquestación con IA Generativa.
- **Núcleo Técnico:** Pipeline de RAG (Retrieval-Augmented Generation) con segmentación (chunking), generación de embeddings y búsqueda vectorial en Vector Store para anclar el contenido didáctico con fidelidad en las fuentes técnicas originales, integrado a **OCI Object Storage en la capa Always Free**.

---

## 2. Sector Empresarial
**EdTech / Capacitación Corporativa / Plataformas de Educación Técnica:** Aplicaciones y servicios orientados a la democratización y aceleración del aprendizaje técnico. El sector atiende a instituciones educativas, empresas de tecnología y equipos de ingeniería que necesitan capacitar a públicos diversos (desde principiantes en transición de carrera hasta líderes técnicos y arquitectos) a partir de documentaciones, manuales y materiales técnicos densos y en constante evolución.

---

## 3. Descripción del Proyecto
Crear una solución inteligente capaz de ingerir documentaciones técnicas, manuales de software, artículos o bases de conocimiento y transformarlos automáticamente en contenidos educativos personalizados y estructurados según el perfil del destinatario, la industria de aplicación y el formato pedagógico de salida elegido.

Hoy en día, la creación y adaptación manual de materiales didácticos a partir de documentaciones complejas es un proceso lento que consume semanas de trabajo de especialistas y diseñadores instruccionales. La solución **NuevaMente** debe utilizar técnicas de IA Generativa, RAG (Retrieval-Augmented Generation) y Orquestación de Agentes para automatizar este flujo, garantizando fidelidad técnica (anclaje en las fuentes originales) y adecuación pedagógica.

### Criterios de Parametrización:
- **Perfil del Destinatario:**
  - Principiante / Transición de Carrera
  - Desarrollador Junior / Semi Senior
  - Líder Técnico / Arquitecto
  - Gestor / Ejecutivo (No Técnico)
- **Formato Pedagógico de Salida:**
  - Guía Práctica Paso a Paso (Tutorial)
  - Flashcards de Memorización
  - Quiz Interactivo con Justificaciones
  - Resumen Ejecutivo (TL;DR)
  - Guion de Clase / Video
- **Nicho / Contexto de Aplicación:**
  - Fintech
  - Salud
  - E-commerce
  - General
- **Nivel de Detalle:**
  - Didáctico, Técnico, Ejecutivo, etc.

---

## 4. Requisitos de Inteligencia de la Aplicación
1. **Extraer e indexar** el contenido técnico utilizando técnicas de RAG (segmentación en chunks y embeddings vectoriales) para fundamentar las respuestas.
2. **Orquestar un flujo de agentes o cadenas de prompts** utilizando LLMs (Google Gemini, OpenAI ChatGPT/GPT-4o, Anthropic Claude, Grok, Ollama o equivalentes) para reescribir, ejemplificar y estructurar el contenido en el nivel de profundidad y tono adecuados.
3. **Evaluar la coherencia didáctica** y generar metadatos de aprendizaje (conceptos clave, prerrequisitos, tiempo estimado de estudio).
4. **Disponibilizar en formato JSON estructurado** para integración con sistemas externos.
5. **Interfaz interactiva** (Streamlit o Gradio).
6. **Persistencia obligatoria en OCI Object Storage** (capa Always Free) de documentos originales y paquetes de contenido generados.

---

## 5. Contrato de Datos (Entrada y Salida)

### Ejemplo de Solicitud (Entrada):
```json
{
  "documento_titulo": "Introduccion a la Arquitectura de Redes VCN en OCI",
  "documento_contenido": "La Virtual Cloud Network (VCN) es una red privada y personalizable configurada en Oracle Cloud Infrastructure. Similar a una red de centro de datos tradicional, la VCN ofrece control total sobre su entorno de red, incluyendo subredes publicas y privadas, tablas de enrutamiento, Internet Gateways, NAT Gateways y Security Lists para control de trafico mediante reglas de entrada (ingress) y salida (egress).",
  "perfil_destinatario": "Principiante",
  "formato_salida": "Flashcards",
  "nicho_sector": "General",
  "nivel_detalle": "Didactico"
}
```

### Ejemplo de Respuesta (Salida Estructurada):
```json
{
  "status": "exito",
  "metadatos": {
    "perfil_aplicado": "Principiante",
    "formato_generado": "Flashcards",
    "tiempo_estimado_estudio_minutos": 5,
    "conceptos_clave": ["VCN", "Subredes", "Internet Gateway", "Security Lists"]
  },
  "contenido_adaptado": {
    "titulo": "Dominando Redes en la Nube (VCN) desde Cero",
    "introduccion_contextualizada": "Imagina la VCN como tu propio barrio privado y seguro dentro de la nube de Oracle, donde tu decides quien entra y quien sale.",
    "items": [
      {
        "frente": "Que es una VCN en Oracle Cloud?",
        "dorso": "Es tu red virtual privada y personalizada dentro de la nube de Oracle, funcionando como la infraestructura de red de tu empresa.",
        "pista_didactica": "Piensa en ella como el terreno cercado donde residen tus servidores."
      },
      {
        "frente": "Para que sirven las Security Lists (Listas de Seguridad)?",
        "dorso": "Son como guardias virtuales con listas de reglas que definen exactamente que tipo de trafico de datos puede entrar o salir de tu red.",
        "pista_didactica": "Reglas de entrada (ingress) y reglas de salida (egress)."
      }
    ]
  },
  "evaluacion_calidad": {
    "anclaje_fuente_score": 0.98,
    "claridad_pedagogica": "Alta",
    "observaciones": "Lenguaje ajustado con analogias para publico principiante, sin tecnicismos excesivos."
  },
  "almacenamiento_oci": {
    "bucket": "nuevamente-contenidos-educativos",
    "objeto_id": "contenido-vcn-principiante-flashcards-001.json",
    "status_upload": "completado"
  }
}
```

---

## 6. Checklist de Evaluación (Requisitos Mínimos)
- [ ] Ingestión funcional de documentos técnicos (PDF, Markdown o texto).
- [ ] Implementación de RAG con segmentación (chunking), embeddings y búsqueda vectorial en Vector Store.
- [ ] Orquestación con LLM (Google Gemini, OpenAI ChatGPT, Anthropic Claude o equivalente).
- [ ] Capacidad comprobada de adaptar el mismo contenido para al menos 2 perfiles diferentes (ej.: Principiante vs Avanzado) y 2 formatos distintos (ej.: Tutorial vs Flashcards/Quiz).
- [ ] Salida de datos estructurada en JSON e interfaz interactiva (Streamlit o Gradio) o API REST operativa.
- [ ] Integración activa y funcional con OCI Object Storage (capa Always Free) para la persistencia de archivos.
- [ ] Presentación de un mínimo de 3 ejemplos de ejecución con documentaciones reales o simuladas.
- [ ] Documentación completa en el repositorio GitHub con diagrama de arquitectura.

---

## 7. Recursos Opcionales (Diferenciales)
- **Despliegue Completo en la Nube (OCI Compute):** Instancia VM Linux en Always Free de OCI.
- **Sistema Multi-Agente con LangGraph:** Enrutador con Agente Investigador RAG, Agente Redactor Pedagógico y Agente Crítico/Revisor.
- **Generación de Quizzes con Evaluación en Tiempo Real:** Interfaz donde el estudiante responde y recibe feedback instantáneo.
- **Soporte Multimodal:** Interpretación de diagramas técnicos contenidos en el documento original.
- **Exportación Multiformato:** Descarga directa en Markdown, PDF didáctico formateado o CSV compatible con Anki.
