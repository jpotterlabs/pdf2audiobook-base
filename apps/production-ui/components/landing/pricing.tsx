"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { useAuth } from "@clerk/nextjs"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Check, Loader2, Sparkles } from "lucide-react"
import { api } from "@/lib/api/client"
import type { Product } from "@/lib/api/types"
import { toast } from "sonner"

const FALLBACK_PRICING = {
  free: 0,
  pro: 9.99,
  enterprise: 19.99,
}

export function Pricing() {
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)
  const [upgrading, setUpgrading] = useState<string | null>(null)

  const { isSignedIn, getToken, isLoaded } = useAuth()
  const router = useRouter()

  useEffect(() => {
    async function fetchProducts() {
      try {
        const data = await api.payments.getProducts()
        if (Array.isArray(data)) {
          setProducts(data)
        } else {
          console.error("[v0] API returned unexpected products format:", data)
        }
      } catch (error) {
        console.log("[v0] Using fallback pricing data")
      } finally {
        setLoading(false)
      }
    }
    fetchProducts()
  }, [])

  const handleUpgrade = async (tier: "pro" | "enterprise") => {
    if (!isLoaded) return

    if (!isSignedIn) {
      router.push("/sign-up")
      return
    }

    try {
      setUpgrading(tier)
      const token = await getToken()
      if (!token) throw new Error("Authentication failed")

      const product = products.find((p: Product) => p.subscription_tier === tier)
      if (!product) {
        toast.error(`The ${tier} plan is currently unavailable. Please contact support.`)
        return
      }

      const response = await api.payments.createCheckoutUrl(token, product.id)
      if (response && response.checkout_url) {
        window.location.href = response.checkout_url
      } else {
        throw new Error("Invalid checkout response")
      }
    } catch (error) {
      console.error("Upgrade failed:", error)
      toast.error("Unable to start checkout. Please check your connection.")
    } finally {
      setUpgrading(null)
    }
  }

  const getTierFeatures = (tier: string) => {
    const features = {
      free: [
        "Pay as you go",
        "Estimated cost per book",
        "Standard & Premium voices",
        "Summary or Explanation add-ons",
      ],
      pro: [
        "3 audiobook conversions /mo",
        "300k std / 100k premium chars",
        "Summary or Explanation included",
        "Standard processing speed",
      ],
      enterprise: [
        "7 audiobook conversions /mo",
        "500k std / 250k premium chars",
        "5 Summaries or Explanations",
        "Priority processing",
      ],
    }
    return features[tier as keyof typeof features] || []
  }

  const getPrice = (tier: "free" | "pro" | "enterprise") => {
    const product = products.find((p: Product) => p.subscription_tier === tier)
    return product?.price !== undefined ? product.price : FALLBACK_PRICING[tier]
  }

  if (loading) {
    return (
      <section className="py-24 px-4">
        <div className="max-w-7xl mx-auto text-center">
          <p className="text-muted-foreground">Loading pricing...</p>
        </div>
      </section>
    )
  }

  return (
    <section className="py-24 px-4 relative">
      <div className="max-w-7xl mx-auto">
        {/* Section header */}
        <div className="text-center mb-16 space-y-4">
          <h2 className="text-3xl md:text-5xl font-bold tracking-tight text-balance">
            Simple,{" "}
            <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              Transparent Pricing
            </span>
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto leading-relaxed">
            Choose the plan that fits your needs. Start free, upgrade anytime.
          </p>
        </div>

        {/* Pricing cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {/* Free Tier - The Discover */}
          <Card className="glass border-border/50 hover:border-primary/50 transition-all duration-300">
            <CardHeader>
              <CardTitle className="text-2xl">The Discover</CardTitle>
              <CardDescription>Pay as you go</CardDescription>
              <div className="pt-4">
                <span className="text-4xl font-bold">$0</span>
                <span className="text-muted-foreground">/start</span>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <ul className="space-y-3">
                {getTierFeatures("free").map((feature, i) => (
                  <li key={i} className="flex items-start gap-3">
                    <Check className="w-5 h-5 text-primary shrink-0 mt-0.5" />
                    <span className="text-sm leading-relaxed">{feature}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
            <CardFooter>
              <Button asChild className="w-full bg-transparent" variant="outline">
                <Link href="/sign-up">Get Started</Link>
              </Button>
            </CardFooter>
          </Card>

          {/* Pro Tier - The Research */}
          <Card className="glass border-primary/50 hover:border-primary transition-all duration-300 relative overflow-hidden scale-105">
            <div className="absolute top-0 right-0 bg-gradient-to-l from-primary to-accent text-primary-foreground text-xs font-semibold px-4 py-1 rounded-bl-lg">
              POPULAR
            </div>
            <CardHeader>
              <CardTitle className="text-2xl">The Research</CardTitle>
              <CardDescription>Personal use</CardDescription>
              <div className="pt-4">
                <span className="text-4xl font-bold">${getPrice("pro")}</span>
                <span className="text-muted-foreground">/month</span>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <ul className="space-y-3">
                {getTierFeatures("pro").map((feature, i) => (
                  <li key={i} className="flex items-start gap-3">
                    <Check className="w-5 h-5 text-primary shrink-0 mt-0.5" />
                    <span className="text-sm leading-relaxed">{feature}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
            <CardFooter>
              <Button
                className="w-full"
                onClick={() => handleUpgrade("pro")}
                disabled={upgrading === "pro"}
              >
                {upgrading === "pro" ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Redirecting...
                  </>
                ) : (
                  "Upgrade to Pro"
                )}
              </Button>
            </CardFooter>
          </Card>

          {/* Enterprise Tier - The Intelligence */}
          <Card className="glass border-border/50 hover:border-accent/50 transition-all duration-300">
            <CardHeader>
              <CardTitle className="text-2xl">The Intelligence</CardTitle>
              <CardDescription>Power users</CardDescription>
              <div className="pt-4">
                <span className="text-4xl font-bold">${getPrice("enterprise")}</span>
                <span className="text-muted-foreground">/month</span>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <ul className="space-y-3">
                {getTierFeatures("enterprise").map((feature, i) => (
                  <li key={i} className="flex items-start gap-3">
                    <Check className="w-5 h-5 text-accent shrink-0 mt-0.5" />
                    <span className="text-sm leading-relaxed">{feature}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
            <CardFooter>
              <Button
                className="w-full bg-transparent"
                variant="outline"
                onClick={() => handleUpgrade("enterprise")}
                disabled={upgrading === "enterprise"}
              >
                {upgrading === "enterprise" ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Redirecting...
                  </>
                ) : (
                  "Contact Sales"
                )}
              </Button>
            </CardFooter>
          </Card>
        </div>
      </div>
    </section>
  )
}
