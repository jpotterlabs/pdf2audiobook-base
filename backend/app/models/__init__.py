import enum
import os

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


# Production-safe ENUM creation
def create_enum_type(name, values, metadata):
    """Create ENUM type safely for production environments"""
    # Force lowercase values to prevent case sensitivity issues in DB
    processed_values = [v.lower() if hasattr(v, 'lower') else v for v in values]
    return Enum(*processed_values, name=name.lower(), create_type=True)


class JobStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


class VoiceProvider(str, enum.Enum):
    openai = "openai"
    google = "google"
    aws_polly = "aws_polly"
    azure = "azure"
    eleven_labs = "eleven_labs"


class ConversionMode(str, enum.Enum):
    full = "full"
    summary = "summary"
    explanation = "explanation"
    summary_explanation = "summary_explanation"
    full_explanation = "full_explanation"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    auth_provider_id = Column(String(255), unique=True, index=True, nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    jobs = relationship("Job", back_populates="user")


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # File info
    original_filename = Column(String(255), nullable=False)
    pdf_s3_key = Column(String(500), nullable=False)
    audio_s3_key = Column(String(500))
    pdf_s3_url = Column(String(1000))
    audio_s3_url = Column(String(1000))

    # Processing info
    status = Column(
        create_enum_type("jobstatus", JobStatus, Base.metadata),
        default=JobStatus.pending,
    )
    progress_percentage = Column(Integer, default=0)
    error_message = Column(Text)

    # Processing options
    voice_provider = Column(
        create_enum_type("voiceprovider", VoiceProvider, Base.metadata),
        default=VoiceProvider.openai,
    )
    voice_type = Column(String(50), default="default")
    reading_speed = Column(Numeric(3, 2), default=1.0)
    include_summary = Column(Boolean, default=False)
    conversion_mode = Column(
        create_enum_type("conversionmode", ConversionMode, Base.metadata),
        default=ConversionMode.full,
    )
    estimated_cost = Column(Numeric(10, 6), default=0.0)
    chars_processed = Column(Integer, default=0)
    tokens_used = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))

    # Relationships
    user = relationship("User", back_populates="jobs")
