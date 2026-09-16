import { BookOpen, HelpCircle, AlignLeft, Presentation, FileCheck } from 'lucide-react'
import { Badge } from '@/shared/ui/Badge'
import { Card } from '@/shared/ui/Card'
import { ScoreRing } from '@/shared/ui/Alert'
import { cn } from '@/shared/utils'

// ── Format icon map ───────────────────────────────────────────────────────────

const FORMAT_ICONS = {
  Flashcards:         HelpCircle,
  Tutorial:           BookOpen,
  'Resumen Ejecutivo': FileCheck,
  Quiz:               AlignLeft,
  Guion:              Presentation,
}

// ── Format-specific views ─────────────────────────────────────────────────────

function FlashcardItem({ card }) {
  return (
    <div className="group bg-slate-800 rounded-xl border border-slate-700 p-5 hover:border-brand-500/40 transition-all duration-200">
      <div className="flex items-start justify-between gap-3 mb-3">
        <Badge variant="brand"   size="sm">{card.concept}</Badge>
        <Badge variant="default" size="sm">{card.difficulty}</Badge>
      </div>
      <p className="text-sm font-semibold text-slate-200 mb-2">❓ {card.question}</p>
      <div className="mt-3 pt-3 border-t border-slate-700">
        <p className="text-sm text-slate-400">✅ {card.answer}</p>
      </div>
      {card.source && (
        <p className="text-xs text-slate-600 mt-3">Fuente: {card.source}</p>
      )}
    </div>
  )
}

function FlashcardsView({ content }) {
  return (
    <div>
      <p className="text-sm text-slate-500 mb-4">
        {content.cards?.length ?? 0} flashcards generadas
      </p>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {content.cards?.map((card, i) => (
          <FlashcardItem key={i} card={card} />
        ))}
      </div>
    </div>
  )
}

function TutorialView({ content }) {
  return (
    <div className="space-y-6">
      {content.introduction && (
        <div className="p-4 bg-brand-600/10 border border-brand-600/20 rounded-xl">
          <p className="text-sm font-semibold text-brand-300 mb-2">Introducción</p>
          <p className="text-sm text-slate-300">{content.introduction}</p>
        </div>
      )}
      {content.steps?.map((step, i) => (
        <div key={i} className="flex gap-4">
          <div className="flex-shrink-0 w-8 h-8 rounded-full bg-brand-600/20 border border-brand-600/30 flex items-center justify-center text-brand-400 font-bold text-sm">
            {i + 1}
          </div>
          <div className="flex-1">
            <p className="font-semibold text-slate-200 text-sm">{step.title}</p>
            <p className="text-sm text-slate-400 mt-1">{step.content}</p>
            {step.example && (
              <pre className="mt-2 p-3 bg-slate-900 rounded-lg text-xs text-slate-300 overflow-x-auto">
                {step.example}
              </pre>
            )}
          </div>
        </div>
      ))}
      {content.conclusion && (
        <div className="p-4 bg-emerald-600/10 border border-emerald-600/20 rounded-xl">
          <p className="text-sm font-semibold text-emerald-300 mb-2">Conclusión</p>
          <p className="text-sm text-slate-300">{content.conclusion}</p>
        </div>
      )}
    </div>
  )
}

