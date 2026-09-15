"""
Interfaz Gráfica Principal de NuevaMente.
Desarrollada con Streamlit para el Hackathon ONE G10 (Oracle Next Education & No Country).
"""
import sys
import os
import json
from pathlib import Path
import streamlit as st

# Asegurar path del proyecto en sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config.settings import settings
from src.utils.schemas import (
    SolicitudAdaptacion,
    PerfilDestinatario,
    FormatoSalida,
    NichoSector,
    NivelDetalle
)
from src.ingestion.loaders import doc_loader
from src.ingestion.chunker import doc_chunker
from src.rag.vector_store import vector_store
from src.storage.oci_client import oci_storage
from src.llm.engine import llm_engine

# Configuración de página
st.set_page_config(
    page_title="NuevaMente — EdTech RAG & OCI Always Free",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cargar estilos CSS si existen
css_path = BASE_DIR / "ui" / "assets" / "styles.css"
if css_path.exists():
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Encabezado Principal
st.markdown("""
<div class="main-header">
    <h1 style="margin:0; font-size: 2.2rem;">🎓 NuevaMente</h1>
    <p style="margin: 0.25rem 0 0 0; font-size: 1.05rem; opacity: 0.9;">
        Sistema Inteligente de Adaptación y Generación de Contenido Educativo · <strong>Hackathon ONE G10</strong>
    </p>
</div>
""", unsafe_allow_html=True)

# --- SIDEBAR: Parámetros y Carga de Documentos ---
with st.sidebar:
    st.header("⚙️ Configuración & Entrada")
    
    modo_entrada = st.radio(
        "Modo de Carga:",
        ["Cargar Escenario Oficial (Demo)", "Subir Documento Propio"],
        index=0
    )

    doc_titulo = ""
    doc_contenido = ""

    if modo_entrada == "Cargar Escenario Oficial (Demo)":
        escenarios_disponibles = {
            "Escenario 1: Redes VCN en OCI (Principiante / Flashcards)": "01_oci_vcn_redes.md",
            "Escenario 2: Arquitectura Microservicios (Arquitecto / Tutorial)": "02_arquitectura_microservicios.md",
            "Escenario 3: Gobernanza IAM y Seguridad (Ejecutivo / Resumen)": "03_seguridad_cloud_iam.txt"
        }
        seleccion_escenario = st.selectbox("Selecciona un escenario de prueba:", list(escenarios_disponibles.keys()))
        archivo_muestra = settings.SAMPLES_DIR / escenarios_disponibles[seleccion_escenario]
        
        if archivo_muestra.exists():
            doc_titulo = seleccion_escenario.split(":")[1].strip()
            doc_contenido = doc_loader.extract_from_file(archivo_muestra)
            st.success(f"Cargado: {escenarios_disponibles[seleccion_escenario]} ({len(doc_contenido)} caracteres)")
    else:
        doc_titulo_input = st.text_input("Título del Documento:", value="Guía Técnica Personalizada")
        archivo_subido = st.file_uploader("Arrastra tu documento técnico (PDF, Markdown o TXT):", type=["pdf", "md", "txt", "markdown"])
        
        if archivo_subido is not None:
            bytes_data = archivo_subido.read()
            doc_titulo = doc_titulo_input or archivo_subido.name
            doc_contenido = doc_loader.extract_from_bytes(archivo_subido.name, bytes_data)
            st.success(f"Archivo procesado: {archivo_subido.name} ({len(doc_contenido)} caracteres)")
        else:
            texto_manual = st.text_area("O pega el texto técnico directamente aquí:", height=150)
            if texto_manual.strip():
                doc_titulo = doc_titulo_input or "Documento Manual"
                doc_contenido = texto_manual

    st.markdown("---")
    st.subheader("🎯 Parámetros Pedagógicos")

    perfil = st.selectbox(
        "Perfil del Destinatario:",
        [p.value for p in PerfilDestinatario],
        index=0
    )

    formato = st.selectbox(
        "Formato Pedagógico de Salida:",
        [f.value for f in FormatoSalida],
        index=0
    )

    col_side1, col_side2 = st.columns(2)
    with col_side1:
        nicho = st.selectbox("Nicho / Sector:", [n.value for n in NichoSector], index=3)
    with col_side2:
        detalle = st.selectbox("Nivel de Detalle:", [d.value for d in NivelDetalle], index=0)

    st.markdown("---")
    btn_generar = st.button("🚀 Generar Adaptación Pedagógica", type="primary", use_container_width=True)

# --- PANEL PRINCIPAL: Estado de la Infraestructura ---
col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
with col_stat1:
    st.metric("Vector Store", "ChromaDB (Local)", "Indexación Activa")
with col_stat2:
    estado_oci = "Conectado" if not oci_storage.is_emulated else "Always Free (Local/Emulado)"
    st.metric("OCI Storage", estado_oci, settings.OCI_BUCKET_OUTPUTS)
with col_stat3:
    st.metric("Modelo LLM", settings.DEFAULT_LLM_MODEL, "Structured Output")
with col_stat4:
    st.metric("Control Calidad", "RAG Grounding", "Anti-alucinación")

st.markdown("---")

# --- PROCESAMIENTO AL PRESIONAR EL BOTÓN ---
if btn_generar:
    if not doc_contenido.strip():
        st.error("Por favor ingresa o carga un documento técnico antes de continuar.")
    else:
        with st.spinner("1/3 Indexando en Vector Store y guardando documento original en OCI..."):
            # Subir documento original a OCI
            nombre_doc_oci = f"{doc_titulo.lower().replace(' ', '_')[:25]}.txt"
            oci_storage.upload_raw_document(nombre_doc_oci, doc_contenido.encode("utf-8"), "text/plain")

            # Chunking y guardado en ChromaDB
            chunks = doc_chunker.split_text(doc_contenido, source_id=doc_titulo)
            vector_store.clear()
            vector_store.add_chunks(chunks)

        with st.spinner("2/3 Orquestando LLM, recuperando contexto RAG y estructurando contenido..."):
            req = SolicitudAdaptacion(
                documento_titulo=doc_titulo,
                documento_contenido=doc_contenido,
                perfil_destinatario=PerfilDestinatario(perfil),
                formato_salida=FormatoSalida(formato),
                nicho_sector=NichoSector(nicho),
                nivel_detalle=NivelDetalle(detalle)
            )
            respuesta = llm_engine.adapt_content(req)
            st.session_state["ultima_respuesta"] = respuesta
            st.session_state["ultimo_request"] = req

# --- VISUALIZACIÓN DE RESULTADOS ---
if "ultima_respuesta" in st.session_state:
    resp = st.session_state["ultima_respuesta"]
    req = st.session_state["ultimo_request"]

    tab_contenido, tab_calidad, tab_oci, tab_info = st.tabs([
        "📖 Contenido Pedagógico Adaptado",
        "📊 Métricas & Evaluación de Calidad",
        "☁️ Persistencia OCI & JSON Estructurado",
        "👥 Equipo & Documentación"
    ])

    # PESTAÑA 1: Contenido Adaptado
    with tab_contenido:
        st.subheader(resp.contenido_adaptado.titulo)
        st.info(f"💡 **Contexto Pedagógico:** {resp.contenido_adaptado.introduccion_contextualizada}")

        col_meta1, col_meta2, col_meta3 = st.columns(3)
        with col_meta1:
            st.markdown(f"**👤 Perfil:** `{resp.metadatos.perfil_aplicado}`")
        with col_meta2:
            st.markdown(f"**⏱️ Tiempo Estimado:** `{resp.metadatos.tiempo_estimado_estudio_minutos} min`")
        with col_meta3:
            st.markdown(f"**🏷️ Conceptos Clave:** {', '.join(resp.metadatos.conceptos_clave)}")

        st.markdown("---")

        # Renderizado interactivo según formato
        items = resp.contenido_adaptado.items
        if req.formato_salida == FormatoSalida.FLASHCARDS:
            st.markdown("### 🗂️ Tarjetas de Memorización Activa (Flashcards)")
            for i, itm in enumerate(items):
                with st.expander(f"Tarjeta #{i+1}: {itm.get('frente', 'Pregunta')}", expanded=True):
                    st.markdown(f"**Respuesta Didáctica:**\n\n{itm.get('dorso', '')}")
                    if itm.get("pista_didactica"):
                        st.markdown(f"> 🧭 **Pista Didáctica:** *{itm.get('pista_didactica')}*")

        elif req.formato_salida == FormatoSalida.QUIZ:
            st.markdown("### 📝 Quiz de Evaluación en Tiempo Real")
            for i, itm in enumerate(items):
                st.markdown(f"**Pregunta #{i+1}: {itm.get('pregunta', '')}**")
                opciones = itm.get("opciones", [])
                seleccion = st.radio(f"Selecciona tu respuesta para la pregunta #{i+1}:", opciones, key=f"quiz_q_{i}")
                
                if st.button(f"Comprobar Pregunta #{i+1}", key=f"btn_check_{i}"):
                    resp_correcta = itm.get("respuesta_correcta", "")
                    if seleccion.strip() == resp_correcta.strip() or seleccion.startswith(resp_correcta[:2]):
                        st.success("✅ ¡Correcto!")
                    else:
                        st.warning(f"❌ Respuesta esperada: {resp_correcta}")
                    st.info(f"📘 **Justificación Pedagógica:** {itm.get('justificacion_didactica', '')}")

        elif req.formato_salida == FormatoSalida.TUTORIAL:
            st.markdown("### 🛠️ Guía Paso a Paso (Tutorial)")
            for itm in items:
                paso_num = itm.get("paso", 1)
                st.markdown(f"#### Paso {paso_num}: {itm.get('titulo_paso', '')}")
                st.write(itm.get("descripcion", ""))
                if itm.get("comando_o_codigo"):
                    st.code(itm.get("comando_o_codigo"), language="bash")
                if itm.get("verificacion"):
                    st.markdown(f"*✅ Verificación:* `{itm.get('verificacion')}`")
                st.markdown("---")
        else:
            for itm in items:
                st.json(itm)

    # PESTAÑA 2: Evaluación de Calidad
    with tab_calidad:
        st.subheader("Evaluación de Calidad y Fidelidad a la Fuente")
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            score = resp.evaluacion_calidad.anclaje_fuente_score
            st.metric("Puntuación de Anclaje a la Fuente (Grounding)", f"{int(score * 100)}%", help="Medida de similitud y ausencia de alucinaciones con base en la documentación.")
            st.progress(score)
        with col_c2:
            st.metric("Claridad Pedagógica", resp.evaluacion_calidad.claridad_pedagogica)

        st.markdown(f"**Observaciones del Revisor Pedagógico:**\n> {resp.evaluacion_calidad.observaciones}")

    # PESTAÑA 3: Persistencia OCI & JSON
    with tab_oci:
        st.subheader("Persistencia en OCI Object Storage (Always Free)")
        st.success(f"📦 **Bucket de Destino:** `{resp.almacenamiento_oci.bucket}`")
        st.code(f"ID del Objeto: {resp.almacenamiento_oci.objeto_id}\nEstado: {resp.almacenamiento_oci.status_upload}", language="text")

        st.markdown("### Contrato JSON Estructurado Oficial (ONE G10):")
        json_output = resp.model_dump()
        json_str = json.dumps(json_output, indent=2, ensure_ascii=False)
        st.code(json_str, language="json")

        st.download_button(
            label="⬇️ Descargar JSON Generado",
            data=json_str,
            file_name=resp.almacenamiento_oci.objeto_id,
            mime="application/json"
        )

    # PESTAÑA 4: Equipo y Documentación
    with tab_info:
        st.subheader("Equipo del Proyecto — Hackathon ONE G10")
        st.markdown("""
        - **Project Manager:** Martin Morfe
        - **Software / Solution Architect:** Esteban Guillermo Morales Velazquez
        - **Backend Developer:** Juan David Villegas Anaya
        - **Full Stack Developers:** Harol Benjamin Medina Zárate, Heiner Jair Godoy Zamora
        - **Frontend Developers:** Cristian Contreras, Diana Castaño
        - **DevOps Engineer:** Ivan Hernandez
        """)
        st.markdown("Repositorio GitHub: [https://github.com/bitcoinkio/nuevamente](https://github.com/bitcoinkio/nuevamente)")
else:
    st.info("👈 Selecciona un escenario de prueba en la barra lateral o sube tu documento y presiona **'Generar Adaptación Pedagógica'** para comenzar.")
