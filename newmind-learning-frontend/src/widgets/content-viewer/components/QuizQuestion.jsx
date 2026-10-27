import { useState } from 'react'
import {
  CheckCircle2,
  CircleHelp,
  Lightbulb,
  XCircle,
  Target,
} from 'lucide-react'
import { Badge } from '@/shared/ui/Badge'

/** Renders one question without revealing its answer before submission. */
export function QuizQuestion({
  question,
  index,
  selected,
  submitted,
  onSelect,
  onSubmit,
}) {
  const [showHint, setShowHint] = useState(false)

  const options = Array.isArray(question.options) ? question.options : []
  const correctAnswer = question.correct_answer

const canEvaluate =
  typeof correctAnswer === 'string' && correctAnswer.trim().length > 0

const normalizeAnswer = (value) =>
  typeof value === 'string'
    ? value.trim().replace(/^[A-D]\s*[\).:-]\s*/, '').trim().toLowerCase()
    : ''

const getOptionLetter = (value) => {
  if (typeof value !== 'string') return ''

  const match = value.trim().match(/^([A-D])(?:\s*[\).:-]|\s*$)/i)
  return match ? match[1].toUpperCase() : ''
}

const selectedLetter = getOptionLetter(selected)
const correctLetter = getOptionLetter(correctAnswer)

