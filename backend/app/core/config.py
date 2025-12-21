from pydantic import field_validator
from pydantic_settings import BaseSettings
from typing import List, Optional, Any
import os


class Settings(BaseSettings):
    # Core Project Settings
    PROJECT_NAME: str = "pdf2audiobook"
    PROJECT_VERSION: str = "0.1.0"

    # Environment
    ENVIRONMENT: str = "development"  # development, staging, production
    DEBUG: bool = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Diagnostic logging for voice environment variables
        import logging
        logger = logging.getLogger(__name__)
        voice_vars = {k: v for k, v in os.environ.items() if k.startswith("GOOGLE_VOICE_")}
        if voice_vars:
            logger.info(f"Detected Google Voice Env Vars: {voice_vars}")
        else:
            logger.warning("No GOOGLE_VOICE_ environment variables detected at startup.")
    TESTING_MODE: bool = False

    # Database
    DATABASE_URL: str = "sqlite:///./dev.db"

    # Redis/Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # CORS - More restrictive defaults
    ALLOWED_HOSTS: Any = []

    # AWS S3
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    AWS_ENDPOINT_URL: Optional[str] = None
    S3_BUCKET_NAME: Optional[str] = None

    # Authentication (Clerk)
    CLERK_PEM_PUBLIC_KEY: Optional[str] = None
    CLERK_JWT_ISSUER: Optional[str] = None
    CLERK_JWT_AUDIENCE: Optional[str] = None

    # Paddle
    PADDLE_VENDOR_ID: Optional[int] = None
    PADDLE_VENDOR_AUTH_CODE: Optional[str] = None
    PADDLE_PUBLIC_KEY: Optional[str] = None
    PADDLE_ENVIRONMENT: str = "sandbox"  # sandbox or production

    # OpenAI
    OPENAI_API_KEY: Optional[str] = None

    # OpenRouter
    OPENROUTER_API_KEY: Optional[str] = None
    LLM_MODEL: str = "google/gemini-2.0-flash-001:free"

    # Google TTS Voices
    GOOGLE_VOICE_US_FEMALE_STD: str = "en-US-Wavenet-C"
    GOOGLE_VOICE_US_MALE_STD: str = "en-US-Wavenet-I"
    GOOGLE_VOICE_GB_FEMALE_STD: str = "en-GB-Wavenet-F"
    GOOGLE_VOICE_GB_MALE_STD: str = "en-GB-Wavenet-O"
    GOOGLE_VOICE_US_FEMALE_PREMIUM: str = ""
    GOOGLE_VOICE_US_MALE_PREMIUM: str = ""
    GOOGLE_VOICE_GB_FEMALE_PREMIUM: str = ""
    GOOGLE_VOICE_GB_MALE_PREMIUM: str = ""

    # Google TTS Costs (per 1M characters)
    GOOGLE_TTS_COST_WAVENET: float = 4.0
    GOOGLE_TTS_COST_CHIRP: float = 30.0

    # File upload limits
    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_FILE_TYPES: Any = ["application/pdf"]
    FREE_TIER_JOBS_LIMIT: int = 50

    # Rate limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_MINUTES: int = 1

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    @field_validator("ALLOWED_HOSTS", "ALLOWED_FILE_TYPES", mode="before")
    @classmethod
    def parse_env_list(cls, v: Any) -> List[str]:
        """Parse comma-separated strings from environment variables into lists."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    class Config:
        env_file = ".env"
        case_sensitive = False

        @classmethod
        def customize_sources(cls, init_settings, env_settings, file_secret_settings):
            """Customize settings sources with environment-specific priority."""
            return (
                init_settings,
                env_settings,  # Environment variables
                file_secret_settings,  # .env file
            )

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def fix_postgres_prefix(cls, v: Any) -> Any:
        if isinstance(v, str) and v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql://", 1)
        return v

    @field_validator("CLERK_PEM_PUBLIC_KEY", mode="before")
    @classmethod
    def fix_pem_formatting(cls, v: Any) -> Any:
        if isinstance(v, str):
            # Strip quotes and whitespace that might be added by Render/Env
            v = v.strip().strip('"').strip("'").strip()
            
            # Replace literal "\n" characters with actual newlines
            v = v.replace("\\n", "\n")
            
            # Ensure it has the headers/footers if missing
            if "-----BEGIN PUBLIC KEY-----" not in v:
                v = f"-----BEGIN PUBLIC KEY-----\n{v}\n-----END PUBLIC KEY-----"
            
            # Diagnostic info (safe)
            print(f"DEBUG: CLERK_PEM_PUBLIC_KEY structure: length={len(v)}, "
                  f"starts_with='{v[:20]}...', ends_with='...{v[-20:]}'")
        return v

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT.lower() == "development"

    @property
    def max_file_size_bytes(self) -> int:
        """Get maximum file size in bytes."""
        return self.MAX_FILE_SIZE_MB * 1024 * 1024

    def validate_production_settings(self):
        """Validate that required production settings are configured."""
        if self.is_production:
            required_settings = [
                ("DATABASE_URL", self.DATABASE_URL),
                ("SECRET_KEY", self.SECRET_KEY),
                ("CLERK_PEM_PUBLIC_KEY", self.CLERK_PEM_PUBLIC_KEY),
                ("CLERK_JWT_ISSUER", self.CLERK_JWT_ISSUER),
                ("CLERK_JWT_AUDIENCE", self.CLERK_JWT_AUDIENCE),
            ]

            missing = [name for name, value in required_settings if not value]
            if missing:
                raise ValueError(f"Missing required production settings: {', '.join(missing)}")

            # Validate SECRET_KEY is not default
            if self.SECRET_KEY == "dev-secret-key-change-in-production":
                raise ValueError("SECRET_KEY must be changed from default value in production")


    # Google Cloud Credentials
    GOOGLE_APPLICATION_CREDENTIALS_JSON: Optional[str] = None

    def setup_google_credentials(self):
        """Helper to write Google Credentials from JSON to file if provided."""
        from loguru import logger
        
        env_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        logger.info(f"Checking credentials... env_var='{env_path}'")
        
        if env_path:
            if os.path.exists(env_path):
                logger.info(f"✅ Using valid existing path: {env_path}")
                return
            else:
                logger.warning(f"⚠️ GOOGLE_APPLICATION_CREDENTIALS is set to {env_path} but FILE NOT FOUND")

        json_text = self.GOOGLE_APPLICATION_CREDENTIALS_JSON
        if json_text and json_text.strip():
             # Basic sanity check: If it doesn't start with '{', it's likely a path or junk
             if not json_text.strip().startswith("{"):
                 logger.warning(f"⚠️ GOOGLE_APPLICATION_CREDENTIALS_JSON exists but doesn't look like JSON (starts with '{json_text[:5]}...'). Skipping manual setup.")
                 return
                 
             logger.info(f"🛠 Manual setup trigger detected (JSON length: {len(json_text)})")
             cred_path = "/tmp/google_credentials.json"
             try:
                 with open(cred_path, "w") as f:
                     f.write(json_text)
                 os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cred_path
                 logger.info(f"✅ Successfully wrote Google Application Credentials to {cred_path}")
             except Exception as e:
                 logger.error(f"❌ Failed to write Google Credentials: {e}")
        else:
             logger.info("ℹ️ No Google credentials configuration detected (skipping setup)")

settings = Settings()
settings.setup_google_credentials()
