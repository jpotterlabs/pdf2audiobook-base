"use client"

import { createContext, useContext, useState, useEffect, type ReactNode, useCallback } from "react"
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

export function CreditsProvider({ children, noAuth = false }: { children: ReactNode; noAuth?: boolean }) {
  const [credits, setCredits] = useState<number>(0)
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const refreshCredits = useCallback(async () => {
    // For base pipeline, we just return a default state or fetch from a public /me if available
    // But since auth is gone, we'll just keep it simple
    setCredits(0)
    setUser(null)
    setLoading(false)
  }, [])

  useEffect(() => {
    refreshCredits()
  }, [refreshCredits])

  return (
    <CreditsContext.Provider value={{ credits, user, loading, error, refreshCredits }}>
      {children}
    </CreditsContext.Provider>
  )
}

export function useCredits() {
  const context = useContext(CreditsContext)
  if (context === undefined) {
    throw new Error("useCredits must be used within a CreditsProvider")
  }
  return context
}
