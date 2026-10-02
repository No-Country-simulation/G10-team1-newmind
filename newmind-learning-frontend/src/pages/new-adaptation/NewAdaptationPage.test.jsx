import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes, useLocation, useParams } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { adaptationsApi, documentsApi } from '@/shared/api'
import { NewAdaptationPage } from './NewAdaptationPage'

const uploadedDocument = {
  id: 17,
  title: 'Testing React applications',
  type: 'txt',
  size: 12,
  createdAt: '2026-09-25T00:00:00Z',
}

function ResultProbe() {
  const { id } = useParams()
  const location = useLocation()

  return (
    <div>
      <span>Result route: {id}</span>
      <span>Adaptation state: {location.state?.adaptation?.id}</span>
    </div>
  )
}

function renderPage() {
  render(
    <MemoryRouter initialEntries={['/new']}>
      <Routes>
        <Route path="/new" element={<NewAdaptationPage />} />
        <Route path="/result/:id" element={<ResultProbe />} />
      </Routes>
    </MemoryRouter>
  )
}

async function uploadDocument(user) {
  const file = new File(['test content'], 'source.txt', { type: 'text/plain' })
  await user.upload(screen.getByLabelText(/Arrastrá o hacé clic para subir/i), file)
  await screen.findByText(uploadedDocument.title)
}

async function completeAdaptationForm(user) {
  await user.click(screen.getByRole('button', { name: /Líder Técnico/i }))
  await user.click(screen.getByRole('button', { name: 'Siguiente' }))
  await user.click(screen.getByRole('button', { name: /Resumen Ejecutivo/i }))
  await user.click(screen.getByRole('button', { name: 'Siguiente' }))
  await user.click(screen.getByRole('button', { name: 'Fintech' }))
  await user.click(screen.getByRole('button', { name: 'Siguiente' }))
  await user.click(screen.getByRole('button', { name: /Detallado/i }))
}

describe('NewAdaptationPage', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
    vi.spyOn(documentsApi, 'upload').mockResolvedValue(uploadedDocument)
  })

  it('creates an adaptation with the accepted payload and navigates to its result route', async () => {
    const user = userEvent.setup()
    const adaptation = { id: 42, status: 'pending' }
    const createSpy = vi.spyOn(adaptationsApi, 'create').mockResolvedValue(adaptation)
    renderPage()

    await uploadDocument(user)
    await completeAdaptationForm(user)
    await user.click(screen.getByRole('button', { name: 'Generar contenido' }))

    expect(createSpy).toHaveBeenCalledWith({
      documentId: 17,
      profile: 'Lider',
      format: 'Resumen Ejecutivo',
      industry: 'Fintech',
      detailLevel: 'Detallado',
    })
    expect(await screen.findByText('Result route: 42')).toBeInTheDocument()
    expect(screen.getByText('Adaptation state: 42')).toBeInTheDocument()
  })

  it('gives the user an actionable next step when creation fails', async () => {
    const user = userEvent.setup()
    vi.spyOn(adaptationsApi, 'create').mockRejectedValue(
      new Error('Request failed with status code 503')
    )
    renderPage()

    await uploadDocument(user)
    await completeAdaptationForm(user)
    await user.click(screen.getByRole('button', { name: 'Generar contenido' }))

    expect(await screen.findByRole('alert')).toHaveTextContent(
      /Revisá tu conexión e intentá de nuevo/i
    )
  })
})
