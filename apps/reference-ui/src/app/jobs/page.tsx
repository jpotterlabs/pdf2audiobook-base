'use client'

import { useEffect, useState } from 'react'
import { getJobs, deleteJob, cleanupFailedJobs } from '../../lib/api'
import { Job } from '../../lib/types'
import Link from 'next/link'

export default function JobsPage() {
  const [jobs, setJobs] = useState<Job[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isDeleting, setIsDeleting] = useState(false)

  const fetchJobs = async () => {
    try {
      const fetchedJobs = await getJobs()
      setJobs(fetchedJobs)
    } catch (error) {
      console.error('Failed to fetch jobs:', error)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchJobs()
  }, [])

  const handleDeleteJob = async (jobId: number) => {
    if (!confirm('Are you sure you want to delete this job? This action cannot be undone.')) {
      return
    }

    setIsDeleting(true)
    try {
      await deleteJob(jobId)
      await fetchJobs() // Refresh list
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
      const result = await cleanupFailedJobs()
      alert(result.message)
      await fetchJobs() // Refresh list
    } catch (error) {
      console.error('Failed to cleanup jobs:', error)
      alert('Failed to cleanup jobs.')
    } finally {
      setIsDeleting(false)
    }
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

      {/* Simplified Info Banner */}
      <div className="bg-blue-50 p-4 rounded-lg border border-blue-200 mb-8 flex items-center justify-between">
        <div>
          <p className="text-blue-800 font-medium">Base Mode Enabled</p>
          <p className="text-blue-600 text-sm">Job history is stored locally for the Base User.</p>
        </div>
        <Link
          href="/upload"
          className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700 transition-colors"
        >
          New Conversion
        </Link>
      </div>

      {isLoading ? (
        <div className="text-center py-20">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-500">Loading your jobs...</p>
        </div>
      ) : jobs.length === 0 ? (
        <div className="text-center py-20 bg-gray-50 rounded-xl border border-dashed border-gray-300">
          <p className="text-lg text-gray-600 font-medium">You haven't created any jobs yet.</p>
          <p className="text-gray-500 mb-6">Upload your first PDF to get started.</p>
          <Link
            href="/upload"
            className="bg-blue-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-blue-700 transition-colors inline-block"
          >
            Create your first job
          </Link>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-lg overflow-hidden border border-gray-200">
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
                  <tr key={job.id} className="hover:bg-gray-50 transition-colors">
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
                      <div className="flex items-center gap-2">
                        <div className="w-16 bg-gray-200 rounded-full h-1.5 overflow-hidden">
                          <div
                            className="bg-blue-600 h-full transition-all duration-500"
                            style={{ width: `${job.progress_percentage}%` }}
                          />
                        </div>
                        <span>{job.progress_percentage}%</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(job.created_at).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-4">
                      {job.status === 'completed' && job.audio_s3_url && (
                        <a
                          href={job.audio_s3_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-green-600 hover:text-green-900"
                        >
                          Download
                        </a>
                      )}
                      <button
                        onClick={() => handleDeleteJob(job.id)}
                        disabled={isDeleting}
                        className="text-red-600 hover:text-red-900 disabled:opacity-50"
                        title="Delete Job"
                      >
                        Delete
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
