import { cn } from '@/shared/utils'
import { CheckCircle, Circle, Loader, AlertCircle } from 'lucide-react'

// ── Constants ─────────────────────────────────────────────────────────────────

const AGENT_STEPS = [
  { id: 'orchestrator', label: 'Orchestrator Agent',     description: 'Analizando solicitud y definiendo ruta' },
  { id: 'researcher',   label: 'RAG Researcher Agent',   description: 'Recuperando fragmentos relevantes del documento' },
  { id: 'context',      label: 'Context/Profile Agent',  description: 'Adaptando al perfil e instrucciones pedagógicas' },
  { id: 'generator',    label: 'Educational Generator',  description: 'Generando contenido educativo estructurado' },
  { id: 'critic',       label: 'Critic Agent',           description: 'Evaluando calidad, fidelidad y coherencia' },
]

const STATUS_LABELS = {
  processing: 'Generando contenido...',
  completed:  '¡Contenido generado!',
  failed:     'Error en la generación',
  pending:    'En espera',
}

// ── Step status derivation ────────────────────────────────────────────────────

/**
 * @param {'pending'|'processing'|'completed'|'failed'} pipelineStatus
 * @param {string} currentAgentId
 * @param {string} stepId
 * @returns {'done'|'active'|'idle'|'error'}
 */
function deriveStepStatus(pipelineStatus, currentAgentId, stepId) {
  if (pipelineStatus === 'completed') return 'done'

  const currentIdx = AGENT_STEPS.findIndex((s) => s.id === currentAgentId)
  const stepIdx    = AGENT_STEPS.findIndex((s) => s.id === stepId)

  if (pipelineStatus === 'failed') {
    return stepIdx <= currentIdx ? 'error' : 'idle'
  }

  if (stepIdx < currentIdx)  return 'done'
  if (stepIdx === currentIdx) return 'active'
  return 'idle'
}

// ── Sub-components ────────────────────────────────────────────────────────────

const STEP_ICON = {
  done:   <CheckCircle className="w-5 h-5 text-emerald-400" />,
  active: <Loader      className="w-5 h-5 text-brand-400 animate-spin" />,
  idle:   <Circle      className="w-5 h-5 text-slate-600" />,
  error:  <AlertCircle className="w-5 h-5 text-red-400" />,
}

const STEP_LABEL_CLASS = {
  active: 'text-brand-300',
  done:   'text-slate-300',
  error:  'text-red-300',
  idle:   'text-slate-500',
}

function AgentStep({ agent, stepStatus }) {
  return (
    <div
      className={cn(
        'flex items-center gap-3 p-3 rounded-lg transition-all duration-300',
        stepStatus === 'active' && 'bg-brand-600/10 border border-brand-600/20',
        stepStatus === 'done'   && 'opacity-70',
        stepStatus === 'idle'   && 'opacity-40',
        stepStatus === 'error'  && 'bg-red-500/10 border border-red-500/20'
      )}
    >
      <div className="flex-shrink-0">{STEP_ICON[stepStatus]}</div>
      <div className="flex-1 min-w-0">
        <p className={cn('text-sm font-medium', STEP_LABEL_CLASS[stepStatus])}>
          {agent.label}
        </p>
        {stepStatus === 'active' && (
          <p className="text-xs text-slate-500 mt-0.5">{agent.description}</p>
        )}
      </div>
    </div>
  )
}

// ── Main component ────────────────────────────────────────────────────────────

/**
 * Visualises the multiagent pipeline progress.
 *
 * @param {Object} props
 * @param {'pending'|'processing'|'completed'|'failed'} props.status
 * @param {string}  [props.currentAgent]   - id of the agent currently running
 * @param {number}  [props.iteration=0]    - current Critic iteration
 * @param {number}  [props.maxIterations=3]
 */
export function GenerationStatus({ status, currentAgent, iteration = 0, maxIterations = 3 }) {
  const currentIdx  = AGENT_STEPS.findIndex((s) => s.id === currentAgent)
  const progressPct = ((currentIdx + 1) / AGENT_STEPS.length) * 100

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <p className="font-semibold text-slate-200">
            {STATUS_LABELS[status] ?? STATUS_LABELS.pending}
          </p>
          {status === 'processing' && (
            <p className="text-xs text-slate-500 mt-0.5">Sistema multiagente activo</p>
          )}
        </div>
        {iteration > 0 && (
          <div className="text-xs text-amber-400 bg-amber-400/10 border border-amber-400/20 px-2.5 py-1 rounded-full">
            Iteración {iteration}/{maxIterations}
          </div>
        )}
      </div>

      {/* Progress bar */}
      {status === 'processing' && (
        <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden" role="progressbar" aria-valuenow={progressPct} aria-valuemin={0} aria-valuemax={100}>
          <div
            className="h-full bg-gradient-to-r from-brand-500 to-accent-500 rounded-full"
            style={{ width: `${progressPct}%`, transition: 'width 0.5s ease' }}
          />
        </div>
      )}

      {/* Agent steps */}
      <div className="space-y-2">
        {AGENT_STEPS.map((agent) => (
          <AgentStep
            key={agent.id}
            agent={agent}
            stepStatus={deriveStepStatus(status, currentAgent, agent.id)}
          />
        ))}
      </div>
    </div>
  )
}
