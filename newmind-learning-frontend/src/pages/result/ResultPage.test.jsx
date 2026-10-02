import { act, fireEvent, render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { adaptationsApi } from '@/shared/api'
import { ResultPage } from './ResultPage'
import { ADAPTATION_POLL_POLICY } from './adaptationPolling'

vi.mock('@/widgets/generation-status/GenerationStatus', () => ({
  GenerationStatus: ({ status }) => <div>Estado del proceso: {status}</div>,
}))

vi.mock('@/widgets/content-viewer/ContentViewer', () => ({
  ContentViewer: ({ adaptation }) => (
    <div>Contenido completo: {adaptation.content?.marker}</div>
  ),
}))

const pendingAdaptation = {
  id: 42,
  documentTitle: 'Guía de pruebas',
  profile: 'Lider',
  format: 'Resumen Ejecutivo',
  industry: 'Fintech',
  detailLevel: 'Detallado',
  status: 'pending',
}

function deferred() {
  let resolve
  let reject
  const promise = new Promise((resolvePromise, rejectPromise) => {
    resolve = resolvePromise
    reject = rejectPromise
  })

  return { promise, resolve, reject }
}

function renderPage(adaptation = pendingAdaptation) {
  return render(
    <MemoryRouter
      initialEntries={[{ pathname: '/result/42', state: { adaptation } }]}
    >
      <Routes>
        <Route path="/result/:id" element={<ResultPage />} />
      </Routes>
    </MemoryRouter>
  )
}

async function advancePolling(milliseconds = ADAPTATION_POLL_POLICY.intervalMs) {
  await act(async () => {
    await vi.advanceTimersByTimeAsync(milliseconds)
  })
}

describe('ResultPage polling lifecycle', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    vi.restoreAllMocks()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('polls pending and processing states sequentially and loads the completed result', async () => {
    vi.spyOn(adaptationsApi, 'getStatus')
      .mockResolvedValueOnce({ id: 42, status: 'processing' })
      .mockResolvedValueOnce({ id: 42, status: 'completed' })
    const getSpy = vi.spyOn(adaptationsApi, 'get').mockResolvedValue({
      ...pendingAdaptation,
      status: 'completed',
      content: { marker: 'resultado final' },
    })
    renderPage()

    await advancePolling()
    expect(screen.getByText('Estado del proceso: processing')).toBeInTheDocument()

    await advancePolling()
    expect(screen.getByText('Contenido completo: resultado final')).toBeInTheDocument()
    expect(getSpy).toHaveBeenCalledWith('42')
  })

  it('loads the full failed result and exposes an actionable exit', async () => {
    vi.spyOn(adaptationsApi, 'getStatus').mockResolvedValue({ id: 42, status: 'failed' })
    const getSpy = vi.spyOn(adaptationsApi, 'get').mockResolvedValue({
      ...pendingAdaptation,
      status: 'failed',
      error: 'El generador no pudo completar la adaptación.',
    })
    renderPage()

    await advancePolling()

    expect(getSpy).toHaveBeenCalledWith('42')
    expect(screen.getByRole('alert')).toHaveTextContent(
      'El generador no pudo completar la adaptación.'
    )
    expect(screen.getByRole('link', { name: /Intentar nuevamente/i })).toHaveAttribute(
      'href',
      '/new'
    )
  })

  it('offers retry and navigation recovery after an HTTP polling failure', async () => {
    const getStatusSpy = vi.spyOn(adaptationsApi, 'getStatus')
      .mockRejectedValueOnce(new Error('Request failed with status code 503'))
      .mockResolvedValueOnce({ id: 42, status: 'processing' })
    renderPage()

    await advancePolling()

    const alert = screen.getByRole('alert')
    expect(alert).toHaveTextContent('Request failed with status code 503')
    expect(screen.getByRole('button', { name: /Reintentar consulta/i })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /Ver historial/i })).toHaveAttribute(
      'href',
      '/history'
    )

    fireEvent.click(screen.getByRole('button', { name: /Reintentar consulta/i }))
    await advancePolling(0)
    expect(getStatusSpy).toHaveBeenCalledTimes(2)
  })

  it('stops after the polling attempt limit and exposes recovery actions', async () => {
    const getStatusSpy = vi.spyOn(adaptationsApi, 'getStatus').mockResolvedValue({
      id: 42,
      status: 'processing',
    })
    renderPage()

    await advancePolling(
      ADAPTATION_POLL_POLICY.intervalMs * ADAPTATION_POLL_POLICY.maxAttempts
    )

    expect(getStatusSpy).toHaveBeenCalledTimes(ADAPTATION_POLL_POLICY.maxAttempts)
    expect(screen.getByRole('alert')).toHaveTextContent(/tiempo de espera/i)
    expect(screen.getByRole('button', { name: /Reintentar consulta/i })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /Ver historial/i })).toBeInTheDocument()

    await advancePolling(ADAPTATION_POLL_POLICY.intervalMs * 2)
    expect(getStatusSpy).toHaveBeenCalledTimes(ADAPTATION_POLL_POLICY.maxAttempts)
  })

  it('never starts another status request while the current request is pending', async () => {
    const firstRequest = deferred()
    const getStatusSpy = vi.spyOn(adaptationsApi, 'getStatus')
      .mockReturnValueOnce(firstRequest.promise)
      .mockResolvedValueOnce({ id: 42, status: 'processing' })
    renderPage()

    await advancePolling(ADAPTATION_POLL_POLICY.intervalMs * 10)
    expect(getStatusSpy).toHaveBeenCalledTimes(1)

    await act(async () => {
      firstRequest.resolve({ id: 42, status: 'processing' })
      await firstRequest.promise
    })
    await advancePolling()
    expect(getStatusSpy).toHaveBeenCalledTimes(2)
  })

  it('aborts the active status request on unmount and never reschedules it', async () => {
    const activeRequest = deferred()
    const getStatusSpy = vi.spyOn(adaptationsApi, 'getStatus').mockReturnValue(
      activeRequest.promise
    )
    const getSpy = vi.spyOn(adaptationsApi, 'get')
    const view = renderPage()

    await advancePolling()
    const requestConfig = getStatusSpy.mock.calls[0][1]
    expect(requestConfig.signal.aborted).toBe(false)

    view.unmount()
    expect(requestConfig.signal.aborted).toBe(true)

    await act(async () => {
      activeRequest.resolve({ id: 42, status: 'completed' })
      await activeRequest.promise
    })
    await advancePolling(ADAPTATION_POLL_POLICY.intervalMs * 2)

    expect(getStatusSpy).toHaveBeenCalledTimes(1)
    expect(getSpy).not.toHaveBeenCalled()
  })
})
