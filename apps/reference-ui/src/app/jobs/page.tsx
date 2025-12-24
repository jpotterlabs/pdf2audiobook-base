'use client'

import { useEffect, useState } from 'react'
import { getJobs, deleteJob, cleanupFailedJobs } from '../../lib/api'
import { Job } from '../../lib/types'
import Link from 'next/link'
import { useAuth } from '@clerk/nextjs'

const hasClerkKey =
  typeof process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY === 'string' &&
  process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY.startsWith('pk_')

export default function JobsPage() {
  const [jobs, setJobs] = useState<Job[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isDeleting, setIsDeleting] = useState(false)
  const { getToken } = useAuth()

  const fetchJobs = async () => {
    try {
      if (!hasClerkKey) {
        setIsLoading(false)
        return
      }

      const token = await getToken()
      if (!token) {
        setIsLoading(false)
        return
      }

      const fetchedJobs = await getJobs(token)
      setJobs(fetchedJobs)
    } catch (error) {
      console.error('Failed to fetch jobs:', error)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchJobs()
  }, [getToken])

  const handleDeleteJob = async (jobId: number) => {
    if (!confirm('Are you sure you want to delete this job? This action cannot be undone.')) {
      return
    }

    setIsDeleting(true)
    try {
      const token = await getToken()
      if (token) {
        await deleteJob(jobId, token)
        await fetchJobs() // Refresh list
      }
    } catch (error) {
      console.error('Failed to delete job:', error)
      alert('Failed to delete job. Please try again.')
    } finally {
      setIsDeleting(false)
    }
  }

  const handleCleanupFailed = async () => {
    if (!confirm('Are you sure you want to permanently delete all failed and cancelled jobs?')) {
      return
    }

    setIsDeleting(true)
    try {
      const token = await getToken()
      if (token) {
        const result = await cleanupFailedJobs(token)
        alert(result.message)
        await fetchJobs() // Refresh list
      }
    } catch (error) {
      console.error('Failed to cleanup jobs:', error)
      alert('Failed to cleanup jobs.')
    } finally {
      setIsDeleting(false)
    }
  }

  if (!hasClerkKey) {
    return (
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <h1 className="text-2xl md:text-3xl font-bold text-gray-900 mb-4">
          My Jobs
        </h1>
        <p className="text-sm text-gray-600">
          Clerk is not configured in this environment, so job history cannot be
          loaded. In production, this page will show your PDF-to-audiobook
          conversions.
        </p>
      </div>
    )
  }

  const hasFailedJobs = jobs.some(j => j.status === 'failed' || j.status === 'cancelled')

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="flex flex-col md:flex-row justify-between items-center mb-12">
        <div className="text-center md:text-left mb-4 md:mb-0">
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-2">
            My Jobs
          </h1>
          <p className="text-xl text-gray-600">
            Manage your PDF conversions.
          </p>
        </div>

        {hasFailedJobs && (
          <button
            onClick={handleCleanupFailed}
            disabled={isDeleting}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50"
          >
            {isDeleting ? 'Cleaning...' : 'Clean Up Failed Jobs'}
          </button>
        )}
      </div>

      {isLoading ? (
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4">Loading jobs...</p>
        </div>
      ) : jobs.length === 0 ? (
        <div className="text-center">
          <p className="text-lg">You haven't created any jobs yet.</p>
          <Link
            href="/upload"
            className="text-blue-600 hover:underline mt-4 inline-block"
          >
            Create your first job
          </Link>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Filename
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Progress
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Created At
                  </th>
                  <th scope="col" className="relative px-6 py-3">
                    <span className="sr-only">Actions</span>
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {jobs.map((job) => (
                  <tr key={job.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {job.original_filename}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <span
                        className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${job.status === 'completed'
                          ? 'bg-green-100 text-green-800'
                          : job.status === 'failed'
                            ? 'bg-red-100 text-red-800'
                            : 'bg-yellow-100 text-yellow-800'
                          }`}
                      >
                        {job.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {job.progress_percentage}%
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(job.created_at).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-3">
                      <Link
                        href={`/jobs/view?id=${job.id}`}
                        className="text-blue-600 hover:text-blue-900"
                      >
                        View
                      </Link>
                      <button
                        onClick={() => handleDeleteJob(job.id)}
                        disabled={isDeleting}
                        className="text-red-600 hover:text-red-900 disabled:opacity-50"
                        title="Delete Job"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
