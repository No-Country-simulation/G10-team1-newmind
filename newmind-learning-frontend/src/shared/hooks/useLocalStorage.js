import { useState } from 'react'

/**
 * Persist state to localStorage
 * @template T
 * @param {string} key
 * @param {T} initialValue
 * @returns {[T, (value: T) => void]}
 */
export function useLocalStorage(key, initialValue) {
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key)
      return item ? JSON.parse(item) : initialValue
    } catch {
      return initialValue
    }
  })

  const setValue = (value) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value
      setStoredValue(valueToStore)
      window.localStorage.setItem(key, JSON.stringify(valueToStore))
    } catch (error) {
      console.warn(`useLocalStorage: error writing key "${key}"`, error)
    }
  }

  return [storedValue, setValue]
}

