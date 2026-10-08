import { screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { ApiHealthCard } from '@/features/dashboard/ApiHealthCard'
import { renderApp } from '@/test/render'

describe('API health card', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('shows a loading state while the health request is pending', () => {
    vi.stubGlobal('fetch', vi.fn(() => new Promise(() => undefined)))

    renderApp(<ApiHealthCard />)

    expect(screen.getByText('Checking API')).toBeInTheDocument()
  })

  it('shows an available state for a healthy API', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ status: 'ok' }),
      }),
    )

    renderApp(<ApiHealthCard />)

    expect(await screen.findByText('API available')).toBeInTheDocument()
  })

  it('shows an unavailable state when the API cannot be reached', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('connection refused')))

    renderApp(<ApiHealthCard />)

    expect(await screen.findByText('API unavailable')).toBeInTheDocument()
  })
})
