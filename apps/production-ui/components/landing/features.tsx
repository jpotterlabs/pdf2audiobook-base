import { BookOpen, Mic2, Zap, Globe, Shield, Sparkles } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"

const features = [
  {
    icon: Mic2,
    title: "Natural AI Voices",
    description: "Choose from multiple premium TTS providers including OpenAI, Google, ElevenLabs, and more.",
  },
  {
    icon: Sparkles,
    title: "AI Summaries",
    description: "Get intelligent summaries or full word-for-word conversion. Your choice.",
  },
  {
    icon: Zap,
    title: "Lightning Fast",
    description: "Process PDFs in minutes, not hours. Our cloud infrastructure ensures rapid conversion.",
  },
  {
    icon: Globe,
    title: "Multi-Language Support",
    description: "Support for dozens of languages and accents across all major TTS providers.",
  },
  {
    icon: Shield,
    title: "Secure & Private",
    description: "Your documents are encrypted and automatically deleted after conversion.",
  },
  {
    icon: BookOpen,
    title: "Perfect Audio Quality",
    description: "High-quality MP3 output with customizable reading speed and voice selection.",
  },
]

export function Features() {
  return (
    <section id="features" className="py-24 px-4 relative">
      <div className="max-w-7xl mx-auto">
        {/* Section header */}
        <div className="text-center mb-16 space-y-4">
          <h2 className="text-3xl md:text-5xl font-bold tracking-tight text-balance">
            Everything You Need for{" "}
            <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              Perfect Audiobooks
            </span>
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto leading-relaxed">
            Powerful features designed to give you the best PDF to audiobook conversion experience.
          </p>
        </div>

        {/* Features grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <Card
              key={index}
              className="glass group hover:bg-card/70 transition-all duration-300 hover:scale-105 hover:shadow-2xl hover:shadow-primary/20 border-border/50"
            >
              <CardContent className="p-6 space-y-4">
                <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
                  <feature.icon className="w-6 h-6 text-primary" />
                </div>
                <h3 className="text-xl font-semibold">{feature.title}</h3>
                <p className="text-muted-foreground leading-relaxed">{feature.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}
