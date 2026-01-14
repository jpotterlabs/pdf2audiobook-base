// Voice options for different TTS providers

import type { VoiceProvider } from "@/lib/api/types"

export interface VoiceOption {
  id: string
  name: string
  description?: string
}

export const VOICE_OPTIONS: Record<VoiceProvider, VoiceOption[]> = {
  google: [
    { id: "us_female_premium", name: "US Female (Premium)", description: "High-quality US English female voice" },
    { id: "us_female_std", name: "US Female (Standard)", description: "Natural US English female voice" },
    { id: "us_male_premium", name: "US Male (Premium)", description: "High-quality US English male voice" },
    { id: "us_male_std", name: "US Male (Standard)", description: "Natural US English male voice" },
    { id: "gb_female_premium", name: "UK Female (Premium)", description: "High-quality UK English female voice" },
    { id: "gb_female_std", name: "UK Female (Standard)", description: "Natural UK English female voice" },
    { id: "gb_male_premium", name: "UK Male (Premium)", description: "High-quality UK English male voice" },
    { id: "gb_male_std", name: "UK Male (Standard)", description: "Natural UK English male voice" },
  ],
  openai: [],
  aws_polly: [],
  azure: [],
  eleven_labs: [],
}

export const PROVIDER_NAMES: Record<VoiceProvider, string> = {
  google: "Google Cloud",
  openai: "OpenAI",
  aws_polly: "Amazon Polly",
  azure: "Microsoft Azure",
  eleven_labs: "ElevenLabs",
}