function ExecutiveSummaryView({ content }) {
  return (
    <div className="space-y-5">
      {content.summary && (
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">Resumen</p>
          <p className="text-slate-300 text-sm leading-relaxed">{content.summary}</p>
        </div>
      )}
      {content.key_points?.length > 0 && (
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">Puntos Clave</p>
          <ul className="space-y-2">
            {content.key_points.map((point, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-slate-300">
                <span className="w-1.5 h-1.5 rounded-full bg-brand-400 mt-1.5 flex-shrink-0" />
                {point}
              </li>
            ))}
          </ul>
        </div>
      )}
      {content.risks?.length > 0 && (
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-amber-500 mb-2">Riesgos</p>
          <ul className="space-y-2">
            {content.risks.map((risk, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-amber-300">
                <span className="w-1.5 h-1.5 rounded-full bg-amber-400 mt-1.5 flex-shrink-0" />
                {risk}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

function QuizView({ content }) {
  return (
    <div className="space-y-6">
      {content.questions?.map((q, i) => (
        <div key={i} className="p-5 bg-slate-800 rounded-xl border border-slate-700">
          <div className="flex items-start justify-between gap-2 mb-3">
            <p className="text-sm font-semibold text-slate-200">
              {i + 1}. {q.question}
            </p>
            <Badge variant="default" size="sm">{q.difficulty}</Badge>
          </div>
          <div className="space-y-2">
            {q.options?.map((opt, j) => (
              <div
                key={j}
                className={cn(
                  'flex items-center gap-3 p-3 rounded-lg text-sm border transition-colors',
                  opt === q.correct_answer
                    ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
                    : 'bg-slate-700/40    border-slate-700      text-slate-400'
                )}
              >
                <span className="font-medium">{String.fromCharCode(65 + j)}.</span>
                {opt}
              </div>
            ))}
          </div>
          {q.justification && (
            <p className="text-xs text-slate-500 mt-3 pt-3 border-t border-slate-700">
              💡 {q.justification}
            </p>
          )}
        </div>
      ))}
    </div>
  )
}

/**
 * Guion view — structured display will be implemented once the schema is finalised.
 * Currently renders a formatted JSON fallback.
 */
function GuionView({ content }) {
  return (
    <pre className="text-sm text-slate-300 whitespace-pre-wrap bg-slate-900 p-5 rounded-xl overflow-x-auto">
      {JSON.stringify(content, null, 2)}
    </pre>
  )
}

// ── Format renderer map ───────────────────────────────────────────────────────

const FORMAT_VIEWS = {
  Flashcards:          FlashcardsView,
  Tutorial:            TutorialView,
  'Resumen Ejecutivo': ExecutiveSummaryView,
  Quiz:                QuizView,
  Guion:               GuionView,
}

// ── Evaluation breakdown ──────────────────────────────────────────────────────

function EvaluationBreakdown({ evaluation }) {
  if (!evaluation?.criteria) return null
  return (
    <Card>
      <p className="text-sm font-semibold text-slate-300 mb-4">Evaluación del Critic Agent</p>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {Object.entries(evaluation.criteria).map(([key, val]) => (
          <div key={key} className="text-center">
            <p className="text-lg font-bold text-slate-100">{Math.round(val * 100)}%</p>
            <p className="text-xs text-slate-500 mt-0.5 capitalize">
              {key.replace(/_/g, ' ')}
            </p>
          </div>
        ))}
      </div>
    </Card>
  )
}

// ── Main component ────────────────────────────────────────────────────────────

/**
 * Renders the generated educational content based on the adaptation format.
 * Returns null if the adaptation is not completed or has no content.
 *
 * @param {Object} props
 * @param {import('@/shared/types').Adaptation} props.adaptation
 */
export function ContentViewer({ adaptation }) {
  if (!adaptation?.content || adaptation.status !== 'completed') return null

  const FormatIcon = FORMAT_ICONS[adaptation.format] ?? BookOpen
  const FormatView = FORMAT_VIEWS[adaptation.format]
  const { content, evaluation } = adaptation

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 bg-slate-800/60 rounded-xl border border-slate-700/50">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-brand-500 to-accent-500 flex items-center justify-center">
            <FormatIcon className="w-5 h-5 text-white" />
          </div>
          <div>
            <p className="font-semibold text-slate-100">{adaptation.format}</p>
            <div className="flex items-center gap-2 mt-0.5">
              <Badge variant="brand"   size="sm">{adaptation.profile}</Badge>
              <Badge variant="default" size="sm">{adaptation.industry}</Badge>
            </div>
          </div>
        </div>

        {evaluation && (
          <div className="flex items-center gap-4">
            <div className="text-right">
              <p className="text-xs text-slate-500">Calidad Critic</p>
              <p className="text-xs text-slate-400 mt-0.5">
                {evaluation.approved ? '✅ Aprobado' : '❌ No aprobado'}
              </p>
            </div>
            <ScoreRing score={evaluation.score} size={64} />
          </div>
        )}
      </div>

      {/* Format-specific content */}
      {FormatView ? (
        <FormatView content={content} />
      ) : (
        <pre className="text-sm text-slate-300 whitespace-pre-wrap bg-slate-900 p-5 rounded-xl">
          {JSON.stringify(content, null, 2)}
        </pre>
      )}

      <EvaluationBreakdown evaluation={evaluation} />
    </div>
  )
}
