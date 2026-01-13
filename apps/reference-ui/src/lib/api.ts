import axios from 'axios'
import { Job, Product, User } from './types'

/**
 * API base URL strategy:
 * - Defaults to http://localhost:8000
 * - We normalize to always target the versioned API under /api/v1.
 */
const getApiBaseUrl = () => {
  const raw = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'

  try {
    const url = new URL(raw)
    // If the path already ends with /api/v1, respect it as-is
    if (url.pathname.replace(/\/+$/, '') === '/api/v1') {
      return url.toString().replace(/\/+$/, '')
    }

    // Otherwise, ensure /api/v1 is appended
    url.pathname = '/api/v1'
    return url.toString().replace(/\/+$/, '')
  } catch {
    // Fallback: assume the raw value is already a correct base
    return raw.replace(/\/+$/, '')
  }
}

export const API_BASE_URL = getApiBaseUrl()
const MOCK_TOKEN = 'mock-token-for-base-pipeline'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
})

const getHeaders = () => ({
  headers: {
    Authorization: `Bearer ${MOCK_TOKEN}`,
  },
})

export const createJob = async (
  formData: FormData
): Promise<Job> => {
  const response = await apiClient.post('/jobs/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
      Authorization: `Bearer ${MOCK_TOKEN}`,
    },
  })
  return response.data
}

export const getJobs = async (): Promise<Job[]> => {
  const response = await apiClient.get('/jobs/', getHeaders())
  return response.data
}

export const getJob = async (jobId: number): Promise<Job> => {
  const response = await apiClient.get(`/jobs/${jobId}`, getHeaders())
  return response.data
}

export const getJobStatus = async (
  jobId: number
): Promise<any> => {
  const response = await apiClient.get(
    `/jobs/${jobId}/status`,
    getHeaders()
  )
  return response.data
}

export const getCurrentUser = async (): Promise<User> => {
  const response = await apiClient.get('/auth/me', getHeaders())
  return response.data
}

export const updateUser = async (
  userUpdate: any
): Promise<User> => {
  const response = await apiClient.put(
    '/auth/me',
    userUpdate,
    getHeaders()
  )
  return response.data
}

export const verifyToken = async (token: string): Promise<any> => {
  const response = await apiClient.post(
    '/auth/verify',
    { token },
    getHeaders()
  )
  return response.data
}

export const deleteJob = async (
  jobId: number
): Promise<void> => {
  await apiClient.delete(`/jobs/${jobId}`, getHeaders())
}

export const cleanupFailedJobs = async (): Promise<any> => {
  const response = await apiClient.delete('/jobs/cleanup', getHeaders())
  return response.data
}
