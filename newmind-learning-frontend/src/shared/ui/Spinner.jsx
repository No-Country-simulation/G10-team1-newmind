import { cn } from '@/shared/utils'

const SIZES = {
  sm: 'w-4 h-4',
  md: 'w-6 h-6',
  lg: 'w-10 h-10',
}

// ── Spinner ───────────────────────────────────────────────────────────────────

/**
 * Animated loading spinner.
 *
 * @param {Object} props
 * @param {'sm'|'md'|'lg'} [props.size='md']
 * @param {string} [props.className]
 */
export function Spinner({ size = 'md', className }) {
  return (
    <span
      role="status"
      aria-label="Cargando"
      className={cn(
        'border-2 border-brand-500 border-t-transparent rounded-full animate-spin inline-block',
        SIZES[size],
        className
      )}
    />
  )
}

// ── PageLoader ────────────────────────────────────────────────────────────────

/**
 * Vertically centered full-area loading state.
 *
 * @param {Object} props
 * @param {string} [props.message='Cargando...']
 */
export function PageLoader({ message = 'Cargando...' }) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[400px] gap-4">
      <Spinner size="lg" />
      <p className="text-slate-400 text-sm">{message}</p>
    </div>
  )
}

// ── Skeleton ──────────────────────────────────────────────────────────────────

/**
 * Pulse placeholder for content that is loading.
 *
 * @param {Object} props
 * @param {string} [props.className] - Use to set width/height (e.g. "h-4 w-32")
 */
export function Skeleton({ className }) {
  return (
    <div
      aria-hidden="true"
      className={cn('bg-slate-700/60 rounded-md animate-pulse', className)}
    />
  )
}
