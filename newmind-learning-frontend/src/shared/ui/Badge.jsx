import { cn } from '@/shared/utils'

// ── Variant / size maps ───────────────────────────────────────────────────────

const VARIANTS = {
  default: 'bg-slate-700 text-slate-300',
  brand:   'bg-brand-500/20   text-brand-300   border border-brand-500/30',
  success: 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30',
  warning: 'bg-amber-500/20   text-amber-300   border border-amber-500/30',
  danger:  'bg-red-500/20     text-red-300     border border-red-500/30',
  info:    'bg-blue-500/20    text-blue-300    border border-blue-500/30',
  violet:  'bg-violet-500/20  text-violet-300  border border-violet-500/30',
}

const DOT_COLORS = {
  default: 'bg-slate-400',
  brand:   'bg-brand-400',
  success: 'bg-emerald-400',
  warning: 'bg-amber-400',
  danger:  'bg-red-400',
  info:    'bg-blue-400',
  violet:  'bg-violet-400',
}

const SIZES = {
  sm: 'px-2   py-0.5 text-xs',
  md: 'px-2.5 py-1   text-xs',
  lg: 'px-3   py-1   text-sm',
}

// ── Component ─────────────────────────────────────────────────────────────────

/**
 * Pill-shaped status / category label.
 *
 * @param {Object} props
 * @param {'default'|'brand'|'success'|'warning'|'danger'|'info'|'violet'} [props.variant='default']
 * @param {'sm'|'md'|'lg'} [props.size='md']
 * @param {boolean} [props.dot] - Prepend a colored indicator dot
 * @param {string} [props.className]
 * @param {React.ReactNode} props.children
 */
export function Badge({
  variant = 'default',
  size = 'md',
  dot = false,
  className,
  children,
}) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 font-medium rounded-full',
        VARIANTS[variant],
        SIZES[size],
        className
      )}
    >
      {dot && (
        <span
          className={cn('w-1.5 h-1.5 rounded-full', DOT_COLORS[variant])}
        />
      )}
      {children}
    </span>
  )
}
