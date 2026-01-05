import { Header } from "@/components/landing/header"
import { Pricing } from "@/components/landing/pricing"
import { Footer } from "@/components/landing/footer"

export default function PricingPage() {
  return (
    <div className="min-h-screen">
      <Header />
      <main className="pt-16">
        <Pricing />
      </main>
      <Footer />
    </div>
  )
}
