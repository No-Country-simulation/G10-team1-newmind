import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

/**
 * Utility to merge Tailwind classes safely
 * @param {...any} inputs
 * @returns {string}
 */
export function cn(...inputs) {
  return twMerge(clsx(inputs))
}

/**
 * Format a date string to locale format
 * @param {string|Date} date
 * @returns {string}
 */
export function formatDate(date) {
  return new Date(date).toLocaleDateString('es-ES', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

/**
 * Format file size in human readable form
 * @param {number} bytes
 * @returns {string}
 */
export function formatFileSize(bytes) {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`
}

/**
 * Get color class for a profile type
 * @param {string} profile
 * @returns {string}
 */
export function getProfileColor(profile) {
  const map = {
    'Principiante': 'text-emerald-400 bg-emerald-400/10',
    'Junior': 'text-blue-400 bg-blue-400/10',
    'Senior': 'text-violet-400 bg-violet-400/10',
    'Lider': 'text-orange-400 bg-orange-400/10',
    'Gestor': 'text-pink-400 bg-pink-400/10',
  }
  return map[profile] ?? 'text-slate-400 bg-slate-400/10'
}

/**
 * Get color class for a format type
 * @param {string} format
 * @returns {string}
 */
export function getFormatColor(format) {
  const map = {
    'Flashcards': 'text-cyan-400 bg-cyan-400/10',
    'Tutorial': 'text-indigo-400 bg-indigo-400/10',
    'Quiz': 'text-yellow-400 bg-yellow-400/10',
    'Resumen Ejecutivo': 'text-rose-400 bg-rose-400/10',
    'Guion': 'text-teal-400 bg-teal-400/10',
  }
  return map[format] ?? 'text-slate-400 bg-slate-400/10'
}

/**
 * Truncate text to a max length
 * @param {string} text
 * @param {number} maxLength
 * @returns {string}
 */
export function truncate(text, maxLength = 60) {
  if (!text) return ''
  return text.length > maxLength ? `${text.slice(0, maxLength)}…` : text
}

