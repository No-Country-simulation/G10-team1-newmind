import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'
import postcss from 'postcss'
import tailwindcss from 'tailwindcss'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { adaptFlashcardsResponse } from './adaptFlashcardsResponse'
import { ContentViewer } from './ContentViewer'

const canonicalCards = [
  {
    frente: '¿Qué es una VCN?',
    dorso: 'Una red virtual privada en OCI.',
    pista_didactica: 'Imagine una red privada.',
  },
  {
    frente: '¿Qué contiene una VCN?',
    dorso: 'Subredes y reglas de seguridad.',
    pista_didactica: 'Piense en barrios conectados.',
  },
]

function buildAdaptation(items = canonicalCards) {
  const contenidoAdaptado = {
    titulo: 'Redes en OCI',
    introduccion_contextualizada: 'Aprenda los conceptos esenciales.',
  }
  if (items !== null) contenidoAdaptado.items = items

  return {
    id: 18,
    documentTitle: 'Guía de OCI',
    profile: 'Principiante',
    format: 'Flashcards',
    industry: 'General',
    detailLevel: 'Didactico',
    status: 'completed',
    content: contenidoAdaptado,
    evaluation: { approved: true, score: 0.92 },
    officialResponse: {
      status: 'exito',
      metadatos: {
        perfil_aplicado: 'Principiante',
        formato_generado: 'Flashcards',
        tiempo_estimado_estudio_minutos: 8,
        conceptos_clave: ['VCN', 'Subredes'],
      },
      contenido_adaptado: contenidoAdaptado,
      evaluacion_calidad: {
        anclaje_fuente_score: 0.92,
        claridad_pedagogica: 'Alta',
        observaciones: 'Contenido trazable.',
      },
      almacenamiento_oci: {
        bucket: 'learning-content',
        objeto_id: 'flashcards.json',
        status_upload: 'completado',
      },
    },
  }
}

