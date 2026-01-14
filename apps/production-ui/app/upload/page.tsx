import { UploadForm } from "@/components/upload/upload-form"
import { Header } from "@/components/landing/header"

export default async function UploadPage() {
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
