import axios from 'axios'

// ── Client configuration ──────────────────────────────────────────────────────

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 60_000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// ── Interceptors ──────────────────────────────────────────────────────────────

apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('nm_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message =
      error.response?.data?.detail ??
      error.response?.data?.message ??
      error.message ??
      'Error desconocido'
    return Promise.reject(new Error(message))
  }
)

// ── API namespaces ────────────────────────────────────────────────────────────

/**
 * Document endpoints.
 * Upload accepts multipart/form-data; other methods use JSON.
 */
export const documentsApi = {
  /** @param {File} file */
  upload: (file) => {
    const form = new FormData()
    form.append('file', file)
    return apiClient.post('/api/v1/documents', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },

  /** @returns {Promise<import('@/shared/types').Document[]>} */
  list: () => apiClient.get('/api/v1/documents'),

  /** @param {number} id */
  get: (id) => apiClient.get(`/api/v1/documents/${id}`),

  /** @param {number} id */
  delete: (id) => apiClient.delete(`/api/v1/documents/${id}`),
}

/**
 * Adaptation endpoints.
 */
export const adaptationsApi = {
  /** @param {import('@/shared/types').AdaptationRequest} payload */
  create: (payload) => apiClient.post('/api/v1/adaptations', payload),

  /** @param {{ profile?: string, format?: string, status?: string }} [params] */
  list: (params) => apiClient.get('/api/v1/adaptations', { params }),

  /** @param {number} id */
  get: (id) => apiClient.get(`/api/v1/adaptations/${id}`),

  /**
   * Poll for status updates during generation.
   * @param {number} id
   */
  getStatus: (id) => apiClient.get(`/api/v1/adaptations/${id}/status`),
}

/**
 * Health check endpoint.
 */
export const healthApi = {
  check: () => apiClient.get('/health'),
}
