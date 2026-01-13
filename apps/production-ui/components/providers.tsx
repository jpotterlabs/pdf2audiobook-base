"use client"

import * as React from "react"
import { CreditsProvider } from "@/lib/contexts/credits-context"

export function Providers({
    children
}: {
    children: React.ReactNode
}) {
    return (
        <CreditsProvider noAuth>
            {children}
        </CreditsProvider>
    )
}
