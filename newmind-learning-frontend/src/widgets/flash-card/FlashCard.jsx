import { useState } from 'react'
import { Lightbulb, RotateCw } from 'lucide-react'

export const FlashCard = ({ item, index, total }) => {
  const [isFlipped, setIsFlipped] = useState(false)
  const [showHint, setShowHint] = useState(false)
  const flip = () => setIsFlipped((current) => !current)

  return (
    <article className="w-full max-w-xl mx-auto my-6 perspective-1000">
      <div className={`flashcard-flip relative grid min-h-80 rounded-2xl shadow-xl transform-style-3d ${isFlipped ? 'rotate-y-180' : ''}`}>
        <button
          type="button"
          aria-pressed={isFlipped}
          aria-label={`${isFlipped ? 'Volver a la pregunta' : 'Mostrar respuesta'} de la tarjeta ${index + 1}`}
          onClick={flip}
          className={`flashcard-flip-control absolute inset-0 z-10 w-full h-full rounded-2xl cursor-pointer focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 ${isFlipped ? 'focus-visible:outline-white' : 'focus-visible:outline-indigo-600'}`}
        />
        <div
          aria-hidden={isFlipped}
          inert={isFlipped}
          className="col-start-1 row-start-1 backface-hidden bg-white rounded-2xl border border-slate-200 border-t-4 border-t-indigo-600 p-6 flex flex-col justify-between gap-6"
        >
          <div className="flex flex-1 flex-col gap-6" onClick={flip}>
            <div className="flex justify-between items-center gap-4 text-xs font-semibold text-slate-500">
              <span>TARJETA {index + 1} DE {total}</span>
              <span className="flex items-center gap-1 text-indigo-700"><RotateCw className="w-3 h-3" /> Mostrar respuesta</span>
            </div>
            <h3 className="flex-1 flex items-center justify-center px-4 text-center text-xl md:text-2xl font-bold text-slate-800 leading-snug">
              {item.frente}
            </h3>
          </div>
          <div className="relative z-20 self-start pointer-events-none">
            <button
              type="button"
              onClick={() => setShowHint((current) => !current)}
              className="pointer-events-auto flex items-center gap-1.5 text-xs font-medium text-amber-800 bg-amber-50 hover:bg-amber-100 px-3 py-2 rounded-full transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-amber-700"
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
          </div>
        </div>

        <div
          aria-hidden={!isFlipped}
          inert={!isFlipped}
          onClick={flip}
          className="col-start-1 row-start-1 backface-hidden rotate-y-180 bg-indigo-900 rounded-2xl border border-indigo-800 p-6 flex flex-col justify-between gap-6 text-white"
        >
          <span className="text-xs font-semibold text-indigo-200">RESPUESTA / CONCEPTO</span>
          <p className="flex-1 flex items-center justify-center px-4 text-center text-lg md:text-xl font-medium leading-relaxed text-indigo-50">
            {item.dorso}
          </p>
          <p className="text-center text-xs text-indigo-300">¿Lograste recordarlo correctamente?</p>
        </div>
      </div>
    </article>
  )
}
