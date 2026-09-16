import { useState } from 'react'
import { ChevronRight, User, FileText, Building2, Layers } from 'lucide-react'
import { Button } from '@/shared/ui/Button'
import { cn } from '@/shared/utils'
import { PROFILES, FORMATS, INDUSTRIES, DETAIL_LEVELS } from '@/shared/types'

// ── Constants ─────────────────────────────────────────────────────────────────

const STEPS = [
  { id: 'profile',  label: 'Perfil',   icon: User      },
  { id: 'format',   label: 'Formato',  icon: FileText   },
  { id: 'industry', label: 'Nicho',    icon: Building2  },
  { id: 'detail',   label: 'Detalle',  icon: Layers     },
]

const STEP_IDS = STEPS.map((s) => s.id)

const INITIAL_VALUES = {
  profile:     '',
  format:      '',
  industry:    'General',
  detailLevel: 'Didactico',
}

// ── Sub-components ────────────────────────────────────────────────────────────

function StepIndicator({ currentStep }) {
  const currentIndex = STEP_IDS.indexOf(currentStep)
  return (
    <div className="flex items-center gap-2 mb-6">
      {STEPS.map((step, i) => {
        const Icon     = step.icon
        const isActive = step.id === currentStep
        const isDone   = i < currentIndex
        return (
          <div key={step.id} className="flex items-center gap-2">
            <div
              className={cn(
                'flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all',
                isActive && 'bg-brand-600 text-white',
                isDone   && 'bg-emerald-600/20 text-emerald-400',
                !isActive && !isDone && 'bg-slate-800 text-slate-500'
              )}
            >
              <Icon className="w-3.5 h-3.5" />
              {step.label}
            </div>
            {i < STEPS.length - 1 && (
              <ChevronRight className="w-3 h-3 text-slate-600" />
            )}
          </div>
        )
      })}
    </div>
  )
}

/**
 * Reusable grid of selectable option cards.
 *
 * @param {{ options: Array, value: string, onChange: (v: string) => void, renderOption: (opt) => React.ReactNode }} props
 */
function OptionGrid({ options, value, onChange, renderOption }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
      {options.map((opt) => (
        <button
          key={opt.value}
          type="button"
          onClick={() => onChange(opt.value)}
          aria-pressed={value === opt.value}
          className={cn(
            'text-left p-4 rounded-xl border transition-all duration-200',
            value === opt.value
              ? 'border-brand-500/60 bg-brand-600/10 ring-1 ring-brand-500/40'
              : 'border-slate-700/50 bg-slate-800/60 hover:border-slate-600 hover:bg-slate-800'
          )}
        >
          {renderOption(opt)}
        </button>
      ))}
    </div>
  )
}

// ── Step content ──────────────────────────────────────────────────────────────

function ProfileStep({ value, onChange }) {
  return (
    <div className="animate-fade-in">
      <p className="text-sm text-slate-400 mb-4">¿Quién va a recibir este contenido?</p>
      <OptionGrid
        options={PROFILES}
        value={value}
        onChange={onChange}
        renderOption={(opt) => (
          <>
            <p className="font-medium text-slate-200 text-sm">{opt.label}</p>
            <p className="text-xs text-slate-500 mt-1">{opt.description}</p>
          </>
        )}
      />
    </div>
  )
}

function FormatStep({ value, onChange }) {
  return (
    <div className="animate-fade-in">
      <p className="text-sm text-slate-400 mb-4">¿Qué formato de contenido querés generar?</p>
      <OptionGrid
        options={FORMATS}
        value={value}
        onChange={onChange}
        renderOption={(opt) => (
          <div className="flex items-start gap-3">
            <span className="text-2xl" aria-hidden="true">{opt.icon}</span>
            <div>
              <p className="font-medium text-slate-200 text-sm">{opt.label}</p>
              <p className="text-xs text-slate-500 mt-0.5">{opt.description}</p>
            </div>
          </div>
        )}
      />
    </div>
  )
}

