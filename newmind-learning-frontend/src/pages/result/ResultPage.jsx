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
import { ADAPTATION_POLL_POLICY } from './adaptationPolling'

// ── Polling helpers ────────────────────────────────────────────────────────────

const AGENT_SEQUENCE = ['orchestrator', 'researcher', 'context', 'generator', 'critic']

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
  const [pollRun, setPollRun] = useState(0)

  useEffect(() => {
    let active = true
    let timeoutId
    let activeStatusController
    let attempts = 0

    const loadFullAdaptation = async () => {
      const fullAdaptation = await adaptationsApi.get(id)
      if (active) {
        setAdaptation(fullAdaptation)
      }
      return fullAdaptation
    }

    const scheduleNextPoll = () => {
      timeoutId = setTimeout(pollStatus, ADAPTATION_POLL_POLICY.intervalMs)
    }

    const pollStatus = async () => {
      if (!active) return

      const controller = new AbortController()
      activeStatusController = controller
      attempts += 1

      try {
        const statusUpdate = await adaptationsApi.getStatus(id, {
          signal: controller.signal,
        })
        if (!active) return

        setError(null)
        setAdaptation((prev) => ({ ...prev, ...statusUpdate }))

        if (isTerminalStatus(statusUpdate.status)) {
          await loadFullAdaptation()
          return
        }

        if (attempts >= ADAPTATION_POLL_POLICY.maxAttempts) {
          setError(
            'Se agotó el tiempo de espera para completar la adaptación. Reintenta la consulta o vuelve al historial.'
          )
          return
        }

        scheduleNextPoll()
      } catch (err) {
        if (active) {
          setError(err.message ?? 'Error al consultar el estado de la adaptación.')
        }
      } finally {
        if (activeStatusController === controller) {
          activeStatusController = undefined
        }
        if (active) setLoading(false)
      }
    }

    if (initialAdaptation && !isTerminalStatus(initialAdaptation.status)) {
      if (pollRun > 0) {
        pollStatus()
      } else {
        scheduleNextPoll()
      }
    } else {
      loadFullAdaptation()
        .then((fullAdaptation) => {
          if (active && !isTerminalStatus(fullAdaptation.status)) {
            scheduleNextPoll()
          }
          if (active) setError(null)
        })
        .catch((err) => {
          if (active) setError(err.message ?? 'Error al cargar la adaptación.')
        })
        .finally(() => {
          if (active) setLoading(false)
        })
    }

    return () => {
      active = false
      clearTimeout(timeoutId)
      activeStatusController?.abort()
    }
  }, [id, initialAdaptation, pollRun])

  const retryPolling = () => {
    setError(null)
    setPollRun((currentRun) => currentRun + 1)
  }

  return { adaptation, loading, error, retryPolling }
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

  const { adaptation, loading, error, retryPolling } = useAdaptationResult(
    id,
    state?.adaptation ?? null
  )
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
          <p>{error}</p>
          <div className="mt-3 flex flex-wrap gap-2">
            <Button variant="secondary" size="sm" onClick={retryPolling}>
              Reintentar consulta
            </Button>
            <Link to="/history" className="btn-ghost text-sm">
              Ver historial
            </Link>
          </div>
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
          <div className="mt-3 flex flex-wrap gap-2">
            <Link to="/new">
              <Button variant="secondary" size="sm" leftIcon={<RefreshCw className="w-4 h-4" />}>
                Intentar nuevamente
              </Button>
            </Link>
            <Link to="/history" className="btn-ghost text-sm">
              Ver historial
            </Link>
          </div>
        </Alert>
      )}
    </div>
  )
}
