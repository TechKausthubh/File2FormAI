import { Navigate, Route, Routes } from 'react-router-dom'

import { AppShell } from '@/components/layout/AppShell'
import { DashboardPage } from '@/features/dashboard/DashboardPage'
import { PendingPage } from '@/features/placeholders/PendingPage'

export function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route index element={<Navigate replace to="/dashboard" />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="equipment" element={<PendingPage title="Equipment" />} />
        <Route path="documents" element={<PendingPage title="Documents" />} />
        <Route path="users" element={<PendingPage title="Users" />} />
        <Route path="knowledge" element={<PendingPage title="Knowledge" />} />
        <Route path="troubleshooting" element={<PendingPage title="Troubleshooting" />} />
        <Route path="ai-configuration" element={<PendingPage title="AI configuration" />} />
        <Route path="tools" element={<PendingPage title="Tools" />} />
        <Route path="settings" element={<PendingPage title="Settings" />} />
        <Route path="*" element={<Navigate replace to="/dashboard" />} />
      </Route>
    </Routes>
  )
}
