import { z } from 'zod'

import { clientEnvironment } from '@/lib/environment'

const healthResponseSchema = z.object({
  status: z.literal('ok'),
})

export type HealthResponse = z.infer<typeof healthResponseSchema>

export async function getApiHealth(signal?: AbortSignal): Promise<HealthResponse> {
  const response = await fetch(`${clientEnvironment.VITE_API_BASE_URL}/health`, {
    headers: { Accept: 'application/json' },
    signal,
  })

  if (!response.ok) {
    throw new Error('API health request failed')
  }

  return healthResponseSchema.parse(await response.json())
}
