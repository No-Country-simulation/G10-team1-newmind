import { cn } from '@/shared/utils'

// ── Variant / size maps ───────────────────────────────────────────────────────

const VARIANTS = {
  primary:   'bg-brand-600 hover:bg-brand-500 text-white focus:ring-brand-500',
  secondary: 'bg-slate-700 hover:bg-slate-600 text-slate-200 focus:ring-slate-500',
  ghost:     'text-slate-400 hover:text-slate-100 hover:bg-slate-800 focus:ring-slate-500',
  danger:    'bg-red-600/20     hover:bg-red-600/30     text-red-400     border border-red-500/30     focus:ring-red-500',
  success:   'bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-400 border border-emerald-500/30 focus:ring-emerald-500',
}

const SIZES = {
  sm: 'px-3 py-1.5 text-sm  gap-1.5',
  md: 'px-4 py-2   text-sm  gap-2',
  lg: 'px-5 py-2.5 text-base gap-2',
}

// ── Component ─────────────────────────────────────────────────────────────────

/**
 * Base button component.
 * Renders a <button> element; for link-style navigation compose with react-router Link externally.
 *
 * @param {Object} props
 * @param {'primary'|'secondary'|'ghost'|'danger'|'success'} [props.variant='primary']
 * @param {'sm'|'md'|'lg'} [props.size='md']
 * @param {boolean} [props.loading=false] - Shows spinner and disables interaction
 * @param {boolean} [props.fullWidth=false]
 * @param {React.ReactNode} [props.leftIcon]
 * @param {React.ReactNode} [props.rightIcon]
 * @param {boolean} [props.disabled]
 */
export function Button({
  variant = 'primary',
  size = 'md',
  loading = false,
  fullWidth = false,
  leftIcon,
  rightIcon,
  className,
  children,
  disabled,
  ...props
}) {
  const isDisabled = disabled || loading

  return (
    <button
      disabled={isDisabled}
      aria-busy={loading}
      className={cn(
        'inline-flex items-center justify-center font-medium rounded-lg',
        'transition-all duration-200',
        'focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-900',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        VARIANTS[variant],
        SIZES[size],
        fullWidth && 'w-full',
        className
      )}
      {...props}
    >
      {loading ? (
        <span
          aria-hidden="true"
          className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin"
        />
      ) : (
        leftIcon
      )}
      {children}
      {!loading && rightIcon}
    </button>
  )
}
