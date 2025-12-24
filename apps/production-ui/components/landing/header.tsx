"use client"

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { BookAudio, AlertCircle, RefreshCw, Coins } from "lucide-react"
import { SignedIn, SignedOut, UserButton } from "@clerk/nextjs"
import { useCredits } from "@/lib/contexts/credits-context"
import { useState } from "react"

export function Header() {
  const hasClerkKeys = !!process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY
  const { credits, loading, refreshCredits } = useCredits()
  const [refreshing, setRefreshing] = useState(false)

  const handleRefresh = async () => {
    setRefreshing(true)
    await refreshCredits()
    setRefreshing(false)
  }

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border/40 glass-strong">
      {!hasClerkKeys && (
        <div className="bg-yellow-500/10 border-b border-yellow-500/20 px-4 py-2">
          <div className="container flex items-center gap-2 text-sm text-yellow-500">
            <AlertCircle className="w-4 h-4" />
            <span>
              Authentication not configured. Add NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY and CLERK_SECRET_KEY to enable
              sign-in.
            </span>
          </div>
        </div>
      )}

      <div className="container flex h-16 items-center justify-between px-4">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-accent flex items-center justify-center">
            <BookAudio className="w-5 h-5 text-white" />
          </div>
          <span className="font-bold text-xl">PDF2Audiobook</span>
        </Link>

        {/* Navigation */}
        <nav className="hidden md:flex items-center gap-8">
          <Link href="#features" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
            Features
          </Link>
          <Link href="#pricing" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
            Pricing
          </Link>
          <Link href="/jobs" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
            My Library
          </Link>
        </nav>

        <div className="flex items-center gap-4">
          {hasClerkKeys ? (
            <>
              <SignedOut>
                <Button asChild variant="ghost" size="sm">
                  <Link href="/sign-in">Sign In</Link>
                </Button>
                <Button asChild size="sm">
                  <Link href="/sign-up">Get Started</Link>
                </Button>
              </SignedOut>
              <SignedIn>
                <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-primary/10 border border-primary/20">
                  <Coins className="w-4 h-4 text-primary" />
                  {loading ? (
                    <Skeleton className="h-4 w-12" />
                  ) : (
                    <span className="text-sm font-semibold text-primary">${Number(credits || 0).toFixed(2)}</span>
                  )}
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-6 w-6 p-0"
                    onClick={handleRefresh}
                    disabled={refreshing}
                  >
                    <RefreshCw className={`w-3 h-3 ${refreshing ? "animate-spin" : ""}`} />
                  </Button>
                </div>
                <Button asChild size="sm" variant="outline">
                  <Link href="/upload">Upload PDF</Link>
                </Button>
                <UserButton afterSignOutUrl="/" />
              </SignedIn>
            </>
          ) : (
            <Button asChild size="sm" disabled>
              <span>Setup Required</span>
            </Button>
          )}
        </div>
      </div>
    </header>
  )
}
