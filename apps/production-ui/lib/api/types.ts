// TypeScript types for API responses and requests

export type JobStatus = "pending" | "processing" | "completed" | "failed" | "cancelled"

export type ConversionMode = "full" | "summary" | "explanation" | "summary_explanation"

export type VoiceProvider = "openai" | "google" | "aws_polly" | "azure" | "eleven_labs"

export interface Job {
  id: number
  original_filename: string
  voice_provider: VoiceProvider
  voice_type: string
  reading_speed: number
  include_summary: boolean
  conversion_mode: ConversionMode
  user_id: number
  pdf_s3_key: string
  audio_s3_key?: string | null
  pdf_s3_url?: string | null
  audio_s3_url?: string | null
  status: JobStatus
  progress_percentage: number
  error_message?: string | null
  estimated_cost: number
  tokens_used?: number
  chars_processed?: number
  created_at: string
  started_at?: string | null
  completed_at?: string | null
}

export interface User {
  id: number
  email: string
  first_name?: string | null
  last_name?: string | null
  created_at: string
  updated_at?: string | null
}

export interface CreateJobRequest {
  file: File
  voice_provider?: VoiceProvider
  voice_type?: string
  reading_speed?: number
  include_summary?: boolean
  conversion_mode?: ConversionMode
}
