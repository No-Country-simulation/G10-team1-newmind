import { useEffect, useState } from 'react'
import { Link, useParams, useLocation } from 'react-router-dom'
import { ArrowLeft, Download, RefreshCw } from 'lucide-react'
import { GenerationStatus } from '@/widgets/generation-status/GenerationStatus'
import { ContentViewer } from '@/widgets/content-viewer/ContentViewer'
import { Card } from '@/shared/ui/Card'
import { Badge } from '@/shared/ui/Badge'
import { Button } from '@/shared/ui/Button'
import { Alert } from '@/shared/ui/Alert'

// ── Mock pipeline simulation — remove when real API polling is implemented ────

const AGENT_SEQUENCE = ['orchestrator', 'researcher', 'context', 'generator', 'critic']

/** Simulated completed adaptation for demo purposes. */
const MOCK_COMPLETED = {
  status: 'completed',
  evaluation: {
    score: 0.92,
    approved: true,
    criteria: {
      fidelity:          0.95,
      profile_alignment: 0.90,
      format_compliance: 0.94,
      coherence:         0.91,
    },
    issues: [],
  },
  content: {
    cards: [
      {
        concept: 'VCN',
        question: '¿Qué es una VCN en OCI?',
        answer: 'Una Virtual Cloud Network (VCN) es una red privada definida por software dentro de Oracle Cloud Infrastructure.',
        difficulty: 'Básico',
        source: 'Sección 1',
      },
      {
        concept: 'Subnet',
        question: '¿Para qué sirve una subnet en una VCN?',
        answer: 'Divide la VCN en segmentos más pequeños para organizar recursos y controlar el tráfico de red.',
        difficulty: 'Básico',
        source: 'Sección 2',
      },
      {
        concept: 'Internet Gateway',
        question: '¿Qué función tiene un Internet Gateway?',
        answer: 'Permite que los recursos dentro de la VCN se comuniquen con internet de forma bidireccional.',
        difficulty: 'Intermedio',
        source: 'Sección 3',
      },
      {
        concept: 'Route Table',
        question: '¿Qué es una Route Table?',
        answer: 'Define las reglas de enrutamiento para determinar a dónde va el tráfico de red dentro y fuera de la VCN.',
        difficulty: 'Intermedio',
        source: 'Sección 4',
      },
    ],
  },
}

// ── Custom hook — pipeline simulation ────────────────────────────────────────

function usePipelineSimulation(initialStatus, onComplete) {
  const [currentAgent, setCurrentAgent] = useState(AGENT_SEQUENCE[0])

  useEffect(() => {
    if (initialStatus !== 'processing') return

    let index = 0
    const interval = setInterval(() => {
      if (index >= AGENT_SEQUENCE.length - 1) {
        clearInterval(interval)
        onComplete()
        return
      }
      index++
      setCurrentAgent(AGENT_SEQUENCE[index])
    }, 1800)

    return () => clearInterval(interval)
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialStatus])

  return { currentAgent }
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
  useParams() // id available for future API polling: const { id } = useParams()
  const { state } = useLocation()

  const [adaptation, setAdaptation] = useState(state?.adaptation ?? null)

  const handlePipelineComplete = () => {
    setAdaptation((prev) => ({ ...prev, ...MOCK_COMPLETED }))
  }

  const { currentAgent } = usePipelineSimulation(
    adaptation?.status,
    handlePipelineComplete
  )

  if (!adaptation) {
    return (
      <div className="max-w-3xl mx-auto">
        <Alert variant="error" title="Adaptación no encontrada">
          No se pudo cargar la información de esta adaptación.
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
          Ocurrió un error durante el procesamiento. El Critic Agent rechazó el contenido tras agotar los intentos.
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
