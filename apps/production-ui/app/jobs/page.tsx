import { auth } from "@clerk/nextjs/server"
import { redirect } from "next/navigation"
import { JobsDashboard } from "@/components/jobs/jobs-dashboard"
import { Header } from "@/components/landing/header"

const hasClerkKeys = !!(process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY && process.env.CLERK_SECRET_KEY)

export default async function JobsPage() {
  if (hasClerkKeys) {
    const { userId } = await auth()
    if (!userId) {
      redirect("/sign-in")
    }
  }

  return (
    <div className="min-h-screen">
      <Header />
      <JobsDashboard />
    </div>
  )
}
