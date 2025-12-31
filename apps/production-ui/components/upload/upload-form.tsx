"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@clerk/nextjs"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { useCredits } from "@/lib/contexts/credits-context"
import { api, APIError } from "@/lib/api/client"
import { VOICE_OPTIONS, PROVIDER_NAMES } from "@/lib/constants/voices"
import type { VoiceProvider, ConversionMode } from "@/lib/api/types"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Slider } from "@/components/ui/slider"
import { Switch } from "@/components/ui/switch"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { FileUploadZone } from "@/components/upload/file-upload-zone"
import { Loader2, Sparkles, AlertTriangle } from "lucide-react"
import { toast } from "sonner"
import Link from "next/link"

const uploadSchema = z.object({
  file: z.instanceof(File).nullable(),
  voice_provider: z.enum(["openai", "google", "aws_polly", "azure", "eleven_labs"]),
  voice_type: z.string(),
  reading_speed: z.number().min(0.5).max(2.0),
  include_summary: z.boolean(),
  conversion_mode: z.enum(["full", "summary", "explanation", "summary_explanation"]),
})

type UploadFormValues = z.infer<typeof uploadSchema>

export function UploadForm() {
  const router = useRouter()
  const { getToken } = useAuth()
  const { credits, loading: creditsLoading, user, refreshCredits } = useCredits()
  const [uploading, setUploading] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)

  const form = useForm<UploadFormValues>({
    resolver: zodResolver(uploadSchema),
    defaultValues: {
      file: null,
      voice_provider: "google",
      voice_type: "en-US-Wavenet-C",
      reading_speed: 1.0,
      include_summary: false,
      conversion_mode: "full",
    },
  })

  const voiceProvider = form.watch("voice_provider")
  const readingSpeed = form.watch("reading_speed")
  const conversionMode = form.watch("conversion_mode")

  const onSubmit = async (data: UploadFormValues) => {
    if (!selectedFile) {
      toast.error("Please select a PDF file")
      return
    }

    setUploading(true)

    try {
      const token = await getToken()
      if (!token) {
        toast.error("Authentication failed")
        return
      }

      const formData = new FormData()
      formData.append("file", selectedFile)
      formData.append("voice_provider", data.voice_provider)
      formData.append("voice_type", data.voice_type)
      formData.append("reading_speed", data.reading_speed.toString())
      formData.append("include_summary", data.include_summary.toString())
      formData.append("conversion_mode", data.conversion_mode)

      await api.jobs.create(token, formData)

      await refreshCredits()
      toast.success("Job created successfully!")
      router.push("/jobs")
    } catch (error) {
      console.error("Upload failed:", error)
      if (error instanceof APIError && error.status === 402) {
        toast.error("Insufficient credits. Please add credits to continue.")
        router.push("/pricing")
      } else {
        toast.error(error instanceof APIError ? error.message : "Failed to create job. Please try again.")
      }
    } finally {
      setUploading(false)
    }
  }

  const hasLowCredits = !creditsLoading && credits <= 0
  const isOnFreePlan = user?.subscription_tier === "free"
  const shouldDisableSubmit = hasLowCredits && isOnFreePlan

  return (
    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
      {shouldDisableSubmit && (
        <Alert className="border-yellow-500/50 bg-yellow-500/10">
          <AlertTriangle className="h-4 w-4 text-yellow-500" />
          <AlertDescription className="text-yellow-500">
            Your credit balance is low. Please{" "}
            <Link href="/pricing" className="underline font-semibold">
              add credits
            </Link>{" "}
            to create new audiobooks.
          </AlertDescription>
        </Alert>
      )}

      <Card className="glass">
        <CardContent className="p-6">
          <FileUploadZone
            onFileSelect={(file) => {
              setSelectedFile(file)
              form.setValue("file", file)
            }}
            selectedFile={selectedFile}
          />
        </CardContent>
      </Card>

      <Card className="glass">
        <CardContent className="p-6 space-y-6">
          <div>
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-primary" />
              Audiobook Settings
            </h3>
          </div>

          <div className="space-y-2">
            <Label htmlFor="voice_provider">Voice Provider</Label>
            <Select
              value={form.watch("voice_provider")}
              onValueChange={(value: VoiceProvider) => {
                form.setValue("voice_provider", value)
                const firstVoice = VOICE_OPTIONS[value][0]?.id || "default"
                form.setValue("voice_type", firstVoice)
              }}
            >
              <SelectTrigger id="voice_provider" className="glass-strong">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="glass-strong">
                <SelectItem value="google">Google Cloud TTS</SelectItem>
              </SelectContent>
            </Select>
            <p className="text-xs text-muted-foreground">High-quality voices powered by Google Cloud</p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="voice_type">Voice</Label>
            <Select value={form.watch("voice_type")} onValueChange={(value) => form.setValue("voice_type", value)}>
              <SelectTrigger id="voice_type" className="glass-strong">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="glass-strong">
                {VOICE_OPTIONS[voiceProvider as VoiceProvider].map((voice: any) => (
                  <SelectItem key={voice.id} value={voice.id}>
                    <div>
                      <div>{voice.name}</div>
                      {voice.description && <div className="text-xs text-muted-foreground">{voice.description}</div>}
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <p className="text-xs text-muted-foreground">Select a specific voice style</p>
          </div>

          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <Label htmlFor="reading_speed">Reading Speed</Label>
              <span className="text-sm font-medium text-primary">{Number(readingSpeed || 1).toFixed(1)}x</span>
            </div>
            <Slider
              id="reading_speed"
              min={0.5}
              max={2.0}
              step={0.1}
              value={[readingSpeed]}
              onValueChange={(value) => form.setValue("reading_speed", value[0])}
              className="py-4"
            />
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>Slower (0.5x)</span>
              <span>Normal (1.0x)</span>
              <span>Faster (2.0x)</span>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="conversion_mode">Conversion Mode</Label>
            <Select
              value={conversionMode}
              onValueChange={(value: ConversionMode) => form.setValue("conversion_mode", value)}
            >
              <SelectTrigger id="conversion_mode" className="glass-strong">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="glass-strong">
                <SelectItem value="full">
                  <div>
                    <div>Full Reading</div>
                    <div className="text-xs text-muted-foreground">Word-for-word conversion</div>
                  </div>
                </SelectItem>
                <SelectItem value="summary">
                  <div>
                    <div>Summary Only</div>
                    <div className="text-xs text-muted-foreground">AI-generated summary</div>
                  </div>
                </SelectItem>
                <SelectItem value="explanation">
                  <div>
                    <div>Explanation</div>
                    <div className="text-xs text-muted-foreground">Core concepts explained</div>
                  </div>
                </SelectItem>
                <SelectItem value="summary_explanation">
                  <div>
                    <div>Summary & Explanation</div>
                    <div className="text-xs text-muted-foreground">Best of both worlds</div>
                  </div>
                </SelectItem>
              </SelectContent>
            </Select>
            <p className="text-xs text-muted-foreground">How should the PDF be converted?</p>
          </div>

          <div className="flex items-center justify-between p-4 rounded-lg bg-muted/30">
            <div className="space-y-0.5">
              <Label htmlFor="include_summary" className="cursor-pointer">
                Include AI Summary
              </Label>
              <p className="text-xs text-muted-foreground">Prepend an AI-generated summary before the audiobook</p>
            </div>
            <Switch
              id="include_summary"
              checked={form.watch("include_summary")}
              onCheckedChange={(checked) => form.setValue("include_summary", checked)}
            />
          </div>
        </CardContent>
      </Card>

      <div className="flex items-center gap-4">
        <Button type="submit" size="lg" disabled={!selectedFile || uploading || shouldDisableSubmit} className="flex-1">
          {uploading ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Creating Audiobook...
            </>
          ) : (
            "Create Audiobook"
          )}
        </Button>
        <Button type="button" size="lg" variant="outline" onClick={() => router.push("/jobs")}>
          Cancel
        </Button>
      </div>
    </form>
  )
}
