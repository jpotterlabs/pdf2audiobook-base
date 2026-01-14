"use client"

import * as React from "react"

import { AlertCircle } from "lucide-react"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"

export function SetupBanner() {
  const hasApiUrl = !!process.env.NEXT_PUBLIC_API_URL

  if (hasApiUrl) return null

  return (
    <Alert variant="destructive" className="mb-8">
      <AlertCircle className="h-4 w-4" />
      <AlertTitle>Setup Required</AlertTitle>
      <AlertDescription className="space-y-2">
        <p>This application requires environment variables to be configured:</p>
        <ul className="list-disc list-inside space-y-1 text-sm">
          {!hasApiUrl && (
            <li>
              <strong>NEXT_PUBLIC_API_URL</strong> - Your backend API URL (defaults to https://api.pdf2audiobook.xyz)
            </li>
          )}
        </ul>
      </AlertDescription>
    </Alert>
  )
}
