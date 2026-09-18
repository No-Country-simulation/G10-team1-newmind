import { useState } from 'react';
import {
  Clock,
  CheckCircle2,
  Cloud,
  ChevronLeft,
  ChevronRight,
  Sparkles,
  BookOpen
} from 'lucide-react';
import { FlashCard } from '@/widgets/flash-card/FlashCard';

// MOCK DATA based on the official project specification
const MOCK_FLASHCARDS_DATA = {
  status: "exito",
  metadatos: {},
  perfil_aplicado: "Principiante",
  formato_generado: "Flashcards",
  tiempo_estimado_estudio_minutos: 5,
  conceptos_clave: ["VCN", "Subredes", "Internet Gateway", "Security Lists"],
  contenido_adaptado: {
    titulo: "Dominando Redes en la Nube (VCN) desde Cero",
    introduccion_contextualizada: "Imagina la VCN como tu propio barrio privado y seguro dentro de la nube de Oracle, donde tú decides quién entra y quién sale.",
    items: [
      {
        frente: "¿Qué es una VCN en Oracle Cloud?",
        dorso: "Es tu red virtual privada y personalizada dentro de la nube de Oracle, funcionando como la infraestructura de red de tu empresa.",
        pista_didactica: "Piensa en ella como el terreno cercado donde residen tus servidores."
      },
      {
        frente: "¿Para qué sirven las Security Lists (Listas de Seguridad)?",
        dorso: "Son como guardias virtuales con listas de reglas que definen exactamente qué tipo de tráfico de datos puede entrar o salir de tu red.",
        pista_didactica: "Reglas de entrada (ingress) y reglas de salida (egress)."
      },
      {
        frente: "¿Qué función cumple un Internet Gateway?",
        dorso: "Es la puerta de enlace que conecta tu VCN directamente con el internet público, permitiendo la comunicación bidireccional.",
        pista_didactica: "Es como la puerta principal que conecta tu barrio privado con la avenida pública."
      },
      {
        frente: "¿Cuál es la diferencia entre una Subred Pública y una Privada?",
        dorso: "La subred pública contiene recursos que pueden acceder directamente a internet, mientras que la subred privada aísla recursos sensibles del exterior.",
        pista_didactica: "Una es como la recepción abierta al público y la otra es la bóveda de seguridad."
      }
    ]
  },
  evaluacion_calidad: {
    anclaje_fuente_score: 0.98,
    claridad_pedagogica: "Alta",
    observaciones: "Lenguaje ajustado con analogías para público principiante, sin tecnicismos excesivos."
  },
  almacenamiento_oci: {
    bucket: "nuevamente-contenidos-educativos",
    objeto_id: "contenido-vcn-principiante-flashcards-001.json",
    status_upload: "completado"
  }
};

