"use client"

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { BookAudio } from "lucide-react"

export function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-border/40 glass-strong">
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
          <Link href="/#features" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
            Features
          </Link>
          <Link href="/jobs" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
            My Library
          </Link>
        </nav>

        <div className="flex items-center gap-4">
          <Button asChild size="sm">
            <Link href="/upload">Upload PDF</Link>
          </Button>
        </div>
      </div>
    </header>
  )
}
