"use client"

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { ArrowRight, Sparkles } from "lucide-react"

export function Hero() {
  return (
    <section className="relative min-h-[90vh] flex items-center justify-center overflow-hidden px-4 py-20">
      {/* Animated background gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary/20 via-background to-accent/20 animate-pulse-slow" />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(56,140,230,0.1),transparent_50%)]" />

      <div className="relative z-10 max-w-5xl mx-auto text-center space-y-8">
        {/* Badge */}
        <div className="inline-flex items-center gap-2 px-4 py-2 glass rounded-full text-sm text-muted-foreground animate-fade-in">
          <Sparkles className="w-4 h-4 text-accent" />
          <span>AI-Powered PDF to Audiobook Conversion</span>
        </div>

        {/* Main heading */}
        <h1 className="text-5xl md:text-7xl lg:text-8xl font-bold tracking-tight text-balance animate-fade-in-up">
          Turn Your PDFs into{" "}
          <span className="bg-gradient-to-r from-primary via-accent to-primary bg-clip-text text-transparent animate-gradient">
            Lifelike Audiobooks
          </span>
        </h1>

        {/* Subheading */}
        <p className="text-lg md:text-xl lg:text-2xl text-muted-foreground max-w-3xl mx-auto leading-relaxed animate-fade-in-up animation-delay-200">
          Transform any PDF document into a high-quality audiobook with natural AI voices. Perfect for learning on the
          go, accessibility, or simply saving your eyes.
        </p>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 animate-fade-in-up animation-delay-400">
          <Button asChild size="lg" className="text-lg px-8 py-6 group">
            <Link href="/sign-up">
              Get Started Free
              <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Link>
          </Button>
          <Button asChild size="lg" variant="outline" className="text-lg px-8 py-6 glass bg-transparent">
            <Link href="#features">See How It Works</Link>
          </Button>
        </div>

        {/* Social proof */}
        <div className="pt-8 animate-fade-in animation-delay-600">
          <p className="text-sm text-muted-foreground mb-4">Trusted by over 10,000 users worldwide</p>
          <div className="flex items-center justify-center gap-8 opacity-60">
            <div className="text-2xl font-bold">⭐⭐⭐⭐⭐</div>
          </div>
        </div>
      </div>

      {/* Decorative elements */}
      <div className="absolute top-20 left-10 w-72 h-72 bg-primary/20 rounded-full blur-3xl animate-pulse" />
      <div className="absolute bottom-20 right-10 w-96 h-96 bg-accent/20 rounded-full blur-3xl animate-pulse animation-delay-1000" />
    </section>
  )
}
