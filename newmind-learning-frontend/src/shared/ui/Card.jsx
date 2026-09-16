import { cn } from '@/shared/utils'

// ── Card ──────────────────────────────────────────────────────────────────────

/**
 * Surface container with optional glassmorphism and hover effects.
 *
 * @param {Object} props
 * @param {boolean} [props.glass=true]  - Glassmorphism background
 * @param {boolean} [props.hover=false] - Interactive hover state
 * @param {string}  [props.className]
 * @param {React.ReactNode} props.children
 */
export function Card({ glass = true, hover = false, className, children, ...props }) {
  return (
    <div
      className={cn(
        'rounded-xl p-5',
        glass
          ? 'bg-slate-800/60 backdrop-blur-sm border border-slate-700/50'
          : 'bg-slate-800 border border-slate-700',
        hover && 'hover:border-slate-600 hover:bg-slate-800/80 transition-all duration-200 cursor-pointer',
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
}

// ── CardHeader ────────────────────────────────────────────────────────────────

/**
 * Standalone section header with title on the left and optional action on the right.
 * Does NOT render a Card wrapper — compose with Card when needed.
 *
 * @param {Object} props
 * @param {React.ReactNode} props.title
 * @param {React.ReactNode} [props.action]
 * @param {string} [props.className]
 */
export function CardHeader({ title, action, className }) {
  return (
    <div className={cn('flex items-center justify-between', className)}>
      <h3 className="text-base font-semibold text-slate-100">{title}</h3>
      {action && <div>{action}</div>}
    </div>
  )
}
