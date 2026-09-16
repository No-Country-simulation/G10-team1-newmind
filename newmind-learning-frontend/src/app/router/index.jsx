import { Routes, Route, Navigate } from 'react-router-dom'
import { DashboardPage } from '@/pages/dashboard/DashboardPage'
import { NewAdaptationPage } from '@/pages/new-adaptation/NewAdaptationPage'
import { ResultPage } from '@/pages/result/ResultPage'
import { HistoryPage } from '@/pages/history/HistoryPage'

export function AppRouter() {
  return (
    <Routes>
      <Route path="/" element={<DashboardPage />} />
      <Route path="/new" element={<NewAdaptationPage />} />
      <Route path="/result/:id" element={<ResultPage />} />
      <Route path="/history" element={<HistoryPage />} />
      {/* Catch-all */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