describe('Flashcards adaptation contract', () => {
  it('adapts the canonical official response into one ready view model', () => {
    expect(adaptFlashcardsResponse(buildAdaptation())).toEqual({
      status: 'ready',
      viewModel: {
        title: 'Redes en OCI',
        introduction: 'Aprenda los conceptos esenciales.',
        profile: 'Principiante',
        studyTime: 8,
        keyConcepts: ['VCN', 'Subredes'],
        qualityScore: 0.92,
        remarks: 'Contenido trazable.',
        bucket: 'learning-content',
        objectId: 'flashcards.json',
        items: canonicalCards,
      },
    })
  })

  it.each([
    ['missing items', null],
    ['non-array items', { frente: 'Pregunta' }],
    ['malformed card', [{ front: 'Question', back: 'Answer', didactic_hint: 'Hint' }]],
  ])('renders invalid-contract feedback for %s', (_case, items) => {
    render(<ContentViewer adaptation={buildAdaptation(items)} />)

    expect(screen.getByRole('alert')).toHaveTextContent(
      'La respuesta recibida no cumple el contrato de flashcards.'
    )
    expect(screen.queryByText('No hay flashcards para mostrar.')).not.toBeInTheDocument()
  })

  it('renders a true empty result separately from an invalid contract', () => {
    render(<ContentViewer adaptation={buildAdaptation([])} />)

    expect(screen.getByRole('status')).toHaveTextContent('No hay flashcards para mostrar.')
    expect(screen.queryByRole('alert')).not.toBeInTheDocument()
  })

  it('renders canonical cards when the completed adaptation content is null', async () => {
    const user = userEvent.setup()
    const adaptation = buildAdaptation()
    adaptation.content = null

    render(<ContentViewer adaptation={adaptation} />)

    expect(screen.getByRole('heading', { name: 'Redes en OCI' })).toBeInTheDocument()
    expect(screen.getByText('¿Qué es una VCN?')).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'Mostrar respuesta de la tarjeta 1' }))
    expect(screen.getByText('Una red virtual privada en OCI.')).toBeInTheDocument()
    expect(screen.queryByRole('alert')).not.toBeInTheDocument()
  })

  it.each([
    ['missing items', null],
    ['malformed cards', [{ front: 'Question', back: 'Answer' }]],
  ])('shows invalid-contract feedback for %s with null adaptation content', (_case, items) => {
    const adaptation = buildAdaptation(items)
    adaptation.content = null

    render(<ContentViewer adaptation={adaptation} />)

    expect(screen.getByRole('alert')).toHaveTextContent(
      'La respuesta recibida no cumple el contrato de flashcards.'
    )
    expect(screen.queryByText('No hay flashcards para mostrar.')).not.toBeInTheDocument()
  })

  it('renders metadata and supports card controls by pointer and keyboard', async () => {
    const user = userEvent.setup()
    render(<ContentViewer adaptation={buildAdaptation()} />)

    expect(screen.getByRole('heading', { name: 'Redes en OCI' })).toBeInTheDocument()
    expect(screen.getByText('Aprenda los conceptos esenciales.')).toBeInTheDocument()
    expect(screen.getByText('VCN')).toBeInTheDocument()
    expect(screen.getByText('¿Qué es una VCN?')).toBeInTheDocument()

    const hintButton = screen.getByRole('button', { name: 'Ver pista didáctica' })
    await user.click(hintButton)
    expect(screen.getByText('Imagine una red privada.')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Mostrar respuesta de la tarjeta 1' })).toHaveAttribute('aria-pressed', 'false')
    hintButton.focus()
    await user.keyboard(' ')
    expect(screen.queryByText('Imagine una red privada.')).not.toBeInTheDocument()

    const flipButton = screen.getByRole('button', {
      name: 'Mostrar respuesta de la tarjeta 1',
    })
    flipButton.focus()
    await user.keyboard('{Enter}')
    expect(screen.getByText('Una red virtual privada en OCI.')).toBeInTheDocument()
    expect(flipButton).toHaveAttribute('aria-pressed', 'true')
    expect(flipButton).toHaveFocus()
    expect(screen.queryByRole('button', { name: 'Ver pista didáctica' })).not.toBeInTheDocument()
    flipButton.focus()
    await user.keyboard(' ')
    expect(flipButton).toHaveAttribute('aria-pressed', 'false')
    await user.keyboard('{Enter}')

    await user.click(screen.getByRole('button', { name: 'Siguiente' }))
    expect(screen.getByText('¿Qué contiene una VCN?')).toBeInTheDocument()
    expect(screen.getByText('2 / 2')).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'Ver pista didáctica' }))
    expect(screen.getByText('Piense en barrios conectados.')).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'Mostrar respuesta de la tarjeta 2' }))
    expect(screen.getByText('Subredes y reglas de seguridad.')).toBeInTheDocument()

    const previousButton = screen.getByRole('button', { name: 'Anterior' })
    previousButton.focus()
    await user.keyboard('{Enter}')
    expect(screen.getByText('¿Qué es una VCN?')).toBeInTheDocument()
  })

  it('flips by clicking non-control areas of both faces without flipping on hint', async () => {
    const user = userEvent.setup()
    render(<ContentViewer adaptation={buildAdaptation()} />)

    const question = screen.getByRole('heading', { name: '¿Qué es una VCN?' })
    await user.click(question)
    const flipButton = screen.getByRole('button', { name: 'Volver a la pregunta de la tarjeta 1' })
    expect(flipButton).toHaveAttribute('aria-pressed', 'true')
    expect(question.closest('[aria-hidden]')).toHaveAttribute('aria-hidden', 'true')

    await user.click(screen.getByText('Una red virtual privada en OCI.'))
    expect(flipButton).toHaveAttribute('aria-pressed', 'false')
    expect(screen.getByRole('heading', { name: '¿Qué es una VCN?' })).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'Ver pista didáctica' }))
    expect(screen.getByText('Imagine una red privada.')).toBeInTheDocument()
    expect(flipButton).toHaveAttribute('aria-pressed', 'false')
  })

  it('emits a 3D transform transition only when motion is preferred', async () => {
    const flashcardCss = readFileSync(resolve('src/app/styles/globals.css'), 'utf8')
    const css = (await postcss([tailwindcss()]).process(flashcardCss, { from: undefined })).css
    expect(css).toMatch(/\.perspective-1000\s*\{\s*perspective:\s*1000px/)
    expect(css).toMatch(/\.transform-style-3d\s*\{\s*transform-style:\s*preserve-3d/)
    expect(css).toMatch(/\.backface-hidden\s*\{\s*backface-visibility:\s*hidden/)
    expect(css).toMatch(/\.rotate-y-180\s*\{\s*transform:\s*rotateY\(180deg\)/)
    expect(css).toMatch(/@media\s*\(prefers-reduced-motion:\s*no-preference\)[\s\S]*?\.flashcard-flip\s*\{\s*transition:\s*transform 500ms/)

    const { container } = render(<ContentViewer adaptation={buildAdaptation()} />)
    const flipButton = screen.getByRole('button', { name: 'Mostrar respuesta de la tarjeta 1' })
    expect(flipButton).toHaveClass('flashcard-flip-control')
    expect(container.querySelector('.flashcard-flip.transform-style-3d')).toBeInTheDocument()
    await userEvent.setup().click(flipButton)
    expect(container.querySelector('.flashcard-flip.rotate-y-180')).toBeInTheDocument()
  })

  it('preserves non-Flashcards rendering', () => {
    const adaptation = buildAdaptation()
    adaptation.format = 'Resumen Ejecutivo'
    adaptation.content = { summary: 'Resumen conservado.' }

    render(<ContentViewer adaptation={adaptation} />)

    expect(screen.getByText('Resumen conservado.')).toBeInTheDocument()
  })
})