const isCorrect =
  submitted &&
  canEvaluate &&
  (
    (selectedLetter && correctLetter && selectedLetter === correctLetter) ||
    normalizeAnswer(selected) === normalizeAnswer(correctAnswer)
  )
  const justification = question.justification
  const hint = question.hint

  return (
    <article className="overflow-hidden rounded-2xl border border-slate-700/80 bg-slate-800 shadow-lg shadow-slate-950/10 transition-shadow hover:shadow-slate-950/20">
      {/* Encabezado de la pregunta */}
      <header className="border-b border-slate-700/80 bg-gradient-to-r from-slate-800 to-slate-800/60 p-5 sm:p-6">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-brand-500/15 text-sm font-bold text-brand-300 ring-1 ring-brand-400/20">
              {String(index + 1).padStart(2, '0')}
            </span>
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Pregunta
            </span>
          </div>

          {question.difficulty && (
            <Badge size="sm">{question.difficulty}</Badge>
          )}
        </div>

        <h3 className="text-base font-semibold leading-7 text-white sm:text-lg">
          {question.prompt}
        </h3>
      </header>

      <div className="space-y-5 p-5 sm:p-6">
        {/* Opciones de respuesta */}
        {options.length > 0 ? (
          <fieldset disabled={submitted} className="space-y-3">
            <legend className="mb-3 flex items-center gap-2 text-sm font-medium text-slate-300">
              <Target className="h-4 w-4 text-brand-300" />
              Selecciona una respuesta
            </legend>

            {options.map((option, optionIndex) => {
              const isSelected = selected === option
              const isCorrectOption =
                submitted && canEvaluate && option === correctAnswer
              const isWrongSelection =
                submitted && isSelected && canEvaluate && !isCorrect

              let optionStyle =
                'border-slate-700 bg-slate-900/40 hover:border-slate-500 hover:bg-slate-700/60'

              if (isSelected && !submitted) {
                optionStyle =
                  'border-brand-400 bg-brand-500/10 ring-2 ring-brand-400/20'
              }

              if (isCorrectOption) {
                optionStyle =
                  'border-emerald-500/60 bg-emerald-500/10 ring-1 ring-emerald-500/20'
              }

              if (isWrongSelection) {
                optionStyle =
                  'border-rose-500/60 bg-rose-500/10 ring-1 ring-rose-500/20'
              }

              return (
                <label
                  key={`${optionIndex}-${option}`}
                  className={`group flex cursor-pointer items-start gap-3 rounded-xl border p-4 text-sm leading-relaxed text-slate-200 transition-all duration-200 focus-within:outline focus-within:outline-2 focus-within:outline-offset-2 focus-within:outline-brand-400 ${optionStyle} ${
                    submitted ? 'cursor-default' : ''
                  }`}
                >
                  <input
                    type="radio"
                    name={`quiz-question-${index}`}
                    value={option}
                    checked={isSelected}
                    onChange={() => onSelect(option)}
                    className="mt-1 h-4 w-4 shrink-0 accent-indigo-500"
                  />

                  <span className="min-w-0 flex-1">{option}</span>

                  {isCorrectOption && (
                    <CheckCircle2
                      aria-label="Respuesta correcta"
                      className="mt-0.5 h-5 w-5 shrink-0 text-emerald-400"
                    />
                  )}

                  {isWrongSelection && (
                    <XCircle
                      aria-label="Respuesta seleccionada incorrecta"
                      className="mt-0.5 h-5 w-5 shrink-0 text-rose-400"
                    />
                  )}
                </label>
              )
            })}
          </fieldset>
        ) : (
          <p
            className="rounded-xl border border-amber-500/30 bg-amber-500/10 p-4 text-sm leading-relaxed text-amber-200"
            role="status"
          >
            Esta pregunta no contiene opciones de respuesta válidas.
          </p>
        )}

        {/* Acciones */}
        <div className="flex flex-wrap items-center gap-3 border-t border-slate-700/70 pt-5">
          {!submitted && (
            <button
              type="button"
              onClick={onSubmit}
              disabled={!selected || options.length === 0}
              className="inline-flex min-h-11 items-center justify-center gap-2 rounded-xl bg-brand-500 px-5 py-3 text-sm font-semibold text-white shadow-md shadow-brand-950/20 transition-all hover:-translate-y-0.5 hover:bg-brand-400 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-300 disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:translate-y-0"
            >
              <CheckCircle2 className="h-4 w-4" />
              Comprobar respuesta
            </button>
          )}

          {!submitted && hint && (
            <button
              type="button"
              onClick={() => setShowHint((current) => !current)}
              aria-expanded={showHint}
              className="inline-flex min-h-11 items-center justify-center gap-2 rounded-xl border border-amber-500/20 px-4 py-2.5 text-sm font-medium text-amber-300 transition-colors hover:bg-amber-500/10 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-amber-300"
            >
              <Lightbulb className="h-4 w-4" />
              {showHint ? 'Ocultar pista' : 'Ver pista'}
            </button>
          )}
        </div>

        {/* Pista didáctica */}
        {showHint && hint && !submitted && (
          <div
            className="flex gap-3 rounded-xl border border-amber-500/20 bg-amber-500/5 p-4 text-sm leading-relaxed text-amber-100"
            role="note"
          >
            <CircleHelp className="mt-0.5 h-5 w-5 shrink-0 text-amber-300" />
            <div>
              <p className="mb-1 font-semibold text-amber-300">
                Pista para ayudarte
              </p>
              <p>{hint}</p>
            </div>
          </div>
        )}

        {/* Retroalimentación después de responder */}
        {submitted && (
          <div
            role="status"
            className={`rounded-xl border p-4 sm:p-5 ${
              !canEvaluate
                ? 'border-slate-600 bg-slate-900/70'
                : isCorrect
                  ? 'border-emerald-500/30 bg-emerald-500/10'
                  : 'border-rose-500/30 bg-rose-500/10'
            }`}
          >
            <div className="mb-3 flex items-start gap-3">
              <span
                className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-xl ${
                  !canEvaluate
                    ? 'bg-slate-700 text-slate-300'
                    : isCorrect
                      ? 'bg-emerald-500/15 text-emerald-300'
                      : 'bg-rose-500/15 text-rose-300'
                }`}
              >
                {!canEvaluate ? (
                  <CircleHelp className="h-5 w-5" />
                ) : isCorrect ? (
                  <CheckCircle2 className="h-5 w-5" />
                ) : (
                  <XCircle className="h-5 w-5" />
                )}
              </span>

              <div className="min-w-0 flex-1">
                <p
                  className={`font-semibold ${
                    !canEvaluate
                      ? 'text-slate-200'
                      : isCorrect
                        ? 'text-emerald-300'
                        : 'text-rose-300'
                  }`}
                >
                  {!canEvaluate
                    ? 'Respuesta registrada'
                    : isCorrect
                      ? '¡Respuesta correcta!'
                      : 'Respuesta incorrecta'}
                </p>

                <p className="mt-1 text-sm leading-relaxed text-slate-300">
                  {!canEvaluate
                    ? 'No es posible evaluar automáticamente esta respuesta porque falta la clave de respuesta.'
                    : isCorrect
                      ? 'Has identificado la opción correcta.'
                      : 'Revisa la respuesta correcta y su explicación para reforzar tu aprendizaje.'}
                </p>
              </div>
            </div>

            {canEvaluate && !isCorrect && (
              <p className="mb-3 rounded-lg bg-slate-950/30 p-3 text-sm text-slate-200">
                <span className="text-slate-400">Respuesta correcta: </span>
                <strong className="text-emerald-300">
                  {correctAnswer}
                </strong>
              </p>
            )}

            {justification && (
              <div className="border-t border-slate-700/70 pt-3">
                <p className="mb-1 text-xs font-semibold uppercase tracking-wider text-slate-400">
                  Explicación
                </p>
                <p className="text-sm leading-relaxed text-slate-300">
                  {justification}
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </article>
  )
}
