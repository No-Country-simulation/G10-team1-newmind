import { CheckCircle, Clock, AlertCircle, Loader } from 'lucide-react'
import { Badge } from '@/shared/ui/Badge'
import { cn, formatDate, truncate } from '@/shared/utils'

// ── Status configuration ──────────────────────────────────────────────────────

const STATUS_CONFIG = {
  completed:  { label: 'Completado', variant: 'success', Icon: CheckCircle },
  pending:    { label: 'Pendiente',  variant: 'warning', Icon: Clock       },
  processing: { label: 'Procesando', variant: 'info',    Icon: Loader      },
  failed:     { label: 'Error',      variant: 'danger',  Icon: AlertCircle },
}

const FALLBACK_STATUS = STATUS_CONFIG.pending

// ── Component ─────────────────────────────────────────────────────────────────

/**
 * Summary card for a single adaptation, used in lists and grids.
 * Pass `onClick` to make the card interactive.
 *
 * @param {Object} props
 * @param {import('@/shared/types').Adaptation} props.adaptation
 * @param {() => void} [props.onClick]
 */
export function AdaptationCard({ adaptation, onClick }) {
  const statusCfg = STATUS_CONFIG[adaptation.status] ?? FALLBACK_STATUS

  return (
    <article
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      onClick={onClick}
      onKeyDown={onClick ? (e) => e.key === 'Enter' && onClick() : undefined}
      className={cn(
        'p-4 rounded-xl border border-slate-700/50 bg-slate-800/60',
        'transition-all duration-200',
        onClick && 'cursor-pointer hover:border-slate-600 hover:bg-slate-800/80 focus:outline-none focus:ring-2 focus:ring-brand-500/50'
      )}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <p className="font-medium text-slate-200 text-sm truncate">
            {truncate(adaptation.documentTitle, 50)}
          </p>
          <div className="flex flex-wrap items-center gap-2 mt-2">
            <Badge variant="brand"   size="sm">{adaptation.profile}</Badge>
            <Badge variant="violet"  size="sm">{adaptation.format}</Badge>
            <Badge variant="default" size="sm">{adaptation.industry}</Badge>
          </div>
        </div>
        <Badge variant={statusCfg.variant} size="sm" dot>
          {statusCfg.label}
        </Badge>
      </div>

      <div className="flex items-center justify-between mt-3 pt-3 border-t border-slate-700/50">
        <span className="text-xs text-slate-500">{formatDate(adaptation.createdAt)}</span>
        {adaptation.evaluation && (
          <span className="text-xs font-medium text-emerald-400">
            Score {Math.round(adaptation.evaluation.score * 100)}%
          </span>
        )}
      </div>
    </article>
  )
}
