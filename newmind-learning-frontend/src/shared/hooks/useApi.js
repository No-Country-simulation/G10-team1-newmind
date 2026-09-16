import { useState, useCallback } from 'react'

/**
 * Generic hook to call async API functions with loading/error state
 * @template T
 * @param {(...args: any[]) => Promise<T>} apiFn
 * @returns {{ data: T|null, loading: boolean, error: string|null, execute: (...args: any[]) => Promise<T> }}
 */
export function useApi(apiFn) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const execute = useCallback(
    async (...args) => {
      try {
        setLoading(true)
        setError(null)
        const result = await apiFn(...args)
        setData(result)
        return result
      } catch (err) {
        setError(err.message ?? 'Error inesperado')
        throw err
      } finally {
        setLoading(false)
      }
    },
    [apiFn]
  )

  return { data, loading, error, execute }
}

