"""
Central application configuration.
All environment-dependent values live here — never hardcode secrets or
environment-specific values elsewhere in the codebase.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    APP_NAME: str = "JanSwasthya AI"
    ENVIRONMENT: str = "development"
    API_V1_PREFIX: str = "/api/v1"

    # Security
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    DATABASE_URL: str  # postgresql://user:pass@host:5432/dbname
    REDIS_URL: str = "redis://localhost:6379/0"

    # Vector DB
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_COLLECTION: str = "health_knowledge_base"

    # AI / LLM
    LLM_PROVIDER: str = "local"  # local | openai_compatible
    LLM_MODEL_NAME: str = "mistral-7b-instruct"
    LLM_API_BASE: str | None = None
    LLM_API_KEY: str | None = None
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"

    # RAG guardrails
    RAG_MIN_CONFIDENCE: float = 0.55
    RAG_TOP_K: int = 5

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 30

        # Email / OTP
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    SMTP_FROM: str
    OTP_EXPIRE_SECONDS: int = 300
    OTP_MAX_ATTEMPTS: int = 5

    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]


settings = Settings()
