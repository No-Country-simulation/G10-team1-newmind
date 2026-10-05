# Proyecto 1 – 🎓 NuevaMente – Sistema Inteligente de Adaptación y Generación de Contenido Educativo
**Programa ONE · Grupo 10 | Hackathon ONE G10 — Oracle Next Education & Alura**

---

## 1. Mapeo de Formaciones ONE (Grupo 10)
- **Formaciones Indispensables:** Inteligencia de Datos y RAG Avanzado y Oracle Cloud Infrastructure (OCI).
- **Formaciones de Refuerzo:** Ingeniería de Agentes y Automatización con IA y Desarrollo y Orquestación con IA Generativa.
- **Núcleo Técnico:** Pipeline RAG con segmentación, embeddings y búsqueda vectorial en ChromaDB para fundamentar el contenido didáctico en fuentes técnicas. El cliente de OCI Object Storage admite persistencia real si está configurado y emulación local en caso contrario; no debe confundirse esta última con una integración activa en OCI Always Free.

---

## 2. Sector Empresarial
**EdTech / Capacitación Corporativa / Plataformas de Educación Técnica:** Aplicaciones y servicios orientados a democratizar y acelerar el aprendizaje técnico. El sector atiende a instituciones educativas, empresas de tecnología y equipos de ingeniería que necesitan capacitar a públicos diversos (desde principiantes en transición de carrera hasta líderes técnicos y arquitectos) a partir de documentaciones, manuales y materiales técnicos densos y en constante evolución.

---

## 3. Descripción del Proyecto
NuevaMente busca ingerir documentaciones técnicas, manuales de software, artículos o bases de conocimiento y transformarlos en contenidos educativos personalizados y estructurados según el perfil del destinatario, la industria de aplicación y el formato pedagógico elegido. La implementación actual carga archivos PDF, Markdown y TXT mediante una API FastAPI y ofrece una interfaz React/Vite para configurar y consultar adaptaciones.

La creación manual de materiales didácticos a partir de documentación compleja consume tiempo de especialistas y diseñadores instruccionales. La solución combina IA generativa y RAG para reducir ese trabajo y favorecer la fidelidad técnica. Hoy utiliza un motor de adaptación con recuperación de contexto; la orquestación multiagente sigue siendo una posibilidad futura, no una capacidad acreditada.

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
  - Básico, Intermedio, Didáctico, Detallado (valores de la API).

---

## 4. Requisitos de Inteligencia de la Aplicación
1. **Extraer e indexar** documentos técnicos mediante segmentación, embeddings y búsqueda vectorial. La carga actual admite PDF, MD y TXT (máximo 20 MB); el resultado depende de que el archivo tenga texto extraíble.
2. **Orquestar un flujo de agentes o cadenas de prompts** con LLM para reescribir, ejemplificar y estructurar el contenido. Existe un motor único de adaptación; un grafo multiagente no está implementado.
3. **Evaluar la coherencia didáctica** y generar metadatos de aprendizaje (conceptos clave, prerrequisitos, tiempo estimado). La puntuación de anclaje procede de similitud de recuperación y no constituye por sí sola una validación independiente de la claridad pedagógica.
4. **Disponibilizar en formato JSON estructurado** para integración con sistemas externos. La API devuelve un recurso de adaptación con `officialResponse` una vez finalizado el procesamiento, además de `content` y `evaluation`.
5. **Interfaz interactiva:** La interfaz vigente utiliza React/Vite; FastAPI expone la API REST y su documentación en `/docs`, en lugar de Streamlit o Gradio.
6. **Persistencia en OCI Object Storage:** Es un objetivo del proyecto. El cliente implementa almacenamiento real condicionado a credenciales válidas y un modo local emulado; la existencia del cliente no prueba un despliegue o persistencia real en OCI.

---

## 5. Contrato de Datos (Entrada y Salida)

### Ejemplo de Solicitud (Entrada):
Primero se envía el archivo como `multipart/form-data` (campo `file`) a `POST /api/v1/documents`. Con el `id` obtenido, se crea la adaptación mediante `POST /api/v1/adaptations`:

```json
{
  "documentId": 1,
  "profile": "Principiante",
  "format": "Flashcards",
  "industry": "General",
  "detailLevel": "Didactico"
}
```

