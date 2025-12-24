// TypeScript types for API responses and requests

export type JobStatus = "pending" | "processing" | "completed" | "failed" | "cancelled"

export type ConversionMode = "full" | "summary" | "explanation" | "summary_explanation"

export type VoiceProvider = "openai" | "google" | "aws_polly" | "azure" | "eleven_labs"

export type SubscriptionTier = "free" | "pro" | "enterprise"

export type ProductType = "subscription" | "one_time"

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
  auth_provider_id: string
  subscription_tier: SubscriptionTier
  paddle_customer_id?: string | null
  credit_balance: number
  monthly_credits_used: number
  created_at: string
  updated_at?: string | null
}

export interface Product {
  id: number
  name: string
  price: number
  credits_included: number
  type: ProductType
  paddle_product_id: string
  is_active: boolean
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

export interface CheckoutURLRequest {
  product_id: number
}

export interface CheckoutURLResponse {
  checkout_url: string
}
