'use client'

import React, { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react'
import { useAuth } from '@clerk/nextjs'
import { getCurrentUser } from '../lib/api'

interface CreditsContextType {
    credits: number | null
    loading: boolean
    error: boolean
    refreshCredits: () => Promise<void>
}

const CreditsContext = createContext<CreditsContextType | undefined>(undefined)

export function CreditsProvider({ children }: { children: React.ReactNode }) {
    const { getToken, userId, isLoaded } = useAuth()
    const [credits, setCredits] = useState<number | null>(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(false)

    // Store the latest getToken in a ref to avoid effect dependency churn
    // while ensuring we always use the latest one if it changes.
    const getTokenRef = useRef(getToken)

    useEffect(() => {
        getTokenRef.current = getToken
    }, [getToken])

    const fetchCredits = useCallback(async () => {
        if (!userId) {
            setCredits(null)
            setLoading(false)
            return
        }

        setLoading(true)
        try {
            // Use the ref to get the token function
            const token = await getTokenRef.current()
            if (!token) {
                // If no token (not signed in fully yet?), wait or clear
                // But if userId is present, we should have a token usually.
                // It might be an edge case of valid session but no token for audience
                setLoading(false)
                return
            }

            const user = await getCurrentUser(token)
            setCredits(user.credit_balance)
            setError(false)
        } catch (err) {
            console.error('Failed to fetch user credits:', err)
            setError(true)
        } finally {
            setLoading(false)
        }
    }, [userId])

    // Initial fetch when userId becomes available
    useEffect(() => {
        if (isLoaded && userId) {
            fetchCredits()
        } else if (isLoaded && !userId) {
            setCredits(null)
        }
    }, [isLoaded, userId, fetchCredits])

    return (
        <CreditsContext.Provider value={{ credits, loading, error, refreshCredits: fetchCredits }}>
            {children}
        </CreditsContext.Provider>
    )
}

export function useCredits() {
    const context = useContext(CreditsContext)
    if (context === undefined) {
        // Fallback for when provider is missing (e.g. missing Clerk key/no-auth mode)
        // This prevents the app from crashing in development or build environments
        return {
            credits: null,
            loading: false,
            error: false,
            refreshCredits: async () => { }
        }
    }
    return context
}
