import { Header } from "@/components/landing/header"
import { Hero } from "@/components/landing/hero"
import { Features } from "@/components/landing/features"
import { Pricing } from "@/components/landing/pricing"
import { Footer } from "@/components/landing/footer"
import { SetupBanner } from "@/components/setup-banner"

export default function HomePage() {
  return (
    <div className="min-h-screen">
      <Header />
      <main>
        <Hero />
        <div className="container px-4 pt-8">
          <SetupBanner />
        </div>
        <Features />
        <Pricing />
      </main>
      <Footer />
    </div>
  )
}
