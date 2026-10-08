import {
  BookOpenText,
  Bot,
  Boxes,
  FileText,
  Gauge,
  Settings,
  SlidersHorizontal,
  Users,
  Wrench,
  type LucideIcon,
} from 'lucide-react'
import { NavLink, Outlet } from 'react-router-dom'

import { cn } from '@/lib/utils'

interface NavigationItem {
  label: string
  path: string
  icon: LucideIcon
}

const navigationItems: NavigationItem[] = [
  { label: 'Dashboard', path: '/dashboard', icon: Gauge },
  { label: 'Equipment', path: '/equipment', icon: Boxes },
  { label: 'Documents', path: '/documents', icon: FileText },
  { label: 'Users', path: '/users', icon: Users },
  { label: 'Knowledge', path: '/knowledge', icon: BookOpenText },
  { label: 'Troubleshooting', path: '/troubleshooting', icon: Wrench },
  { label: 'AI configuration', path: '/ai-configuration', icon: Bot },
  { label: 'Tools', path: '/tools', icon: SlidersHorizontal },
  { label: 'Settings', path: '/settings', icon: Settings },
]

export function AppShell() {
  return (
    <div className="min-h-screen bg-background text-foreground lg:grid lg:grid-cols-[17rem_1fr]">
      <aside className="border-b border-sidebar-border bg-sidebar text-sidebar-foreground lg:min-h-screen lg:border-r lg:border-b-0">
        <div className="flex h-20 items-center gap-3 px-6">
          <div className="grid size-10 place-items-center rounded-xl bg-primary text-sm font-black text-primary-foreground">
            F2
          </div>
          <div>
            <p className="font-semibold tracking-tight">File2FormAI</p>
            <p className="text-xs text-sidebar-muted">Development shell</p>
          </div>
        </div>
        <nav aria-label="Primary navigation" className="flex gap-1 overflow-x-auto px-3 pb-3 lg:block lg:space-y-1 lg:pb-6">
          {navigationItems.map(({ label, path, icon: Icon }) => (
            <NavLink
              key={path}
              to={path}
              className={({ isActive }) =>
                cn(
                  'flex shrink-0 items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-sidebar-accent text-sidebar-accent-foreground'
                    : 'text-sidebar-muted hover:bg-sidebar-accent/60 hover:text-sidebar-foreground',
                )
              }
            >
              <Icon aria-hidden="true" className="size-4" />
              {label}
            </NavLink>
          ))}
        </nav>
      </aside>

      <div className="min-w-0">
        <header className="flex h-20 items-center justify-between border-b border-border bg-card/80 px-5 backdrop-blur md:px-8">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">
              Troubleshooting platform
            </p>
            <p className="mt-1 text-sm text-foreground">Evidence-grounded guidance</p>
          </div>
          <div className="rounded-full border border-border bg-muted px-3 py-1.5 text-xs font-medium text-muted-foreground">
            Local development
          </div>
        </header>
        <main className="mx-auto w-full max-w-7xl p-5 md:p-8 lg:p-10">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
