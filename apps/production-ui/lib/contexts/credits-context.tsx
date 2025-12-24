"use client"

import { createContext, useContext, useState, useEffect, type ReactNode, useCallback } from "react"
import { useAuth } from "@clerk/nextjs"
import { api } from "@/lib/api/client"
import type { User } from "@/lib/api/types"

interface CreditsContextValue {
  credits: number
  user: User | null
  loading: boolean
  error: string | null
  refreshCredits: () => Promise<void>
}

const CreditsContext = createContext<CreditsContextValue | undefined>(undefined)

function AuthenticatedCreditsProvider({ children }: { children: ReactNode }) {
  const { isSignedIn, getToken } = useAuth()
  const [credits, setCredits] = useState<number>(0)
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const refreshCredits = useCallback(async () => {
    if (!isSignedIn) {
      setCredits(0)
      setUser(null)
      setLoading(false)
      return
    }

    try {
      setLoading(true)
      setError(null)
      const token = await getToken()
      if (!token) throw new Error("No authentication token")

      const userData = (await api.auth.getMe(token)) as User
      setUser(userData)
      setCredits(userData.credit_balance)
    } catch (err) {
      console.error("[v0] Failed to fetch credits:", err)
      setError(err instanceof Error ? err.message : "Failed to fetch credits")
      setCredits(0)
    } finally {
      setLoading(false)
    }
  }, [isSignedIn, getToken])

  useEffect(() => {
    refreshCredits()
  }, [refreshCredits])

  return (
    <CreditsContext.Provider value={{ credits, user, loading, error, refreshCredits }}>
      {children}
    </CreditsContext.Provider>
  )
}

export function CreditsProvider({ children, noAuth = false }: { children: ReactNode; noAuth?: boolean }) {
  if (noAuth) {
    return (
      <CreditsContext.Provider
        value={{
          credits: 0,
          user: null,
          loading: false,
          error: null,
          refreshCredits: async () => {},
        }}
      >
        {children}
      </CreditsContext.Provider>
    )
  }

  return <AuthenticatedCreditsProvider>{children}</AuthenticatedCreditsProvider>
}

export function useCredits() {
  const context = useContext(CreditsContext)
  if (context === undefined) {
    throw new Error("useCredits must be used within a CreditsProvider")
  }
  return context
}
