import { FileText, FileCode, File } from 'lucide-react'
import { Badge } from '@/shared/ui/Badge'
import { cn, formatFileSize, formatDate } from '@/shared/utils'

// ── Type configuration ────────────────────────────────────────────────────────

const TYPE_CONFIG = {
  pdf: { icon: FileText, color: 'text-red-400'   },
  md:  { icon: FileCode, color: 'text-blue-400'  },
  txt: { icon: File,     color: 'text-slate-400' },
}

// ── Sub-components ────────────────────────────────────────────────────────────

/**
 * Icon representing a document type.
 * Can be used standalone outside of DocumentCard.
 *
 * @param {Object} props
 * @param {'pdf'|'md'|'txt'} props.type
 * @param {string} [props.className]
 */
export function DocumentTypeIcon({ type, className }) {
  const cfg  = TYPE_CONFIG[type] ?? { icon: File, color: 'text-slate-400' }
  const Icon = cfg.icon
  return <Icon className={cn('w-5 h-5', cfg.color, className)} />
}

// ── Component ─────────────────────────────────────────────────────────────────

/**
 * Row-style card for a single document.
 * Pass `onSelect` and `selected` to enable selection behaviour.
 *
 * @param {Object} props
 * @param {import('@/shared/types').Document} props.document
 * @param {(doc: import('@/shared/types').Document) => void} [props.onSelect]
 * @param {boolean} [props.selected]
 */
export function DocumentCard({ document, onSelect, selected = false }) {
  const isClickable = !!onSelect

  return (
    <div
      role={isClickable ? 'button' : undefined}
      tabIndex={isClickable ? 0 : undefined}
      onClick={isClickable ? () => onSelect(document) : undefined}
      onKeyDown={isClickable ? (e) => e.key === 'Enter' && onSelect(document) : undefined}
      className={cn(
        'flex items-center gap-4 p-4 rounded-xl border transition-all duration-200',
        isClickable && 'cursor-pointer focus:outline-none focus:ring-2 focus:ring-brand-500/50',
        selected
          ? 'bg-brand-600/10 border-brand-500/40'
          : 'bg-slate-800/60 border-slate-700/50 hover:border-slate-600'
      )}
    >
      <div className="w-10 h-10 rounded-lg bg-slate-700 flex items-center justify-center flex-shrink-0">
        <DocumentTypeIcon type={document.type} />
      </div>

      <div className="flex-1 min-w-0">
        <p className="font-medium text-slate-200 text-sm truncate">{document.title}</p>
        <div className="flex items-center gap-2 mt-1">
          <Badge variant="default" size="sm">{document.type?.toUpperCase()}</Badge>
          <span className="text-xs text-slate-500">{formatFileSize(document.size)}</span>
          <span className="text-xs text-slate-600">{formatDate(document.createdAt)}</span>
        </div>
      </div>

      {selected && (
        <div
          aria-label="Seleccionado"
          className="w-5 h-5 rounded-full bg-brand-500 flex items-center justify-center flex-shrink-0"
        >
          <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 12 12" aria-hidden="true">
            <path d="M10 3L5 8.5 2 5.5l-1 1 4 4 6-7-1-1z" />
          </svg>
        </div>
      )}
    </div>
  )
}
