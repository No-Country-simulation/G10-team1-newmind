import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ArrowLeft, UploadCloud, Settings } from 'lucide-react'
import { DocumentUploader } from '@/widgets/document-uploader/DocumentUploader'
import { AdaptationForm } from '@/widgets/adaptation-form/AdaptationForm'
import { documentsApi, adaptationsApi } from '@/shared/api'
import { Card } from '@/shared/ui/Card'
import { Alert } from '@/shared/ui/Alert'
import { cn } from '@/shared/utils'

// ── Step indicator helpers ────────────────────────────────────────────────────

function StepHeader({ number, icon: Icon, title, subtitle, active }) {
  return (
    <div className="flex items-center gap-3 mb-5">
      <div
        className={cn(
          'w-8 h-8 rounded-full border flex items-center justify-center font-bold text-sm transition-all',
          active
            ? 'bg-brand-600/20 border-brand-600/30 text-brand-400'
            : 'bg-slate-800 border-slate-700 text-slate-600'
        )}
      >
        {number}
      </div>
      <div>
        <p className={cn('font-semibold flex items-center gap-2 transition-colors', active ? 'text-slate-200' : 'text-slate-500')}>
          <Icon className="w-4 h-4" />
          {title}
        </p>
        <p className="text-xs text-slate-500">{subtitle}</p>
      </div>
    </div>
  )
}

// ── Custom hook — upload logic ────────────────────────────────────────────────

function useDocumentUpload() {
  const [uploading, setUploading]       = useState(false)
  const [uploadedDoc, setUploadedDoc]   = useState(null)
  const [uploadError, setUploadError]   = useState(null)

  const handleFileSelect = async (file) => {
    setUploadError(null)
    setUploading(true)
    try {
      const document = await documentsApi.upload(file)
      setUploadedDoc(document)
    } catch (err) {
      setUploadedDoc(null)
      setUploadError(err.message ?? 'Error al subir el archivo. Intentá de nuevo.')
    } finally {
      setUploading(false)
    }
  }

  return { uploading, uploadedDoc, uploadError, handleFileSelect }
}

// ── Page ──────────────────────────────────────────────────────────────────────

export function NewAdaptationPage() {
  const navigate = useNavigate()
  const { uploading, uploadedDoc, uploadError, handleFileSelect } = useDocumentUpload()

  const [generating, setGenerating] = useState(false)
  const [globalError, setGlobalError] = useState(null)

  const handleGenerate = async (formValues) => {
    if (!uploadedDoc) {
      setGlobalError('Primero cargá un documento.')
      return
    }
    setGlobalError(null)
    setGenerating(true)
    try {
      const adaptation = await adaptationsApi.create({
        documentId: uploadedDoc.id,
        ...formValues,
      })
      navigate(`/result/${adaptation.id}`, { state: { adaptation } })
    } catch (err) {
      setGlobalError(err.message ?? 'Error al iniciar la generación.')
    } finally {
      setGenerating(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto space-y-8 animate-fade-in">
      {/* Back */}
      <Link to="/" className="btn-ghost text-sm inline-flex items-center gap-1.5">
        <ArrowLeft className="w-4 h-4" />
        Volver al dashboard
      </Link>

      {/* Title */}
      <div>
        <h1 className="page-title">Nueva Adaptación</h1>
        <p className="text-slate-400 mt-1">
          Cargá tu documento y configurá los parámetros de adaptación educativa.
        </p>
      </div>

      {globalError && <Alert variant="error">{globalError}</Alert>}

      {/* Step 1 — Upload */}
      <Card>
        <StepHeader
          number={1}
          icon={UploadCloud}
          title="Cargar documento"
          subtitle="PDF, Markdown o TXT · máx. 20 MB"
          active
        />
        <DocumentUploader
          onFileSelect={handleFileSelect}
          uploading={uploading}
          error={uploadError}
          success={!!uploadedDoc}
        />
        {uploadedDoc && !uploading && (
          <p className="text-sm text-emerald-400 mt-3 flex items-center gap-1.5">
            ✅ <span className="font-medium">{uploadedDoc.title}</span> listo para procesar
          </p>
        )}
      </Card>

      {/* Step 2 — Form */}
      <Card>
        <StepHeader
          number={2}
          icon={Settings}
          title="Configurar adaptación"
          subtitle="Perfil, formato, nicho y nivel de detalle"
          active={!!uploadedDoc}
        />
        {uploadedDoc ? (
          <AdaptationForm onSubmit={handleGenerate} loading={generating} />
        ) : (
          <p className="text-sm text-slate-500 text-center py-6">
            Primero cargá un documento para habilitar este paso.
          </p>
        )}
      </Card>
    </div>
  )
}
