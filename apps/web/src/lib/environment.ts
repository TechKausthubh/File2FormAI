import { z } from 'zod'

const clientEnvironmentSchema = z.object({
  VITE_API_BASE_URL: z.url().default('http://localhost:8000'),
})

export const clientEnvironment = clientEnvironmentSchema.parse(import.meta.env)