export const FlashcardsPage = ({ data = MOCK_FLASHCARDS_DATA }) => {
  const [currentIndex, setCurrentIndex] = useState(0);

  const activeData = data || MOCK_FLASHCARDS_DATA;
  const items = activeData.adapted_content?.items || activeData.contenido_adaptado?.items || [];

  const handleNext = () => {
    if (currentIndex < items.length - 1) {
      setCurrentIndex((prev) => prev + 1);
    }
  };

  const handlePrev = () => {
    if (currentIndex > 0) {
      setCurrentIndex((prev) => prev - 1);
    }
  };

  if (items.length === 0) {
    return (
      <div className="p-8 text-center text-slate-400">
        No hay datos de flashcards disponibles.
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 py-10 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto space-y-8">

        {/* HEADER AND PEDAGOGICAL METADATA */}
        <div className="bg-slate-900/80 rounded-2xl p-6 sm:p-8 shadow-md border border-slate-800">
          <div className="flex flex-wrap items-center justify-between gap-4 mb-4">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-indigo-900/40 text-indigo-300 border border-indigo-800/50">
              <Sparkles className="w-3.5 h-3.5" />
              Perfil Objetivo: {activeData.applied_profile || activeData.perfil_aplicado}
            </span>

            <div className="flex items-center gap-4 text-xs font-medium text-slate-400">
              <span className="flex items-center gap-1">
                <Clock className="w-4 h-4 text-slate-500" />
                ~{activeData.estimated_study_time_minutes || activeData.tiempo_estimado_estudio_minutos} min tiempo de estudio
              </span>
              <span className="flex items-center gap-1 text-emerald-400 bg-emerald-950/50 px-2 py-0.5 rounded border border-emerald-900/50">
                <CheckCircle2 className="w-4 h-4" />
                Anclaje RAG: {((activeData.quality_evaluation?.source_anchoring_score || activeData.evaluacion_calidad?.anclaje_fuente_score || 0) * 100).toFixed(0)}%
              </span>
            </div>
          </div>

          <h1 className="text-2xl sm:text-3xl font-bold text-slate-50 mb-2">
            {activeData.adapted_content?.title || activeData.contenido_adaptado?.titulo}
          </h1>

          <p className="text-slate-400 text-sm sm:text-base leading-relaxed mb-6">
            {activeData.adapted_content?.contextual_introduction || activeData.contenido_adaptado?.introduccion_contextualizada}
          </p>

          {/* KEY CONCEPTS */}
          <div className="border-t border-slate-800/80 pt-4 flex flex-wrap items-center gap-2">
            <span className="text-xs font-semibold text-slate-400 flex items-center gap-1 mr-2">
              <BookOpen className="w-3.5 h-3.5" /> Conceptos clave:
            </span>
            {(activeData.key_concepts || activeData.conceptos_clave || []).map((concept, idx) => (
              <span
                key={idx}
                className="px-2.5 py-1 bg-slate-800 text-slate-300 rounded-md text-xs font-medium border border-slate-700"
              >
                {concept}
              </span>
            ))}
          </div>
        </div>

        {/* FLASHCARD VIEWER */}
        <div>
          <FlashCard
            item={items[currentIndex]}
            index={currentIndex}
            total={items.length}
          />

          {/* NAVIGATION CONTROLS */}
          <div className="flex items-center justify-between max-w-xl mx-auto mt-4 px-2">
            <button
              onClick={handlePrev}
              disabled={currentIndex === 0}
              className="flex items-center gap-1 px-4 py-2 rounded-xl bg-slate-800 border border-slate-700 text-sm font-semibold text-slate-300 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed shadow-sm transition-all"
            >
              <ChevronLeft className="w-4 h-4" /> Anterior
            </button>

            <span className="text-sm font-medium text-slate-400">
              {currentIndex + 1} / {items.length}
            </span>

            <button
              onClick={handleNext}
              disabled={currentIndex === items.length - 1}
              className="flex items-center gap-1 px-4 py-2 rounded-xl bg-indigo-600 text-white text-sm font-semibold hover:bg-indigo-500 disabled:opacity-40 disabled:cursor-not-allowed shadow-sm transition-all"
            >
              Siguiente <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* FOOTER: OCI OBJECT STORAGE STATUS & REMARKS */}
        <div className="bg-slate-900/50 rounded-xl p-4 flex flex-wrap justify-between items-center text-xs text-slate-400 gap-2 border border-slate-800">
          <div className="flex items-center gap-2">
            <Cloud className="w-4 h-4 text-slate-500" />
            <span>
              Persistido en <strong>Bucket OCI:</strong> {activeData.oci_storage?.bucket || activeData.almacenamiento_oci?.bucket} | ID: <code className="bg-slate-800 px-1.5 py-0.5 rounded text-slate-300 border border-slate-700">{activeData.oci_storage?.object_id || activeData.almacenamiento_oci?.objeto_id}</code>
            </span>
          </div>
          <span className="italic text-slate-500">
            {activeData.quality_evaluation?.remarks || activeData.evaluacion_calidad?.observaciones}
          </span>
        </div>

      </div>
    </div>
  );
};

export default FlashcardsPage;
