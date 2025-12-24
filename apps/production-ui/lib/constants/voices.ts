// Voice options for different TTS providers

import type { VoiceProvider } from "@/lib/api/types"

export interface VoiceOption {
  id: string
  name: string
  description?: string
}

export const VOICE_OPTIONS: Record<VoiceProvider, VoiceOption[]> = {
  openai: [
    { id: "alloy", name: "Alloy", description: "Neutral and balanced" },
    { id: "echo", name: "Echo", description: "Clear and articulate" },
    { id: "fable", name: "Fable", description: "Warm and expressive" },
    { id: "onyx", name: "Onyx", description: "Deep and authoritative" },
    { id: "nova", name: "Nova", description: "Friendly and energetic" },
    { id: "shimmer", name: "Shimmer", description: "Soft and gentle" },
  ],
  google: [
    { id: "en-US-Neural2-A", name: "US English - Neural A" },
    { id: "en-US-Neural2-C", name: "US English - Neural C" },
    { id: "en-US-Neural2-D", name: "US English - Neural D" },
    { id: "en-US-Neural2-E", name: "US English - Neural E" },
  ],
  aws_polly: [
    { id: "Joanna", name: "Joanna", description: "US English, Female" },
    { id: "Matthew", name: "Matthew", description: "US English, Male" },
    { id: "Salli", name: "Salli", description: "US English, Female" },
    { id: "Joey", name: "Joey", description: "US English, Male" },
  ],
  azure: [
    { id: "en-US-JennyNeural", name: "Jenny Neural" },
    { id: "en-US-GuyNeural", name: "Guy Neural" },
    { id: "en-US-AriaNeural", name: "Aria Neural" },
  ],
  eleven_labs: [
    { id: "default", name: "Default Voice" },
    { id: "adam", name: "Adam" },
    { id: "bella", name: "Bella" },
    { id: "rachel", name: "Rachel" },
  ],
}

export const PROVIDER_NAMES: Record<VoiceProvider, string> = {
  openai: "OpenAI",
  google: "Google Cloud",
  aws_polly: "Amazon Polly",
  azure: "Microsoft Azure",
  eleven_labs: "ElevenLabs",
}
