import { useQuery } from '@tanstack/react-query'

import { getApiHealth } from '@/lib/api'

export const apiHealthQueryKey = ['platform', 'api-health'] as const

export function useApiHealth() {
  return useQuery({
    queryKey: apiHealthQueryKey,
    queryFn: ({ signal }) => getApiHealth(signal),
    retry: false,
    refetchInterval: 30_000,
  })
}
