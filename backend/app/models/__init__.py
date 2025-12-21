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
    if os.getenv("ENVIRONMENT") == "production":
        # In production, we still use create_type=True because migrations are idempotent (DROP TYPE IF EXISTS)
        # and this ensures the app can start even if migrations are slightly out of sync.
        return Enum(values, name=name, create_type=True)
    else:
        # In development, create ENUM types automatically
        return Enum(values, name=name, create_type=True)


class SubscriptionTier(str, enum.Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class JobStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class VoiceProvider(str, enum.Enum):
    OPENAI = "openai"
    GOOGLE = "google"
    AWS_POLLY = "aws_polly"
    AZURE = "azure"
    ELEVEN_LABS = "eleven_labs"


class ProductType(str, enum.Enum):
    SUBSCRIPTION = "subscription"
    ONE_TIME = "one_time"


class ConversionMode(str, enum.Enum):
    full = "full"
    summary = "summary"
    explanation = "explanation"
    summary_explanation = "summary_explanation"  # Deprecated soon but keeping for compatibility


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    auth_provider_id = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))

    # Subscription info
    subscription_tier = Column(
        create_enum_type("subscriptiontier", SubscriptionTier, Base.metadata),
        default=SubscriptionTier.FREE,
    )
    paddle_customer_id = Column(String(255))
    one_time_credits = Column(Integer, default=0)
    monthly_credits_used = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    jobs = relationship("Job", back_populates="user")
    subscriptions = relationship("Subscription", back_populates="user")


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
        default=JobStatus.PENDING,
    )
    progress_percentage = Column(Integer, default=0)
    error_message = Column(Text)

    # Processing options
    voice_provider = Column(
        create_enum_type("voiceprovider", VoiceProvider, Base.metadata),
        default=VoiceProvider.OPENAI,
    )
    voice_type = Column(String(50), default="default")
    reading_speed = Column(Numeric(3, 2), default=1.0)
    include_summary = Column(Boolean, default=False)
    conversion_mode = Column(
        create_enum_type("conversionmode", ConversionMode, Base.metadata),
        default=ConversionMode.full,
    )
    estimated_cost = Column(Numeric(10, 6), default=0.0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))

    # Relationships
    user = relationship("User", back_populates="jobs")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    paddle_product_id = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)

    # Pricing
    price = Column(Numeric(10, 2))
    currency = Column(String(3), default="USD")

    # Credits/Tier info
    credits_included = Column(Integer)
    subscription_tier = Column(
        create_enum_type("subscriptiontier", SubscriptionTier, Base.metadata)
    )

    # Status
    is_active = Column(Boolean, default=True)
    # Processing type with safe ENUM handling
    type = Column(
        create_enum_type("producttype", ProductType, Base.metadata), nullable=False
    )

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    subscriptions = relationship("Subscription", back_populates="product")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    # Paddle info
    paddle_subscription_id = Column(String(255), unique=True)
    status = Column(String(50), default="active")

    # Billing
    next_billing_date = Column(DateTime(timezone=True))
    cancelled_at = Column(DateTime(timezone=True))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="subscriptions")
    product = relationship("Product", back_populates="subscriptions")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"))

    # Paddle info
    paddle_transaction_id = Column(String(255), unique=True, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="USD")
    status = Column(String(50), default="completed")

    # Credits applied
    credits_added = Column(Integer)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User")
    product = relationship("Product")
