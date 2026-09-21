import { useState } from 'react';
import { Lightbulb, RotateCw } from 'lucide-react';

export const FlashCard = ({ item, index, total }) => {
  const [isFlipped, setIsFlipped] = useState(false);
  const [showHint, setShowHint] = useState(false);

  // Soporte para propiedades en español e inglés
  const questionText = item.frente || item.front || '';
  const answerText = item.dorso || item.back || '';
  const hintText = item.pista_didactica || item.didactic_hint || '';

  const handleCardClick = () => {
    setIsFlipped(!isFlipped);
  };

  const handleHintClick = (e) => {
    e.stopPropagation();
    setShowHint(!showHint);
  };

  return (
    <div className="w-full max-w-xl mx-auto my-6 perspective-1000">
      <div
        onClick={handleCardClick}
        className={`relative w-full h-80 rounded-2xl shadow-xl border border-slate-200 cursor-pointer transition-transform duration-500 transform-style-3d ${
          isFlipped ? 'rotate-y-180' : ''
        }`}
      >
        {/* CARA FRONTAL (PREGUNTA) */}
        <div
          className="absolute inset-0 w-full h-full bg-white rounded-2xl p-6 flex flex-col justify-between border-t-4 border-t-indigo-600"
          style={{ backfaceVisibility: 'hidden', WebkitBackfaceVisibility: 'hidden' }}
        >
          <div className="flex justify-between items-center text-xs font-semibold text-slate-400">
            <span>TARJETA {index + 1} DE {total}</span>
            <span className="flex items-center gap-1 text-indigo-600">
              <RotateCw className="w-3 h-3" /> Haz clic para voltear
            </span>
          </div>

          <div className="flex-1 flex items-center justify-center px-4 text-center">
            <h3 className="text-xl md:text-2xl font-bold text-slate-800 leading-snug">
              {questionText}
            </h3>
          </div>

          <div className="flex justify-between items-center min-h-[40px]">
            {hintText ? (
              <button
                onClick={handleHintClick}
                className="flex items-center gap-1.5 text-xs font-medium text-amber-600 bg-amber-50 hover:bg-amber-100 px-3 py-1.5 rounded-full transition-colors"
              >
                <Lightbulb className="w-4 h-4" />
                {showHint ? 'Ocultar pista' : 'Ver pista didáctica'}
              </button>
            ) : <div />}
          </div>

          {showHint && hintText && (
            <div className="mt-2 p-3 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-800 italic animate-fade-in">
              💡 <strong>Pista:</strong> {hintText}
            </div>
          )}
        </div>

        {/* CARA TRASERA (RESPUESTA) */}
        <div
          className="absolute inset-0 w-full h-full bg-indigo-900 rounded-2xl p-6 flex flex-col justify-between rotate-y-180 text-white"
          style={{ backfaceVisibility: 'hidden', WebkitBackfaceVisibility: 'hidden' }}
        >
          <div className="flex justify-between items-center text-xs text-indigo-200 font-semibold">
            <span>RESPUESTA / CONCEPTO</span>
            <span className="flex items-center gap-1 text-indigo-300">
              <RotateCw className="w-3 h-3" /> Volver a la pregunta
            </span>
          </div>

          <div className="flex-1 flex items-center justify-center px-4 text-center">
            <p className="text-lg md:text-xl font-medium leading-relaxed text-indigo-50">
              {answerText}
            </p>
          </div>

          <div className="text-center text-xs text-indigo-300">
            ¿Lograste recordarlo correctamente?
          </div>
        </div>
      </div>
    </div>
  );
};