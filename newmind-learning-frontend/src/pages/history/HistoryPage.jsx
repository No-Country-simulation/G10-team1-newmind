import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { History, Search, Filter, PlusCircle } from 'lucide-react'
import { AdaptationCard } from '@/entities/adaptation/ui/AdaptationCard'
import { adaptationsApi } from '@/shared/api'
import { Input, Select } from '@/shared/ui/Input'
import { Button } from '@/shared/ui/Button'
import { Alert, EmptyState } from '@/shared/ui/Alert'
import { Badge } from '@/shared/ui/Badge'
import { PROFILES, FORMATS } from '@/shared/types'

// ── Filtering logic ───────────────────────────────────────────────────────────

function useHistoryFilters() {
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

  return {
    search, setSearch,
    filterProfile, setFilterProfile,
    filterFormat, setFilterFormat,
    filterStatus, setFilterStatus,
    hasActiveFilters, clearFilters,
  }
}

function useAdaptationHistory(filters) {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let ignore = false

    const loadHistory = async () => {
      setLoading(true)
      setError(null)
      try {
        const data = await adaptationsApi.list({
          profile: filters.filterProfile || undefined,
          format: filters.filterFormat || undefined,
          status: filters.filterStatus || undefined,
        })
        if (!ignore) setItems(data)
      } catch (err) {
        if (!ignore) setError(err.message ?? 'Error al cargar el historial.')
      } finally {
        if (!ignore) setLoading(false)
      }
    }

    loadHistory()

    return () => {
      ignore = true
    }
  }, [filters.filterProfile, filters.filterFormat, filters.filterStatus])

  return { items, loading, error }
}

/*
  Search remains client-side because the backend contract currently exposes
  profile, format, and status filters only.
*/
function filterBySearch(items, search) {
  const normalizedSearch = search.toLowerCase()
  return items.filter((a) => {
    return !search || a.documentTitle.toLowerCase().includes(normalizedSearch)
  })
}

// ── Page ──────────────────────────────────────────────────────────────────────

export function HistoryPage() {
  const navigate = useNavigate()

  const filters = useHistoryFilters()
  const { items, loading, error } = useAdaptationHistory(filters)
  const filtered = filterBySearch(items, filters.search)

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
            {loading ? 'Cargando adaptaciones...' : `${items.length} adaptaciones generadas`}
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
          value={filters.search}
          onChange={(e) => filters.setSearch(e.target.value)}
          leftIcon={<Search className="w-4 h-4" />}
        />
        <Select value={filters.filterProfile} onChange={(e) => filters.setFilterProfile(e.target.value)}>
          <option value="">Todos los perfiles</option>
          {PROFILES.map((p) => (
            <option key={p.value} value={p.value}>{p.label}</option>
          ))}
        </Select>
        <Select value={filters.filterFormat} onChange={(e) => filters.setFilterFormat(e.target.value)}>
          <option value="">Todos los formatos</option>
          {FORMATS.map((f) => (
            <option key={f.value} value={f.value}>{f.label}</option>
          ))}
        </Select>
        <Select value={filters.filterStatus} onChange={(e) => filters.setFilterStatus(e.target.value)}>
          <option value="">Todos los estados</option>
          <option value="completed">Completado</option>
          <option value="processing">Procesando</option>
          <option value="pending">Pendiente</option>
          <option value="failed">Error</option>
        </Select>
      </div>

      {/* Active filter pills */}
      {filters.hasActiveFilters && (
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-xs text-slate-500 flex items-center gap-1">
            <Filter className="w-3.5 h-3.5" /> Filtros activos:
          </span>
          {filters.filterProfile && <Badge variant="brand"  size="sm">{filters.filterProfile}</Badge>}
          {filters.filterFormat  && <Badge variant="violet" size="sm">{filters.filterFormat}</Badge>}
          {filters.filterStatus  && <Badge variant="info"   size="sm">{filters.filterStatus}</Badge>}
          <button
            onClick={filters.clearFilters}
            className="text-xs text-slate-500 hover:text-slate-300 underline transition-colors"
          >
            Limpiar
          </button>
        </div>
      )}

      {/* Results */}
      {error && (
        <Alert variant="error" title="No se pudo cargar el historial">
          {error}
        </Alert>
      )}

      {loading ? (
        <p className="text-sm text-slate-400">Cargando historial...</p>
      ) : filtered.length === 0 ? (
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
