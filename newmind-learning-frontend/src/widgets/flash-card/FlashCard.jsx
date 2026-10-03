import { useState } from 'react'
import { Lightbulb, RotateCw } from 'lucide-react'

export const FlashCard = ({ item, index, total }) => {
  const [isFlipped, setIsFlipped] = useState(false)
  const [showHint, setShowHint] = useState(false)

  return (
    <article
      className={`w-full min-h-80 max-w-xl mx-auto my-6 rounded-2xl shadow-xl border p-6 flex flex-col justify-between ${
        isFlipped
          ? 'bg-indigo-900 border-indigo-800 text-white'
          : 'bg-white border-slate-200 border-t-4 border-t-indigo-600'
      }`}
    >
      <header className="flex justify-between items-center gap-4 text-xs font-semibold">
        <span className={isFlipped ? 'text-indigo-200' : 'text-slate-500'}>
          {isFlipped ? 'RESPUESTA / CONCEPTO' : `TARJETA ${index + 1} DE ${total}`}
        </span>
        <button
          type="button"
          aria-pressed={isFlipped}
          onClick={() => setIsFlipped((current) => !current)}
          className={`flex items-center gap-1 px-2 py-2 rounded focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 ${
            isFlipped
              ? 'text-indigo-200 focus-visible:outline-white'
              : 'text-indigo-700 focus-visible:outline-indigo-600'
          }`}
        >
          <RotateCw className="w-3 h-3" />
          {isFlipped ? 'Volver a la pregunta' : 'Mostrar respuesta'}{' '}
          <span className="sr-only">de la tarjeta {index + 1}</span>
        </button>
      </header>

      {isFlipped ? (
        <>
          <p className="flex-1 flex items-center justify-center px-4 text-center text-lg md:text-xl font-medium leading-relaxed text-indigo-50">
            {item.dorso}
          </p>
          <p className="text-center text-xs text-indigo-300">
            ¿Lograste recordarlo correctamente?
          </p>
        </>
      ) : (
        <>
          <h3 className="flex-1 flex items-center justify-center px-4 text-center text-xl md:text-2xl font-bold text-slate-800 leading-snug">
            {item.frente}
          </h3>
          <button
            type="button"
            onClick={() => setShowHint((current) => !current)}
            className="self-start flex items-center gap-1.5 text-xs font-medium text-amber-800 bg-amber-50 hover:bg-amber-100 px-3 py-2 rounded-full transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-amber-700"
          >
            <Lightbulb className="w-4 h-4" />
            {showHint ? 'Ocultar pista' : 'Ver pista didáctica'}
          </button>
          <div aria-live="polite" className="min-h-12 mt-2">
            {showHint && (
              <p className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-900 italic">
                💡 <strong>Pista:</strong> <span>{item.pista_didactica}</span>
              </p>
            )}
          </div>
        </>
      )}
    </article>
  )
}
