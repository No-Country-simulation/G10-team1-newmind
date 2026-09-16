import { BrowserRouter } from 'react-router-dom'

/**
 * Wraps the app with all global context providers.
 * Add additional providers (Theme, Auth, Query) here as needed.
 */
export function Providers({ children }) {
  return (
    <BrowserRouter>
      {children}
    </BrowserRouter>
  )
}

