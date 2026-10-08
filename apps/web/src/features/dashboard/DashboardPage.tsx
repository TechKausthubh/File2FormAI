import { ApiHealthCard } from '@/features/dashboard/ApiHealthCard'

export function DashboardPage() {
  return (
    <section aria-labelledby="dashboard-title">
      <div className="max-w-3xl">
        <p className="text-sm font-semibold text-primary">File2FormAI</p>
        <h1 id="dashboard-title" className="mt-3 text-4xl font-semibold tracking-tight md:text-5xl">
          AI-powered troubleshooting
        </h1>
        <p className="mt-5 text-base leading-7 text-muted-foreground md:text-lg">
          A configurable foundation for evidence-grounded equipment guidance with source citations.
        </p>
      </div>
      <div className="mt-10 max-w-2xl">
        <ApiHealthCard />
      </div>
    </section>
  )
}
