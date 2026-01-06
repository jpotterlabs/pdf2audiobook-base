"use client"

import { useEffect, useState } from "react"
import { useAuth } from "@clerk/nextjs"
import { api } from "@/lib/api/client"
import { useCredits } from "@/lib/contexts/credits-context"
import type { Job } from "@/lib/api/types"
import { Button } from "@/components/ui/button"
import { JobCard } from "@/components/jobs/job-card"
import { Trash2, RefreshCw, AlertCircle } from "lucide-react"
import { toast } from "sonner"
import { useClerkToken } from "@/lib/hooks/use-clerk-token"

export function JobsDashboard() {
  const { getToken } = useAuth()
  useClerkToken()
  const { user, credits, refreshCredits } = useCredits()
  const [jobs, setJobs] = useState<Job[]>([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchJobs = async () => {
    try {
      const token = await getToken()
      if (!token) {
        setError("Authentication required")
        setLoading(false)
        return
      }

      const data = await api.jobs.list(token)
      setJobs(data)
      setError(null)
    } catch (error) {
      console.error("Failed to fetch jobs:", error)
      setError("Unable to connect to server. Please check your API connection.")
      if (!refreshing) {
        toast.error("Failed to load jobs")
      }
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  const handleCleanup = async () => {
    try {
      const token = await getToken()
      if (!token) return

      await api.jobs.cleanup(token)
      toast.success("Failed jobs cleaned up")
      await fetchJobs()
    } catch (error) {
      console.error("Failed to cleanup jobs:", error)
      toast.error("Failed to cleanup jobs")
    }
  }

  const handleDeleteJob = async (jobId: number) => {
    try {
      const token = await getToken()
      if (!token) return

      await api.jobs.delete(token, jobId)
      toast.success("Job deleted")
      setJobs((prev) => prev.filter((job) => job.id !== jobId))
    } catch (error) {
      console.error("Failed to delete job:", error)
      toast.error("Failed to delete job")
    }
  }

  const handleRefresh = () => {
    setRefreshing(true)
    Promise.all([fetchJobs(), refreshCredits()]).finally(() => {
      setRefreshing(false)
    })
  }

  useEffect(() => {
    fetchJobs()
    refreshCredits()
  }, [])

  useEffect(() => {
    const hasActiveJobs = jobs.some((job) => job.status === "pending" || job.status === "processing")

    if (!hasActiveJobs) return

    const interval = setInterval(() => {
      fetchJobs()
    }, 5000) // Poll every 5 seconds

    return () => clearInterval(interval)
  }, [jobs])

  const failedJobsCount = jobs.filter((job) => job.status === "failed" || job.status === "cancelled").length

  if (error && !loading) {
    return (
      <div className="container max-w-7xl mx-auto py-12 px-4">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center space-y-4 max-w-md">
            <div className="w-16 h-16 rounded-full bg-destructive/10 flex items-center justify-center mx-auto">
              <AlertCircle className="w-8 h-8 text-destructive" />
            </div>
            <h3 className="text-xl font-semibold">Connection Error</h3>
            <p className="text-muted-foreground leading-relaxed">{error}</p>
            <div className="text-sm text-muted-foreground space-y-1">
              <p>Make sure:</p>
              <ul className="list-disc list-inside text-left">
                <li>Your backend API is running</li>
                <li>NEXT_PUBLIC_API_URL is configured correctly</li>
                <li>You have a stable internet connection</li>
              </ul>
            </div>
            <Button onClick={handleRefresh} variant="outline">
              <RefreshCw className="w-4 h-4 mr-2" />
              Try Again
            </Button>
          </div>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="container max-w-7xl mx-auto py-12 px-4">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center space-y-4">
            <RefreshCw className="w-8 h-8 animate-spin mx-auto text-primary" />
            <p className="text-muted-foreground">Loading your library...</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="container max-w-7xl mx-auto py-12 px-4 space-y-8">
      {/* Account Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="glass p-6 rounded-xl border border-border/50 flex flex-col justify-between">
          <div className="space-y-1">
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Current Plan</p>
            <h3 className="text-2xl font-bold capitalize">{user?.subscription_tier || "Free"}</h3>
          </div>
          <p className="text-sm text-muted-foreground mt-4">
            {user?.subscription_tier === "pro"
              ? "3 conversions included per month"
              : user?.subscription_tier === "enterprise"
                ? "7 conversions included per month"
                : "Basic pay-as-you-go access"}
          </p>
        </div>

        <div className="glass p-6 rounded-xl border border-border/50 flex flex-col justify-between">
          <div className="space-y-1">
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Available Credits</p>
            <div className="flex items-baseline gap-2">
              <h3 className="text-2xl font-bold">${Number(credits || 0).toFixed(2)}</h3>
              <span className="text-xs text-muted-foreground italic">USD</span>
            </div>
          </div>
          <Link href="/pricing" className="text-sm text-primary hover:underline mt-4 inline-flex items-center gap-1">
            Add more credits <RefreshCw className="w-3 h-3" />
          </Link>
        </div>

        <div className="glass p-6 rounded-xl border border-border/50 flex flex-col justify-between">
          <div className="space-y-1">
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Account ID</p>
            <h3 className="text-sm font-mono truncate">{user?.auth_provider_id || "..."}</h3>
          </div>
          <p className="text-xs text-muted-foreground mt-4">
            Created: {user?.created_at ? new Date(user.created_at).toLocaleDateString() : "..."}
          </p>
        </div>
      </div>

      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl md:text-4xl font-bold mb-2 text-balance">My Library</h1>
          <p className="text-muted-foreground">
            {jobs.length} {jobs.length === 1 ? "audiobook" : "audiobooks"} in your library
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" size="sm" onClick={handleRefresh} disabled={refreshing}>
            <RefreshCw className={`w-4 h-4 mr-2 ${refreshing ? "animate-spin" : ""}`} />
            Refresh
          </Button>
          {failedJobsCount > 0 && (
            <Button variant="destructive" size="sm" onClick={handleCleanup}>
              <Trash2 className="w-4 h-4 mr-2" />
              Clean Up Failed ({failedJobsCount})
            </Button>
          )}
        </div>
      </div>

      {/* Jobs grid */}
      {jobs.length === 0 ? (
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center space-y-4 max-w-md">
            <div className="w-16 h-16 rounded-full bg-muted flex items-center justify-center mx-auto">
              <Trash2 className="w-8 h-8 text-muted-foreground" />
            </div>
            <h3 className="text-xl font-semibold">No audiobooks yet</h3>
            <p className="text-muted-foreground leading-relaxed">
              Upload your first PDF to get started. Your converted audiobooks will appear here.
            </p>
            <Button asChild>
              <a href="/upload">Upload PDF</a>
            </Button>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {jobs.map((job) => (
            <JobCard key={job.id} job={job} onDelete={handleDeleteJob} />
          ))}
        </div>
      )}
    </div>
  )
}
