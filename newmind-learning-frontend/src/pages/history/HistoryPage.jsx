import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { History, Search, Filter, PlusCircle } from 'lucide-react'
import { AdaptationCard } from '@/entities/adaptation/ui/AdaptationCard'
import { Input, Select } from '@/shared/ui/Input'
import { Button } from '@/shared/ui/Button'
import { EmptyState } from '@/shared/ui/Alert'
import { Badge } from '@/shared/ui/Badge'
import { PROFILES, FORMATS } from '@/shared/types'

// ── Mock data — replace with adaptationsApi.list() when backend is ready ──────

const MOCK_HISTORY = [
  {
    id: 1,
    documentTitle: 'Introducción a la Arquitectura de Redes VCN en OCI',
    profile: 'Principiante',
    format: 'Flashcards',
    industry: 'General',
    detailLevel: 'Didactico',
    status: 'completed',
    evaluation: { score: 0.92, approved: true },
    createdAt: '2026-09-15T10:00:00Z',
  },
  {
    id: 2,
    documentTitle: 'Introducción a la Arquitectura de Redes VCN en OCI',
    profile: 'Junior',
    format: 'Tutorial',
    industry: 'E-commerce',
    detailLevel: 'Intermedio',
    status: 'completed',
    evaluation: { score: 0.88, approved: true },
    createdAt: '2026-09-15T11:30:00Z',
  },
  {
    id: 3,
    documentTitle: 'Guía de PostgreSQL para aplicaciones FastAPI',
    profile: 'Lider',
    format: 'Resumen Ejecutivo',
    industry: 'Fintech',
    detailLevel: 'Detallado',
    status: 'completed',
    evaluation: { score: 0.94, approved: true },
    createdAt: '2026-09-14T09:00:00Z',
  },
  {
    id: 4,
    documentTitle: 'Arquitectura Hexagonal en Python',
    profile: 'Junior',
    format: 'Quiz',
    industry: 'General',
    detailLevel: 'Intermedio',
    status: 'failed',
    createdAt: '2026-09-13T16:00:00Z',
  },
  {
    id: 5,
    documentTitle: 'Fundamentos de LangGraph y LangChain',
    profile: 'Lider',
    format: 'Tutorial',
    industry: 'General',
    detailLevel: 'Detallado',
    status: 'completed',
    evaluation: { score: 0.90, approved: true },
    createdAt: '2026-09-12T12:00:00Z',
  },
]

// ── Filtering logic ───────────────────────────────────────────────────────────

function useHistoryFilters(items) {
  const [search, setSearch]             = useState('')
  const [filterProfile, setFilterProfile] = useState('')
  const [filterFormat, setFilterFormat]   = useState('')
  const [filterStatus, setFilterStatus]   = useState('')

  const hasActiveFilters = !!(filterProfile || filterFormat || filterStatus)

  const clearFilters = () => {
    setFilterProfile('')
    setFilterFormat('')
    setFilterStatus('')
  }

  const filtered = items.filter((a) => {
    const matchSearch  = !search        || a.documentTitle.toLowerCase().includes(search.toLowerCase())
    const matchProfile = !filterProfile || a.profile === filterProfile
    const matchFormat  = !filterFormat  || a.format  === filterFormat
    const matchStatus  = !filterStatus  || a.status  === filterStatus
    return matchSearch && matchProfile && matchFormat && matchStatus
  })

  return {
    search, setSearch,
    filterProfile, setFilterProfile,
    filterFormat, setFilterFormat,
    filterStatus, setFilterStatus,
    hasActiveFilters, clearFilters,
    filtered,
  }
}

// ── Page ──────────────────────────────────────────────────────────────────────

export function HistoryPage() {
  const navigate = useNavigate()

  const {
    search, setSearch,
    filterProfile, setFilterProfile,
    filterFormat, setFilterFormat,
    filterStatus, setFilterStatus,
    hasActiveFilters, clearFilters,
    filtered,
  } = useHistoryFilters(MOCK_HISTORY)

  const handleCardClick = (adaptation) => {
    navigate(`/result/${adaptation.id}`, { state: { adaptation } })
  }

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="page-title flex items-center gap-3">
            <History className="w-6 h-6 text-brand-400" />
            Historial
          </h1>
          <p className="text-slate-400 mt-1">
            {MOCK_HISTORY.length} adaptaciones generadas
          </p>
        </div>
        <Link to="/new">
          <Button variant="primary" leftIcon={<PlusCircle className="w-4 h-4" />}>
            Nueva adaptación
          </Button>
        </Link>
      </div>

      {/* Filters */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        <Input
          placeholder="Buscar por documento..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          leftIcon={<Search className="w-4 h-4" />}
        />
        <Select value={filterProfile} onChange={(e) => setFilterProfile(e.target.value)}>
          <option value="">Todos los perfiles</option>
          {PROFILES.map((p) => (
            <option key={p.value} value={p.value}>{p.label}</option>
          ))}
        </Select>
        <Select value={filterFormat} onChange={(e) => setFilterFormat(e.target.value)}>
          <option value="">Todos los formatos</option>
          {FORMATS.map((f) => (
            <option key={f.value} value={f.value}>{f.label}</option>
          ))}
        </Select>
        <Select value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)}>
          <option value="">Todos los estados</option>
          <option value="completed">Completado</option>
          <option value="processing">Procesando</option>
          <option value="pending">Pendiente</option>
          <option value="failed">Error</option>
        </Select>
      </div>

      {/* Active filter pills */}
      {hasActiveFilters && (
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-xs text-slate-500 flex items-center gap-1">
            <Filter className="w-3.5 h-3.5" /> Filtros activos:
          </span>
          {filterProfile && <Badge variant="brand"  size="sm">{filterProfile}</Badge>}
          {filterFormat  && <Badge variant="violet" size="sm">{filterFormat}</Badge>}
          {filterStatus  && <Badge variant="info"   size="sm">{filterStatus}</Badge>}
          <button
            onClick={clearFilters}
            className="text-xs text-slate-500 hover:text-slate-300 underline transition-colors"
          >
            Limpiar
          </button>
        </div>
      )}

      {/* Results */}
      {filtered.length === 0 ? (
        <EmptyState
          icon={History}
          title="No se encontraron adaptaciones"
          description="Probá ajustando los filtros o creá una nueva adaptación."
          action={
            <Link to="/new">
              <Button variant="primary" size="sm">Nueva adaptación</Button>
            </Link>
          }
        />
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {filtered.map((adaptation) => (
            <AdaptationCard
              key={adaptation.id}
              adaptation={adaptation}
              onClick={() => handleCardClick(adaptation)}
            />
          ))}
        </div>
      )}
    </div>
  )
}
