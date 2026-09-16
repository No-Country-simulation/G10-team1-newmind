import { cn } from '@/shared/utils'

// ── Variant maps ──────────────────────────────────────────────────────────────

const ALERT_VARIANTS = {
  success: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300',
  error:   'bg-red-500/10    border-red-500/30    text-red-300',
  warning: 'bg-amber-500/10  border-amber-500/30  text-amber-300',
  info:    'bg-blue-500/10   border-blue-500/30   text-blue-300',
}

const SCORE_COLOR = (score) => {
  if (score >= 0.8) return '#34d399' // emerald-400
  if (score >= 0.6) return '#fbbf24' // amber-400
  return '#f87171'                   // red-400
}

// ── Alert ─────────────────────────────────────────────────────────────────────

/**
 * Alert / notification banner.
 *
 * @param {Object} props
 * @param {'success'|'error'|'warning'|'info'} [props.variant='info']
 * @param {string} [props.title]
 * @param {string} [props.className]
 * @param {React.ReactNode} props.children
 */
export function Alert({ variant = 'info', title, className, children }) {
  return (
    <div
      role="alert"
      className={cn(
        'rounded-lg border px-4 py-3 text-sm',
        ALERT_VARIANTS[variant],
        className
      )}
    >
      {title && <p className="font-semibold mb-1">{title}</p>}
      {children}
    </div>
  )
}

// ── EmptyState ────────────────────────────────────────────────────────────────

/**
 * Empty state placeholder with optional icon, description and action slot.
 *
 * @param {Object} props
 * @param {React.ElementType} [props.icon]
 * @param {string} props.title
 * @param {string} [props.description]
 * @param {React.ReactNode} [props.action]
 */
export function EmptyState({ icon: Icon, title, description, action }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 gap-4 text-center">
      {Icon && (
        <div className="w-16 h-16 rounded-2xl bg-slate-800 flex items-center justify-center">
          <Icon className="w-8 h-8 text-slate-500" />
        </div>
      )}
      <div>
        <p className="text-slate-300 font-medium">{title}</p>
        {description && (
          <p className="text-slate-500 text-sm mt-1">{description}</p>
        )}
      </div>
      {action}
    </div>
  )
}

// ── ScoreRing ─────────────────────────────────────────────────────────────────

/**
 * Circular SVG progress ring that displays a 0–1 score as a percentage.
 * Color transitions: green ≥ 0.8 · amber ≥ 0.6 · red < 0.6.
 *
 * @param {Object} props
 * @param {number} props.score - Value between 0 and 1
 * @param {number} [props.size=80] - Outer diameter in px
 */
export function ScoreRing({ score, size = 80 }) {
  const strokeWidth = 6
  const radius      = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * radius
  const offset        = circumference - score * circumference
  const color         = SCORE_COLOR(score)
  const center        = size / 2

  return (
    <svg
      width={size}
      height={size}
      viewBox={`0 0 ${size} ${size}`}
      aria-label={`Score: ${Math.round(score * 100)}%`}
      role="img"
    >
      {/* Track */}
      <circle
        cx={center}
        cy={center}
        r={radius}
        fill="none"
        stroke="#334155"
        strokeWidth={strokeWidth}
      />
      {/* Progress — rotated from top via transform on the SVG */}
      <circle
        cx={center}
        cy={center}
        r={radius}
        fill="none"
        stroke={color}
        strokeWidth={strokeWidth}
        strokeDasharray={circumference}
        strokeDashoffset={offset}
        strokeLinecap="round"
        transform={`rotate(-90 ${center} ${center})`}
        style={{ transition: 'stroke-dashoffset 0.8s ease' }}
      />
      {/* Label */}
      <text
        x={center}
        y={center}
        dominantBaseline="central"
        textAnchor="middle"
        fill={color}
        fontSize={Math.round(size * 0.175)}
        fontWeight={600}
      >
        {Math.round(score * 100)}%
      </text>
    </svg>
  )
}
