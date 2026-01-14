from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum


class JobStatus(str, Enum):
    """Enumeration for the status of a PDF processing job."""

    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


class VoiceProvider(str, Enum):
    """Enumeration for supported Text-to-Speech (TTS) providers."""

    openai = "openai"
    google = "google"
    aws_polly = "aws_polly"
    azure = "azure"
    eleven_labs = "eleven_labs"


class ConversionMode(str, Enum):
    """Enumeration for PDF conversion modes."""

    full = "full"
    summary = "summary"
    explanation = "explanation"
    summary_explanation = "summary_explanation"
    full_explanation = "full_explanation"


# --- User Schemas ---


class UserBase(BaseModel):
    """Base schema for user properties."""

    email: EmailStr = Field(
        ..., json_schema_extra={"example": "user@example.com"}, description="User's unique email address."
    )
    first_name: Optional[str] = Field(
        None, json_schema_extra={"example": "John"}, description="User's first name."
    )
    last_name: Optional[str] = Field(
        None, json_schema_extra={"example": "Doe"}, description="User's last name."
    )


class UserCreate(UserBase):
    """Schema for creating a new user."""

    pass


class UserUpdate(BaseModel):
    """Schema for updating a user's profile information."""

    first_name: Optional[str] = Field(
        None, json_schema_extra={"example": "John"}, description="User's updated first name."
    )
    last_name: Optional[str] = Field(
        None, json_schema_extra={"example": "Doe"}, description="User's updated last name."
    )


class User(UserBase):
    """Schema for representing a user, returned from the API."""

    id: int = Field(
        ..., json_schema_extra={"example": 1}, description="Internal unique identifier for the user."
    )
    created_at: datetime = Field(
        ..., description="Timestamp when the user was created."
    )
    updated_at: Optional[datetime] = Field(
        None, description="Timestamp when the user was last updated."
    )

    model_config = ConfigDict(from_attributes=True)


# --- Job Schemas ---


class JobBase(BaseModel):
    """Base schema for job properties, used for creation."""

    original_filename: str = Field(
        ...,
        json_schema_extra={"example": "my_document.pdf"},
        description="The original filename of the uploaded PDF.",
    )
    voice_provider: VoiceProvider = Field(
        VoiceProvider.openai,
        description="The TTS provider to use for audio generation.",
    )
    voice_type: str = Field(
        "default",
        json_schema_extra={"example": "alloy"},
        description="The specific voice to use from the selected provider.",
    )
    reading_speed: float = Field(
        1.0,
        ge=0.5,
        le=2.0,
        description="The reading speed for the audiobook (0.5x to 2.0x).",
    )
    include_summary: bool = Field(
        False,
        description="Whether to generate and include an AI summary at the beginning of the audiobook.",
    )
    conversion_mode: ConversionMode = Field(
        ConversionMode.full,
        description="Conversion mode: full word-for-word conversion or summary explanation of core concepts.",
    )


class JobCreate(JobBase):
    """Schema used for creating a new job. Inherits all fields from JobBase."""

    pass


class JobUpdate(BaseModel):
    """Schema for updating a job's status or progress."""

    status: Optional[JobStatus] = Field(None, description="The new status of the job.")

    progress_percentage: Optional[int] = Field(
        None, ge=0, le=100, description="The current processing progress (0-100)."
    )

    error_message: Optional[str] = Field(
        None, description="An error message if the job failed."
    )

    audio_s3_url: Optional[str] = Field(
        None, description="The public URL for the generated audio file."
    )

    estimated_cost: Optional[float] = Field(None, description="The estimated cost of the job.")
    chars_processed: Optional[int] = Field(None, description="Total characters processed.")
    tokens_used: Optional[int] = Field(None, description="Total LLM tokens used.")


class Job(JobBase):
    """Schema for representing a job, returned from the API."""

    id: int = Field(
        ..., json_schema_extra={"example": 42}, description="Internal unique identifier for the job."
    )
    user_id: int = Field(
        ..., json_schema_extra={"example": 1}, description="The ID of the user who created the job."
    )
    pdf_s3_key: str = Field(
        ...,
        json_schema_extra={"example": "pdfs/1/my_document.pdf"},
        description="The S3 key for the stored PDF file.",
    )
    audio_s3_key: Optional[str] = Field(
        None,
        json_schema_extra={"example": "audio/1/42.mp3"},
        description="The S3 key for the generated audio file.",
    )
    pdf_s3_url: Optional[str] = Field(
        None,
        json_schema_extra={"example": "https://bucket.s3.amazonaws.com/pdfs/1/my_document.pdf"},
        description="The public URL for the PDF file.",
    )
    audio_s3_url: Optional[str] = Field(
        None,
        json_schema_extra={"example": "https://bucket.s3.amazonaws.com/audio/1/42.mp3"},
        description="The public URL for the generated audio file.",
    )
    status: JobStatus = Field(
        ..., json_schema_extra={"example": JobStatus.completed}, description="The current status of the job."
    )
    progress_percentage: int = Field(
        ..., json_schema_extra={"example": 100}, ge=0, le=100, description="The processing progress (0-100)."
    )
    error_message: Optional[str] = Field(
        None, description="An error message if the job failed."
    )
    estimated_cost: float = Field(0.0, description="The estimated cost of the job.")
    chars_processed: int = Field(0, description="Total characters processed.")
    tokens_used: int = Field(0, description="Total LLM tokens used.")
    created_at: datetime = Field(..., description="Timestamp when the job was created.")
    started_at: Optional[datetime] = Field(
        None, description="Timestamp when processing started."
    )
    completed_at: Optional[datetime] = Field(
        None, description="Timestamp when processing was completed."
    )

    model_config = ConfigDict(from_attributes=True)


# --- Auth Schemas ---


class Token(BaseModel):
    """Schema for the access token returned upon successful authentication."""

    access_token: str = Field(
        ...,
        json_schema_extra={"example": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."},
        description="A JWT access token.",
    )
    token_type: str = Field("bearer", description="The type of the token.")


class TokenData(BaseModel):
    """Schema for the data encoded within the JWT access token."""

    user_id: Optional[int] = Field(
        None, description="The user ID associated with the token."
    )
