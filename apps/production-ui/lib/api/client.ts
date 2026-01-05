// API client with Clerk authentication

const ENV = process.env.NEXT_PUBLIC_ENVIRONMENT || "sandbox"
const API_BASE_URL =
  ENV === "production"
    ? process.env.NEXT_PUBLIC_PROD_API_URL || "https://api.pdf2audiobook.com"
    : process.env.NEXT_PUBLIC_SANDBOX_API_URL || "http://localhost:8000"

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

  // Add authorization header if token is provided
  if (token) {
    headers["Authorization"] = `Bearer ${token}`
  }

  // Don't set Content-Type for FormData, browser will set it with boundary
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
  // Auth endpoints
  auth: {
    verify: async (token: string) => {
      const response = await fetchWithAuth("/api/v1/auth/verify", {
        method: "POST",
        body: JSON.stringify({ token }),
      })
      return response.json()
    },

    getMe: async (token: string) => {
      const response = await fetchWithAuth("/api/v1/auth/me", { method: "GET" }, token)
      return response.json()
    },

    updateMe: async (token: string, data: { first_name?: string; last_name?: string }) => {
      const response = await fetchWithAuth(
        "/api/v1/auth/me",
        {
          method: "PUT",
          body: JSON.stringify(data),
        },
        token,
      )
      return response.json()
    },
  },

  // Job endpoints
  jobs: {
    create: async (token: string, jobData: FormData) => {
      const response = await fetchWithAuth(
        "/api/v1/jobs/",
        {
          method: "POST",
          body: jobData,
        },
        token,
      )
      return response.json()
    },

    list: async (token: string, skip = 0, limit = 50) => {
      const response = await fetchWithAuth(`/api/v1/jobs/?skip=${skip}&limit=${limit}`, { method: "GET" }, token)
      return response.json()
    },

    get: async (token: string, jobId: number) => {
      const response = await fetchWithAuth(`/api/v1/jobs/${jobId}`, { method: "GET" }, token)
      return response.json()
    },

    getStatus: async (token: string, jobId: number) => {
      const response = await fetchWithAuth(`/api/v1/jobs/${jobId}/status`, { method: "GET" }, token)
      return response.json()
    },

    delete: async (token: string, jobId: number) => {
      await fetchWithAuth(`/api/v1/jobs/${jobId}`, { method: "DELETE" }, token)
    },

    cleanup: async (token: string) => {
      const response = await fetchWithAuth("/api/v1/jobs/cleanup", { method: "DELETE" }, token)
      return response.json()
    },
  },

  // Payment endpoints
  payments: {
    getProducts: async () => {
      const response = await fetchWithAuth("/api/v1/payments/products", { method: "GET" })
      return response.json()
    },

    createCheckoutUrl: async (token: string, productId: number) => {
      const response = await fetchWithAuth(
        "/api/v1/payments/checkout-url",
        {
          method: "POST",
          body: JSON.stringify({ product_id: productId }),
        },
        token,
      )
      return response.json()
    },
  },
}