El ejemplo original incorporaba título y texto directamente en una única solicitud; esa no es la entrada de la API vigente. Los perfiles admitidos incluyen `Principiante`, `Junior`, `Senior`, `Lider` y `Gestor`; los formatos son `Flashcards`, `Tutorial`, `Quiz`, `Resumen Ejecutivo` y `Guion`.

### Ejemplo de Respuesta (Salida Estructurada):
Una vez terminada la adaptación, `GET /api/v1/adaptations/{id}` devuelve el recurso con `status: "completed"` y `officialResponse`. El siguiente bloque ilustra los cinco campos del contenido oficial, no representa una ejecución ni certifica almacenamiento real o un resultado de calidad medido:

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
    "introduccion_contextualizada": "Una VCN permite organizar una red privada en OCI.",
    "items": [
      {
        "frente": "¿Qué es una VCN en Oracle Cloud?",
        "dorso": "Una red virtual privada y personalizable en OCI.",
        "pista_didactica": "Relaciona sus subredes con la segmentación de la red."
      },
      {
        "frente": "¿Para qué sirven las Security Lists?",
        "dorso": "Definen reglas de tráfico entrante y saliente.",
        "pista_didactica": "Distingue reglas de entrada y salida."
      }
    ]
  },
  "evaluacion_calidad": {
    "anclaje_fuente_score": 0.8,
    "claridad_pedagogica": "Alta",
    "observaciones": "Ejemplo ilustrativo; verificar las fuentes recuperadas."
  },
  "almacenamiento_oci": {
    "bucket": "nuevamente-contenidos-educativos",
    "objeto_id": "contenido-vcn-principiante-flashcards-001.json",
    "status_upload": "completado (local/emulado)"
  }
}
```

`status_upload` debe comprobarse en cada ejecución: puede indicar modo emulado local. El motor asigna «Alta» a `claridad_pedagogica` sin medirla independientemente; la evaluación que expone la API reutiliza la puntuación de anclaje en varios criterios, no equivale a cuatro mediciones independientes. Sin claves o tras fallos de proveedor, el motor utiliza una generación heurística de demostración, que tampoco acredita uso de LLM.

---

## 6. Checklist de Evaluación (Requisitos Mínimos)
- [ ] Ingestión funcional de documentos técnicos (PDF, Markdown o texto); demostrarla con archivos representativos.
- [ ] Implementación de RAG con segmentación, embeddings y búsqueda vectorial en Vector Store; comprobar recuperación sobre el documento correspondiente.
- [ ] Orquestación con LLM (Gemini, OpenAI, Anthropic o equivalente); verificar proveedor y resultados en la ejecución, sin presentar el motor único como multiagente.
- [ ] Adaptar el mismo contenido para al menos 2 perfiles diferentes y 2 formatos distintos (por ejemplo, Principiante/Arquitecto y Tutorial/Flashcards).
- [ ] Salida estructurada JSON e interfaz interactiva o API REST operativa; la interfaz vigente es React/Vite y la API, FastAPI.
- [ ] Integración activa con OCI Object Storage (Always Free); comprobar modo real y objetos persistidos, no solo emulación local.
- [ ] Presentar al menos 3 ejemplos de ejecución con documentación real o simulada; no constan aquí como entregados.
- [ ] Documentación completa en GitHub con diagrama de arquitectura; verificar el artefacto y su versión antes de marcar el requisito.

---

## 7. Recursos Opcionales (Diferenciales)
- **Despliegue Completo en la Nube (OCI Compute):** Posible instancia VM Linux en Always Free; no se acredita un despliegue activo.
- **Sistema Multi-Agente con LangGraph:** Enrutador con Agente Investigador RAG, Agente Redactor Pedagógico y Agente Crítico/Revisor; propuesta, no implementación actual.
- **Generación de Quizzes con Evaluación en Tiempo Real:** Objetivo de interacción y retroalimentación al estudiante; distinguirlo del score de recuperación.
- **Soporte Multimodal:** Interpretación de diagramas técnicos; los PDF escaneados sin texto extraíble no se procesan como contenido multimodal.
- **Exportación Multiformato:** Descarga de Markdown, PDF didáctico o CSV compatible con Anki como diferencial futuro; la API actual expone JSON.
