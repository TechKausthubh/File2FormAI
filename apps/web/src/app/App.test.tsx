import { screen } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { App } from '@/app/App'
import { renderApp } from '@/test/render'

describe('application routes', () => {
  beforeEach(() => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ status: 'ok' }),
      }),
    )
  })

  it('redirects the root route to the dashboard', async () => {
    renderApp(<App />, '/')

    expect(await screen.findByRole('heading', { name: 'AI-powered troubleshooting' })).toBeInTheDocument()
  })

  it('renders pending routes without invented data', () => {
    renderApp(<App />, '/equipment')

    expect(screen.getByRole('heading', { name: 'Equipment' })).toBeInTheDocument()
    expect(screen.getByText('Functionality pending')).toBeInTheDocument()
  })
})