function IndustryStep({ value, onChange }) {
  return (
    <div className="animate-fade-in">
      <p className="text-sm text-slate-400 mb-4">¿Cuál es el nicho del contenido?</p>
      <div className="grid grid-cols-2 gap-3">
        {INDUSTRIES.map((opt) => (
          <button
            key={opt.value}
            type="button"
            onClick={() => onChange(opt.value)}
            aria-pressed={value === opt.value}
            className={cn(
              'p-4 rounded-xl border text-center font-medium text-sm transition-all duration-200',
              value === opt.value
                ? 'border-brand-500/60 bg-brand-600/10 text-brand-300 ring-1 ring-brand-500/40'
                : 'border-slate-700/50 bg-slate-800/60 text-slate-300 hover:border-slate-600'
            )}
          >
            {opt.label}
          </button>
        ))}
      </div>
    </div>
  )
}

function DetailStep({ value, onChange }) {
  return (
    <div className="animate-fade-in">
      <p className="text-sm text-slate-400 mb-4">¿Qué nivel de detalle necesitás?</p>
      <div className="space-y-2">
        {DETAIL_LEVELS.map((opt) => (
          <button
            key={opt.value}
            type="button"
            onClick={() => onChange(opt.value)}
            aria-pressed={value === opt.value}
            className={cn(
              'w-full flex items-center gap-4 p-4 rounded-xl border text-left transition-all duration-200',
              value === opt.value
                ? 'border-brand-500/60 bg-brand-600/10 ring-1 ring-brand-500/40'
                : 'border-slate-700/50 bg-slate-800/60 hover:border-slate-600'
            )}
          >
            <div
              className={cn(
                'w-4 h-4 rounded-full border-2 flex-shrink-0 transition-all',
                value === opt.value ? 'border-brand-500 bg-brand-500' : 'border-slate-600'
              )}
            />
            <div>
              <p className="font-medium text-slate-200 text-sm">{opt.label}</p>
              <p className="text-xs text-slate-500">{opt.description}</p>
            </div>
          </button>
        ))}
      </div>
    </div>
  )
}

// ── Validation ────────────────────────────────────────────────────────────────

const canAdvance = {
  profile:  (v) => !!v.profile,
  format:   (v) => !!v.format,
  industry: (v) => !!v.industry,
  detail:   (v) => !!v.detailLevel,
}

// ── Main component ────────────────────────────────────────────────────────────

/**
 * Multi-step form to configure an adaptation request.
 *
 * @param {Object} props
 * @param {(values: Object) => void} props.onSubmit
 * @param {boolean} [props.loading=false]
 */
export function AdaptationForm({ onSubmit, loading = false }) {
  const [stepId, setStepId]   = useState(STEP_IDS[0])
  const [values, setValues]   = useState(INITIAL_VALUES)

  const set = (key) => (val) => setValues((prev) => ({ ...prev, [key]: val }))

  const currentIndex = STEP_IDS.indexOf(stepId)
  const isLastStep   = currentIndex === STEP_IDS.length - 1
  const isFirstStep  = currentIndex === 0

  const handleNext = () => {
    if (isLastStep) {
      onSubmit?.(values)
    } else {
      setStepId(STEP_IDS[currentIndex + 1])
    }
  }

  const handleBack = () => {
    if (!isFirstStep) setStepId(STEP_IDS[currentIndex - 1])
  }

  return (
    <div>
      <StepIndicator currentStep={stepId} />

      {stepId === 'profile'  && <ProfileStep  value={values.profile}     onChange={set('profile')}     />}
      {stepId === 'format'   && <FormatStep   value={values.format}      onChange={set('format')}      />}
      {stepId === 'industry' && <IndustryStep value={values.industry}    onChange={set('industry')}    />}
      {stepId === 'detail'   && <DetailStep   value={values.detailLevel} onChange={set('detailLevel')} />}

      {/* Navigation */}
      <div className="flex items-center justify-between mt-6 pt-4 border-t border-slate-800">
        <Button variant="ghost" onClick={handleBack} disabled={isFirstStep}>
          Atrás
        </Button>
        <Button
          variant="primary"
          onClick={handleNext}
          disabled={!canAdvance[stepId]?.(values)}
          loading={isLastStep && loading}
          rightIcon={!isLastStep ? <ChevronRight className="w-4 h-4" /> : undefined}
        >
          {isLastStep ? 'Generar contenido' : 'Siguiente'}
        </Button>
      </div>
    </div>
  )
}
