// Voice options for different TTS providers

import type { VoiceProvider } from "@/lib/api/types"

export interface VoiceOption {
  id: string
  name: string
  description?: string
}

export const VOICE_OPTIONS: Record<VoiceProvider, VoiceOption[]> = {
  google: [
    { id: "en-US-Chirp3-HD-Sulafat", name: "US Female (Premium)", description: "High-quality US English female voice" },
    { id: "en-US-Wavenet-C", name: "US Female (Standard)", description: "Natural US English female voice" },
    { id: "en-US-Chirp3-HD-Enceladus", name: "US Male (Premium)", description: "High-quality US English male voice" },
    { id: "en-US-Wavenet-I", name: "US Male (Standard)", description: "Natural US English male voice" },
    { id: "en-GB-Chirp3-HD-Despina", name: "UK Female (Premium)", description: "High-quality UK English female voice" },
    { id: "en-GB-Wavenet-F", name: "UK Female (Standard)", description: "Natural UK English female voice" },
    { id: "en-GB-Chirp3-HD-Umbriel", name: "UK Male (Premium)", description: "High-quality UK English male voice" },
    { id: "en-GB-Wavenet-O", name: "UK Male (Standard)", description: "Natural UK English male voice" },
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
