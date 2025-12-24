import { auth } from "@clerk/nextjs/server"
import { redirect } from "next/navigation"
import { UploadForm } from "@/components/upload/upload-form"
import { Header } from "@/components/landing/header"

const hasClerkKeys = !!(process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY && process.env.CLERK_SECRET_KEY)

export default async function UploadPage() {
  if (hasClerkKeys) {
    const { userId } = await auth()
    if (!userId) {
      redirect("/sign-in")
    }
  }

  return (
    <div className="min-h-screen">
      <Header />
      <div className="container max-w-4xl mx-auto py-12 px-4">
        <div className="space-y-6">
          <div>
            <h1 className="text-3xl md:text-4xl font-bold mb-2 text-balance">Create New Audiobook</h1>
            <p className="text-muted-foreground">Upload a PDF and configure your audiobook settings.</p>
          </div>
          <UploadForm />
        </div>
      </div>
    </div>
  )
}
