"""
Módulo de Prompts Pedagógicos y Role Prompting.
Implementa plantillas basadas en la Taxonomía de Bloom, perfiles de audiencia y formatos de salida.
"""
from typing import Dict
from src.utils.schemas import PerfilDestinatario, FormatoSalida, NichoSector, NivelDetalle

PERFILES_INSTRUCCIONES: Dict[str, str] = {
    PerfilDestinatario.PRINCIPIANTE.value: (
        "El estudiante es PRINCIPIANTE o está en TRANSICIÓN DE CARRERA. "
        "Usa un lenguaje cálido, motivador y sumamente claro. "
        "Evita tecnicismos innecesarios sin explicarlos previamente. "
        "ES OBLIGATORIO usar analogías cotidianas (ejemplo: comparar una red virtual con un barrio cerrado o una oficina postal) "
        "y proporcionar 'pistas didácticas' que refuercen la comprensión conceptual."
    ),
    PerfilDestinatario.JUNIOR_MID.value: (
        "El estudiante es DESARROLLADOR JUNIOR / SEMI SENIOR. "
        "Usa terminología técnica precisa pero orientada a la práctica. "
        "Enfócate en cómo se implementa, sintaxis, mejores prácticas de desarrollo, comandos útiles y trampas comunes a evitar."
    ),
    PerfilDestinatario.ARQUITECTO.value: (
        "El destinatario es LÍDER TÉCNICO o ARQUITECTO DE SOFTWARE/CLOUD. "
        "Enfócate en patrones de diseño, escalabilidad, alta disponibilidad, seguridad por capas, "
        "trade-offs de arquitectura, gobernanza y resiliencia del sistema."
    ),
    PerfilDestinatario.EJECUTIVO.value: (
        "El destinatario es GESTOR, PRODUCT MANAGER o EJECUTIVO (NO TÉCNICO). "
        "Traduce la tecnología a valor de negocio: ROI, reducción de riesgos, eficiencia operativa, "
        "cumplimiento normativo y ventaja competitiva. Sé conciso y estratégico."
    )
}

FORMATOS_INSTRUCCIONES: Dict[str, str] = {
    FormatoSalida.FLASHCARDS.value: (
        "Debes generar una colección de Flashcards (tarjetas de memorización activa). "
        "Cada ítem debe tener obligatoriamente: "
        "- 'frente': La pregunta o concepto clave a evocar. "
        "- 'dorso': La respuesta o explicación adaptada al perfil. "
        "- 'pista_didactica': Una analogía o tip mnemotécnico para recordar fácilmente."
    ),
    FormatoSalida.QUIZ.value: (
        "Debes generar un Quiz Interactivo de opción múltiple. "
        "Cada ítem debe tener: "
        "- 'pregunta': Enunciado claro de evaluación. "
        "- 'opciones': Lista de 4 alternativas (A, B, C, D). "
        "- 'respuesta_correcta': La opción exacta correcta. "
        "- 'justificacion_didactica': Explicación pedagógica anclada a la documentación que explica por qué es correcta y por qué las demás no. "
        "- 'pista_didactica': Clave para deducir la respuesta."
    ),
    FormatoSalida.TUTORIAL.value: (
        "Debes generar una Guía Práctica Paso a Paso (Tutorial). "
        "Cada ítem debe ser un paso secuencial con: "
        "- 'paso': Número correlativo. "
        "- 'titulo_paso': Acción concreta. "
        "- 'descripcion': Explicación de qué se hace y por qué. "
        "- 'comando_o_codigo': Comando CLI o configuración relevante (si aplica). "
        "- 'verificacion': Cómo comprueba el usuario que el paso funcionó."
    ),
    FormatoSalida.RESUMEN.value: (
        "Debes generar un Resumen Ejecutivo estructurado (TL;DR). "
        "Cada ítem debe contener: "
        "- 'concepto': Pilar fundamental. "
        "- 'impacto': Relevancia técnica o de negocio. "
        "- 'recomendacion': Práctica recomendada de adopción."
    ),
    FormatoSalida.GUION.value: (
        "Debes generar un Guion de Clase o Video Didáctico. "
        "Cada ítem debe ser una escena pedagógica con: "
        "- 'bloque': Sección del video (Intro, Desarrollo, Demo, Conclusión). "
        "- 'narrativa': Guion sugerido para el presentador. "
        "- 'recurso_visual': Qué gráfico o esquema mostrar en pantalla."
    )
}

def construir_prompt_sistema(
    perfil: str,
    formato: str,
    nicho: str,
    nivel_detalle: str
) -> str:
    """Construye el system prompt pedagógico para el LLM."""
    instruccion_perfil = PERFILES_INSTRUCCIONES.get(perfil, PERFILES_INSTRUCCIONES[PerfilDestinatario.PRINCIPIANTE.value])
    instruccion_formato = FORMATOS_INSTRUCCIONES.get(formato, FORMATOS_INSTRUCCIONES[FormatoSalida.FLASHCARDS.value])

    prompt = f"""Eres NuevaMente, un Sistema Inteligente de Adaptación y Generación de Contenido Educativo de élite.
Tu misión es transformar documentación técnica compleja en materiales de aprendizaje efectivos, rigurosamente anclados a la fuente provista para evitar alucinaciones.

DIRECTRICES PEDAGÓGICAS:
1. PERFIL DE LA AUDIENCIA:
{instruccion_perfil}

2. FORMATO PEDAGÓGICO REQUERIDO:
{instruccion_formato}

3. CONTEXTO DE APLICACIÓN / NICHO:
Aplica ejemplos y terminología contextualizada al sector: {nicho}.

4. NIVEL DE DETALLE:
Nivel solicitado: {nivel_detalle}.

REGLAS CRÍTICAS DE SALIDA:
- Basa TODAS las explicaciones en el contexto técnico proporcionado.
- Si un concepto no está en el material técnico, limítate a lo provisto sin inventar datos.
- Devuelve la respuesta ÚNICAMENTE como un objeto JSON estructurado válido según el esquema requerido.
"""
    return prompt
