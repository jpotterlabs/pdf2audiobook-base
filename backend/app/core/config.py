from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional, Any
import os
from loguru import logger


class Settings(BaseSettings):
    # Core Project Settings
    PROJECT_NAME: str = "pdf2audiobook"
    PROJECT_VERSION: str = "0.1.0"

    # Environment
    ENVIRONMENT: str = "development"  # development, staging, production
    DEBUG: bool = False
    
    # Admin
    ADMIN_EMAIL: Optional[str] = None


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

    # Frontend URLs for CORS
    FRONTEND_URL: str = "http://localhost:3000"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        logger.info("🚀 Loading Configuration")

        # CORS
        if self.FRONTEND_URL and self.FRONTEND_URL not in self.ALLOWED_HOSTS:
            if isinstance(self.ALLOWED_HOSTS, list):
                self.ALLOWED_HOSTS.append(self.FRONTEND_URL)

        from urllib.parse import urlparse
        parsed = urlparse(self.REDIS_URL)
        port_segment = f":{parsed.port}" if parsed.port is not None else ""
        masked_url = f"{parsed.scheme}://{parsed.hostname}{port_segment}{parsed.path}"
        logger.info(f"Using Redis URL: {masked_url}")

        # Diagnostic logging for voice environment variables
        voice_vars = {k: v for k, v in os.environ.items() if k.startswith("GOOGLE_VOICE_")}
        if voice_vars:
            logger.info(f"Detected Google Voice Env Vars: {voice_vars}")
        else:
            logger.warning("No GOOGLE_VOICE_ environment variables detected at startup.")

    # OpenAI
    OPENAI_API_KEY: Optional[str] = None

    # OpenRouter
    OPENROUTER_API_KEY: Optional[str] = None
    LLM_MODEL: str = "google/gemini-2.0-flash-001:free"

    # Local / Custom OpenAI TTS
    OPENAI_BASE_URL: Optional[str] = None
    OPENAI_TTS_MODEL: str = "tts-1"
    
    model_config = SettingsConfigDict(
        env_file=(".env",), 
        extra="ignore",
        case_sensitive=True
    )

    # Google TTS Voices
    GOOGLE_VOICE_US_FEMALE_STD: str = "en-US-Wavenet-C"
    GOOGLE_VOICE_US_MALE_STD: str = "en-US-Wavenet-I"
    GOOGLE_VOICE_GB_FEMALE_STD: str = "en-GB-Wavenet-F"
    GOOGLE_VOICE_GB_MALE_STD: str = "en-GB-Wavenet-O"
    GOOGLE_VOICE_US_FEMALE_PREMIUM: str = "en-US-Studio-O"
    GOOGLE_VOICE_US_MALE_PREMIUM: str = "en-US-Studio-Q"
    GOOGLE_VOICE_GB_FEMALE_PREMIUM: str = "en-GB-Studio-C"
    GOOGLE_VOICE_GB_MALE_PREMIUM: str = "en-GB-Studio-B"

    # Google TTS Costs (per 1M characters)
    GOOGLE_TTS_COST_STANDARD: float = 4.0
    GOOGLE_TTS_COST_PREMIUM: float = 30.0

    # LLM Costs (per 1k tokens - approximate defaults for Flash 2.0/1.5)
    LLM_COST_INPUT_PER_1K: float = 0.0001
    LLM_COST_OUTPUT_PER_1K: float = 0.0004

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



    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def fix_postgres_prefix(cls, v: Any) -> Any:
        if isinstance(v, str) and v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql://", 1)
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
