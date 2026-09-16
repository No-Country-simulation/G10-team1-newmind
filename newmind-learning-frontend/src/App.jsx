import { Sidebar } from '@/shared/ui/Sidebar'
import { AppRouter } from '@/app/router'

/**
 * Root application component.
 * Composes the persistent sidebar with the main content area.
 * All routing is delegated to AppRouter.
 */
export function App() {
  return (
    <div className="flex min-h-screen bg-slate-950">
      <Sidebar />

      <main className="flex-1 ml-64 min-h-screen">
        <div className="max-w-7xl mx-auto px-6 py-8">
          <AppRouter />
        </div>
      </main>
    </div>
  )
}
