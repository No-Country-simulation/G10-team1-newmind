import { cn } from '@/shared/utils'

// ── Shared helper ─────────────────────────────────────────────────────────────

/** Derives a stable HTML id from an optional label string. */
function deriveId(id, label) {
  if (id) return id
  if (label) return label.toLowerCase().replace(/\s+/g, '-')
  return undefined
}

// ── Input ─────────────────────────────────────────────────────────────────────

/**
 * Text input with optional label, icons and validation message.
 *
 * @param {Object} props
 * @param {string} [props.label]
 * @param {string} [props.hint]   - Helper text shown below the field
 * @param {string} [props.error]  - Replaces hint when present; applies error styles
 * @param {React.ReactNode} [props.leftIcon]
 * @param {React.ReactNode} [props.rightIcon]
 * @param {string} [props.id]
 * @param {string} [props.className]
 */
export function Input({
  label,
  hint,
  error,
  leftIcon,
  rightIcon,
  id,
  className,
  ...props
}) {
  const inputId = deriveId(id, label)

  return (
    <div className="w-full">
      {label && (
        <label htmlFor={inputId} className="label">
          {label}
        </label>
      )}

      <div className="relative">
        {leftIcon && (
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none">
            {leftIcon}
          </span>
        )}

        <input
          id={inputId}
          className={cn(
            'input-field',
            leftIcon  && 'pl-9',
            rightIcon && 'pr-9',
            error     && 'border-red-500 focus:ring-red-500',
            className
          )}
          aria-invalid={!!error}
          aria-describedby={error || hint ? `${inputId}-hint` : undefined}
          {...props}
        />

        {rightIcon && (
          <span className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none">
            {rightIcon}
          </span>
        )}
      </div>

      {(error || hint) && (
        <p
          id={`${inputId}-hint`}
          className={cn('mt-1 text-xs', error ? 'text-red-400' : 'text-slate-500')}
        >
          {error ?? hint}
        </p>
      )}
    </div>
  )
}

// ── Select ────────────────────────────────────────────────────────────────────

/**
 * Styled select element with the same label/hint/error API as Input.
 *
 * @param {Object} props
 * @param {string} [props.label]
 * @param {string} [props.hint]
 * @param {string} [props.error]
 * @param {string} [props.id]
 * @param {string} [props.className]
 * @param {React.ReactNode} props.children
 */
export function Select({ label, hint, error, id, className, children, ...props }) {
  const inputId = deriveId(id, label)

  return (
    <div className="w-full">
      {label && (
        <label htmlFor={inputId} className="label">
          {label}
        </label>
      )}

      <select
        id={inputId}
        className={cn(
          'input-field',
          error && 'border-red-500 focus:ring-red-500',
          className
        )}
        aria-invalid={!!error}
        aria-describedby={error || hint ? `${inputId}-hint` : undefined}
        {...props}
      >
        {children}
      </select>

      {(error || hint) && (
        <p
          id={`${inputId}-hint`}
          className={cn('mt-1 text-xs', error ? 'text-red-400' : 'text-slate-500')}
        >
          {error ?? hint}
        </p>
      )}
    </div>
  )
}
