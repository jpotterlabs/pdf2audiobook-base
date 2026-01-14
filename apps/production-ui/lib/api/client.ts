// API client for base pipeline

const rawUrl = process.env.NEXT_PUBLIC_API_URL
const defaultUrl = "http://localhost:8000"

let finalUrl = rawUrl || defaultUrl

const API_BASE_URL = finalUrl

interface ApiError {
  detail?: string | Array<{ msg: string }>
  message?: string
}

export class APIError extends Error {
  constructor(
    message: string,
    public status?: number,
    public details?: unknown,
  ) {
    super(message)
    this.name = "APIError"
  }
}

async function fetchWithAuth(endpoint: string, options: RequestInit = {}, token?: string): Promise<Response> {
  const headers: HeadersInit = {
    ...options.headers,
  }

  if (token) {
    headers["Authorization"] = `Bearer ${token}`
  }

  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json"
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
    cache: "no-store",
  })

  if (!response.ok) {
    const errorData = (await response.json().catch(() => ({}))) as ApiError
    const message =
      typeof errorData.detail === "string"
        ? errorData.detail
        : errorData.message || `Request failed with status ${response.status}`

    throw new APIError(message, response.status, errorData)
  }

  return response
}

export const api = {
  // Auth endpoints (Simplified)
  auth: {
    getMe: async (token?: string) => {
      const response = await fetchWithAuth("/api/v1/auth/me", { method: "GET" }, token || "base-token")
      return response.json()
    },
  },

  // Job endpoints
  jobs: {
    create: async (jobData: FormData, token?: string) => {
      const response = await fetchWithAuth(
        "/api/v1/jobs/",
        {
          method: "POST",
          body: jobData,
        },
        token || "base-token",
      )
      return response.json()
    },

    list: async (skip = 0, limit = 50, token?: string) => {
      const response = await fetchWithAuth(`/api/v1/jobs/?skip=${skip}&limit=${limit}`, { method: "GET" }, token || "base-token")
      return response.json()
    },

    get: async (jobId: number, token?: string) => {
      const response = await fetchWithAuth(`/api/v1/jobs/${jobId}`, { method: "GET" }, token || "base-token")
      return response.json()
    },

    getStatus: async (jobId: number, token?: string) => {
      const response = await fetchWithAuth(`/api/v1/jobs/${jobId}/status`, { method: "GET" }, token || "base-token")
      return response.json()
    },

    delete: async (jobId: number, token?: string) => {
      await fetchWithAuth(`/api/v1/jobs/${jobId}`, { method: "DELETE" }, token || "base-token")
    },

    cleanup: async (token?: string) => {
      const response = await fetchWithAuth("/api/v1/jobs/cleanup", { method: "DELETE" }, token || "base-token")
      return response.json()
    },
  },
}
