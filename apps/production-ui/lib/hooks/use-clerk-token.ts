"use client"

import { useAuth } from "@clerk/nextjs"
import { useEffect, useState } from "react"
import { api } from "@/lib/api/client"

export function useClerkToken() {
  const { getToken, isSignedIn } = useAuth()
  const [synced, setSynced] = useState(false)

  useEffect(() => {
    async function syncUser() {
      if (!isSignedIn) return

      try {
        const token = await getToken()
        if (!token) return

        await api.auth.verify(token)
        setSynced(true)
      } catch (error) {
        console.error("Failed to sync user:", error)
      }
    }

    syncUser()
  }, [isSignedIn, getToken])

  return { synced }
}
