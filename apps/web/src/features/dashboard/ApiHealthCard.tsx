import { AlertTriangle, CheckCircle2, LoaderCircle } from 'lucide-react'

import { Card } from '@/components/ui/card'
import { cn } from '@/lib/utils'
import { useApiHealth } from '@/features/dashboard/useApiHealth'

export function ApiHealthCard() {
  const health = useApiHealth()

  const state = health.isPending
    ? {
        label: 'Checking API',
        detail: 'Waiting for the backend health endpoint.',
        icon: LoaderCircle,
        iconClassName: 'animate-spin text-muted-foreground',
      }
    : health.isError
      ? {
          label: 'API unavailable',
          detail: 'The backend could not be reached. Check that the development services are running.',
          icon: AlertTriangle,
          iconClassName: 'text-destructive',
        }
      : {
          label: 'API available',
          detail: 'The backend health endpoint is responding.',
          icon: CheckCircle2,
          iconClassName: 'text-success',
        }

  const Icon = state.icon

  return (
    <Card className="p-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm font-medium text-muted-foreground">API health</p>
          <p className="mt-2 text-xl font-semibold tracking-tight">{state.label}</p>
          <p className="mt-2 max-w-lg text-sm leading-6 text-muted-foreground">{state.detail}</p>
        </div>
        <div className="grid size-11 shrink-0 place-items-center rounded-xl bg-muted">
          <Icon aria-hidden="true" className={cn('size-5', state.iconClassName)} />
        </div>
      </div>
    </Card>
  )
}
