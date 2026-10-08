import { Construction } from 'lucide-react'

import { Card } from '@/components/ui/card'

interface PendingPageProps {
  title: string
}

export function PendingPage({ title }: PendingPageProps) {
  return (
    <section aria-labelledby="pending-page-title">
      <p className="text-sm font-semibold text-primary">File2FormAI</p>
      <h1 id="pending-page-title" className="mt-3 text-3xl font-semibold tracking-tight">
        {title}
      </h1>
      <Card className="mt-8 flex max-w-2xl items-start gap-4 p-6">
        <div className="grid size-11 shrink-0 place-items-center rounded-xl bg-muted text-muted-foreground">
          <Construction aria-hidden="true" className="size-5" />
        </div>
        <div>
          <h2 className="font-semibold">Functionality pending</h2>
          <p className="mt-2 text-sm leading-6 text-muted-foreground">
            This route is part of the application shell. Its product behavior has not been implemented yet.
          </p>
        </div>
      </Card>
    </section>
  )
}
