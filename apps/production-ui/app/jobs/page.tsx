import { JobsDashboard } from "@/components/jobs/jobs-dashboard"
import { Header } from "@/components/landing/header"

export default async function JobsPage() {
  return (
    <div className="min-h-screen">
      <Header />
      <JobsDashboard />
    </div>
  )
}
