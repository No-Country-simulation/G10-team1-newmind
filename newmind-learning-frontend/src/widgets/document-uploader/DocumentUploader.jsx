import { useCallback, useState } from 'react'
import { UploadCloud, File, X, CheckCircle, AlertCircle } from 'lucide-react'
import { Spinner } from '@/shared/ui/Spinner'
import { cn, formatFileSize } from '@/shared/utils'

// ── Constants ─────────────────────────────────────────────────────────────────

const ACCEPTED_EXTENSIONS = ['.pdf', '.md', '.txt']
const MAX_SIZE_BYTES       = 20 * 1024 * 1024 // 20 MB

// ── Validation ────────────────────────────────────────────────────────────────

function validateFile(file) {
  const ext = `.${file.name.split('.').pop().toLowerCase()}`
  if (!ACCEPTED_EXTENSIONS.includes(ext)) {
    return `Tipo de archivo no soportado. Aceptado: ${ACCEPTED_EXTENSIONS.join(', ')}`
  }
  if (file.size > MAX_SIZE_BYTES) {
    return 'El archivo supera el límite de 20 MB'
  }
  return null
}

// ── Sub-components ────────────────────────────────────────────────────────────

function DropZoneIcon({ dragging, success, hasError }) {
  if (success)   return <CheckCircle  className="w-10 h-10 text-emerald-400" />
  if (hasError)  return <AlertCircle  className="w-10 h-10 text-red-400" />
  return (
    <UploadCloud className={cn('w-10 h-10', dragging ? 'text-brand-400' : 'text-slate-500')} />
  )
}

function DropZoneLabel({ dragging, success }) {
  if (dragging) return <span>Suelta el archivo aquí</span>
  if (success)  return <span>¡Archivo cargado correctamente!</span>
  return <span>Arrastrá o hacé clic para subir</span>
}

function SelectedFileRow({ file, uploading, onClear }) {
  return (
    <div className="flex items-center gap-3 p-3 bg-slate-800 rounded-lg border border-slate-700">
      <File className="w-5 h-5 text-brand-400 flex-shrink-0" />
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-slate-200 truncate">{file.name}</p>
        <p className="text-xs text-slate-500">{formatFileSize(file.size)}</p>
      </div>
      {uploading ? (
        <Spinner size="sm" />
      ) : (
        <button
          type="button"
          onClick={onClear}
          aria-label="Eliminar archivo seleccionado"
          className="text-slate-500 hover:text-slate-300 transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      )}
    </div>
  )
}

// ── Main component ────────────────────────────────────────────────────────────

/**
 * Drag-and-drop file upload zone.
 * Validates type (.pdf, .md, .txt) and size (≤ 20 MB) locally before calling onFileSelect.
 *
 * @param {Object} props
 * @param {(file: File) => void} props.onFileSelect - Called with the validated File object
 * @param {boolean} [props.uploading]               - Shows spinner; disables input
 * @param {string}  [props.error]                   - External error (from parent/API)
 * @param {boolean} [props.success]                 - Marks the zone as successfully uploaded
 */
export function DocumentUploader({ onFileSelect, uploading = false, error, success = false }) {
  const [dragging, setDragging]         = useState(false)
  const [selectedFile, setSelectedFile] = useState(null)
  const [localError, setLocalError]     = useState(null)

  const displayError = error ?? localError

  const processFile = useCallback(
    (file) => {
      const validationError = validateFile(file)
      if (validationError) {
        setLocalError(validationError)
        setSelectedFile(null)
        return
      }
      setLocalError(null)
      setSelectedFile(file)
      onFileSelect?.(file)
    },
    [onFileSelect]
  )

  const handleDrop = useCallback(
    (e) => {
      e.preventDefault()
      setDragging(false)
      const file = e.dataTransfer.files?.[0]
      if (file) processFile(file)
    },
    [processFile]
  )

  const handleInputChange = (e) => {
    const file = e.target.files?.[0]
    if (file) processFile(file)
  }

  const handleClear = () => {
    setSelectedFile(null)
    setLocalError(null)
  }

  return (
    <div className="space-y-3">
      {/* Drop zone */}
      <label
        htmlFor="doc-upload"
        onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        className={cn(
          'flex flex-col items-center justify-center gap-3',
          'border-2 border-dashed rounded-xl p-10 cursor-pointer',
          'transition-all duration-200',
          dragging      && 'border-brand-400 bg-brand-500/10',
          !dragging && success  && 'border-emerald-500/50 bg-emerald-500/5',
          !dragging && displayError && 'border-red-500/50 bg-red-500/5',
          !dragging && !success && !displayError &&
            'border-slate-700 bg-slate-800/40 hover:border-slate-600 hover:bg-slate-800/60'
        )}
      >
        <input
          id="doc-upload"
          type="file"
          accept={ACCEPTED_EXTENSIONS.join(',')}
          className="sr-only"
          onChange={handleInputChange}
          disabled={uploading}
        />
        <DropZoneIcon dragging={dragging} success={success} hasError={!!displayError} />
        <div className="text-center">
          <p className="text-sm font-medium text-slate-300">
            <DropZoneLabel dragging={dragging} success={success} />
          </p>
          <p className="text-xs text-slate-500 mt-1">PDF, Markdown o TXT · Máx. 20 MB</p>
        </div>
      </label>

      {/* Selected file preview */}
      {selectedFile && (
        <SelectedFileRow
          file={selectedFile}
          uploading={uploading}
          onClear={handleClear}
        />
      )}

      {/* Validation / API error */}
      {displayError && (
        <p role="alert" className="text-xs text-red-400 flex items-center gap-1.5">
          <AlertCircle className="w-3.5 h-3.5 flex-shrink-0" />
          {displayError}
        </p>
      )}
    </div>
  )
}
