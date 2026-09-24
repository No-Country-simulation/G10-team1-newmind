import { useEffect, useState } from 'react'
import { Link, useParams, useLocation } from 'react-router-dom'
import { ArrowLeft, Download, RefreshCw } from 'lucide-react'
import { GenerationStatus } from '@/widgets/generation-status/GenerationStatus'
import { ContentViewer } from '@/widgets/content-viewer/ContentViewer'
import { adaptationsApi } from '@/shared/api'
import { Card } from '@/shared/ui/Card'
import { Badge } from '@/shared/ui/Badge'
import { Button } from '@/shared/ui/Button'
import { Alert } from '@/shared/ui/Alert'

// ── Polling helpers ────────────────────────────────────────────────────────────

const AGENT_SEQUENCE = ['orchestrator', 'researcher', 'context', 'generator', 'critic']
const POLL_INTERVAL_MS = 2_000

function usePipelineAgent(status) {
  const [currentAgent, setCurrentAgent] = useState(AGENT_SEQUENCE[0])

  useEffect(() => {
    if (status !== 'processing') return

    let index = 0
    const interval = setInterval(() => {
      index = Math.min(index + 1, AGENT_SEQUENCE.length - 1)
      setCurrentAgent(AGENT_SEQUENCE[index])
    }, 1800)

    return () => clearInterval(interval)
  }, [status])

  return { currentAgent }
}

function isTerminalStatus(status) {
  return status === 'completed' || status === 'failed'
}

function useAdaptationResult(id, initialAdaptation) {
  const [adaptation, setAdaptation] = useState(initialAdaptation)
  const [loading, setLoading] = useState(!initialAdaptation)
  const [error, setError] = useState(null)

  useEffect(() => {
    let ignore = false
    let timeoutId

    const loadFullAdaptation = async () => {
      const fullAdaptation = await adaptationsApi.get(id)
      if (!ignore) {
        setAdaptation(fullAdaptation)
      }
      return fullAdaptation
    }

    const pollStatus = async () => {
      try {
        const statusUpdate = await adaptationsApi.getStatus(id)
        if (ignore) return

        setError(null)
        setAdaptation((prev) => ({ ...prev, ...statusUpdate }))

        if (isTerminalStatus(statusUpdate.status)) {
          await loadFullAdaptation()
          return
        }

        timeoutId = setTimeout(pollStatus, POLL_INTERVAL_MS)
      } catch (err) {
        if (!ignore) setError(err.message ?? 'Error al consultar el estado de la adaptación.')
      } finally {
        if (!ignore) setLoading(false)
      }
    }

    if (initialAdaptation && !isTerminalStatus(initialAdaptation.status)) {
      timeoutId = setTimeout(pollStatus, POLL_INTERVAL_MS)
    } else {
      loadFullAdaptation()
        .then((fullAdaptation) => {
          if (!ignore && !isTerminalStatus(fullAdaptation.status)) {
            timeoutId = setTimeout(pollStatus, POLL_INTERVAL_MS)
          }
          if (!ignore) setError(null)
        })
        .catch((err) => {
          if (!ignore) setError(err.message ?? 'Error al cargar la adaptación.')
        })
        .finally(() => {
          if (!ignore) setLoading(false)
        })
    }

    return () => {
      ignore = true
      clearTimeout(timeoutId)
    }
  }, [id, initialAdaptation])

  return { adaptation, loading, error }
}

// ── Sub-components ────────────────────────────────────────────────────────────

function AdaptationMeta({ adaptation }) {
  return (
    <div>
      <h1 className="page-title">{adaptation.documentTitle ?? 'Resultado'}</h1>
      <div className="flex flex-wrap items-center gap-2 mt-2">
        <Badge variant="brand">{adaptation.profile}</Badge>
        <Badge variant="violet">{adaptation.format}</Badge>
        <Badge variant="default">{adaptation.industry}</Badge>
        <Badge variant="default">{adaptation.detailLevel}</Badge>
      </div>
    </div>
  )
}

function PageHeader({ adaptation }) {
  return (
    <div className="flex items-center justify-between">
      <Link to="/" className="btn-ghost text-sm flex items-center gap-1.5">
        <ArrowLeft className="w-4 h-4" />
        Dashboard
      </Link>
      {adaptation.status === 'completed' && (
        <Button variant="secondary" size="sm" leftIcon={<Download className="w-4 h-4" />}>
          Exportar
        </Button>
      )}
    </div>
  )
}

// ── Page ──────────────────────────────────────────────────────────────────────

export function ResultPage() {
  const { id } = useParams()
  const { state } = useLocation()

  const { adaptation, loading, error } = useAdaptationResult(id, state?.adaptation ?? null)
  const { currentAgent } = usePipelineAgent(adaptation?.status)

  if (loading && !adaptation) {
    return (
      <div className="max-w-3xl mx-auto">
        <Card>
          <p className="text-sm text-slate-400">Cargando adaptación...</p>
        </Card>
      </div>
    )
  }

  if (!adaptation) {
    return (
      <div className="max-w-3xl mx-auto">
        <Alert variant="error" title="Adaptación no encontrada">
          {error ?? 'No se pudo cargar la información de esta adaptación.'}
          <Link to="/history" className="block mt-2 text-sm underline">
            Ver historial
          </Link>
        </Alert>
      </div>
    )
  }

  const isProcessing = adaptation.status === 'processing' || adaptation.status === 'pending'

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-fade-in">
      <PageHeader adaptation={adaptation} />
      <AdaptationMeta adaptation={adaptation} />

      {error && (
        <Alert variant="error" title="No se pudo actualizar el estado">
          {error}
        </Alert>
      )}

      {/* Pipeline status */}
      {isProcessing && (
        <Card>
          <GenerationStatus
            status={adaptation.status}
            currentAgent={currentAgent}
            iteration={0}
            maxIterations={3}
          />
        </Card>
      )}

      {/* Completed content */}
      {adaptation.status === 'completed' && (
        <ContentViewer adaptation={adaptation} />
      )}

      {/* Failed */}
      {adaptation.status === 'failed' && (
        <Alert variant="error" title="Error en la generación">
          {adaptation.error ?? 'Ocurrió un error durante el procesamiento.'}
          <div className="mt-3">
            <Link to="/new">
              <Button variant="secondary" size="sm" leftIcon={<RefreshCw className="w-4 h-4" />}>
                Intentar nuevamente
              </Button>
            </Link>
          </div>
        </Alert>
      )}
    </div>
  )
}
