"""
Enterprise MCP Payments Server Configuration
Environment-based settings with validation and security features.
"""

import os
from typing import List, Optional
from pydantic import Field, field_validator, ConfigDict
from pydantic_settings import BaseSettings
from pydantic.networks import AnyHttpUrl


class Settings(BaseSettings):
    """
    Enterprise MCP Payments Server Settings.
    
    All settings are loaded from environment variables with proper validation,
    defaults, and security considerations.
    """
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    # ============================================================================
    # Core Application Settings
    # ============================================================================
    
    ENVIRONMENT: str = Field("development", description="Application environment")
    DEBUG: bool = Field(False, description="Debug mode")
    APP_NAME: str = Field("mcp-payments-server", description="Application name")
    
    # MCP Server Configuration
    MCP_VERSION: str = Field("2024.1", description="MCP protocol version")
    SERVER_NAME: str = Field("enterprise-payments", description="Server name")
    SERVER_VERSION: str = Field("1.0.0", description="Server version")
    
    # Network Configuration
    HOST: str = Field("0.0.0.0", description="Server host")
    PORT: int = Field(8000, description="Server port")
    BASE_URL: str = Field("http://localhost:8000", description="Base URL of the application")
    LOG_LEVEL: str = Field("INFO", description="Logging level")
    
    # ============================================================================
    # Security Configuration
    # ============================================================================
    
    JWT_SECRET_KEY: str = Field(..., description="JWT signing secret")
    ENCRYPTION_KEY: str = Field(..., description="Data encryption key")
    API_RATE_LIMIT: str = Field("1000/hour", description="API rate limit")
    
    # CORS Settings
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:3001", "http://localhost:8000"],
        description="Allowed CORS origins"
    )
    
    # Authentication
    ENABLE_AUTHENTICATION: bool = Field(True, description="Enable JWT authentication")
    JWT_ALGORITHM: str = Field("HS256", description="JWT signing algorithm")
    JWT_EXPIRATION_HOURS: int = Field(24, description="JWT expiration in hours")
    
    # ============================================================================
    # Database Configuration
    # ============================================================================
    
    DATABASE_URL: str = Field(
        "postgresql+asyncpg://payments:payments_secure_pass@localhost:5432/payments_db",
        description="PostgreSQL database URL"
    )
    DATABASE_POOL_SIZE: int = Field(20, description="Database connection pool size")
    DATABASE_MAX_OVERFLOW: int = Field(30, description="Database max overflow connections")
    DATABASE_ECHO: bool = Field(False, description="Enable SQLAlchemy query logging")
    
    # ============================================================================
    # Redis Configuration
    # ============================================================================
    
    REDIS_URL: str = Field(
        "redis://localhost:6379/0",
        description="Redis connection URL"
    )
    REDIS_POOL_SIZE: int = Field(10, description="Redis connection pool size")
    REDIS_TTL_DEFAULT: int = Field(3600, description="Default Redis TTL in seconds")
    
    # ============================================================================
    # Message Queue Configuration
    # ============================================================================
    
    RABBITMQ_URL: str = Field(
        "amqp://payments:payments_pass@localhost:5672/",
        description="RabbitMQ connection URL"
    )
    CELERY_BROKER_URL: str = Field(
        "redis://localhost:6379/1",
        description="Celery broker URL"
    )
    CELERY_RESULT_BACKEND: str = Field(
        "redis://localhost:6379/2",
        description="Celery result backend URL"
    )
    
    # ============================================================================
    # Payment Provider Configuration
    # ============================================================================
    
    # Stripe Configuration
    STRIPE_API_KEY: Optional[str] = Field(None, description="Stripe secret API key")
    STRIPE_PUBLISHABLE_KEY: Optional[str] = Field(None, description="Stripe publishable key")
    STRIPE_WEBHOOK_SECRET: Optional[str] = Field(None, description="Stripe webhook secret")
    STRIPE_API_VERSION: str = Field("2023-10-16", description="Stripe API version")
    
    # Razorpay Configuration
    RAZORPAY_KEY_ID: Optional[str] = Field(None, description="Razorpay key ID")
    RAZORPAY_KEY_SECRET: Optional[str] = Field(None, description="Razorpay key secret")
    RAZORPAY_WEBHOOK_SECRET: Optional[str] = Field(None, description="Razorpay webhook secret")
    
    # ============================================================================
    # Monitoring & Observability
    # ============================================================================
    
    # OpenTelemetry
    OTEL_EXPORTER_OTLP_ENDPOINT: str = Field(
        "http://localhost:4317",
        description="OTLP exporter endpoint"
    )
    OTEL_SERVICE_NAME: str = Field("mcp-payments-server", description="Service name for tracing")
    
    # Sentry
    SENTRY_DSN: Optional[str] = Field(None, description="Sentry DSN for error tracking")
    SENTRY_TRACES_SAMPLE_RATE: float = Field(0.1, description="Sentry traces sample rate")
    
    # Prometheus
    PROMETHEUS_METRICS_PORT: int = Field(9090, description="Prometheus metrics port")
    
    # ============================================================================
    # Feature Flags
    # ============================================================================
    
    ENABLE_ANALYTICS: bool = Field(True, description="Enable analytics collection")
    ENABLE_AUDIT_LOGGING: bool = Field(True, description="Enable audit logging")
    ENABLE_RATE_LIMITING: bool = Field(True, description="Enable API rate limiting")
    ENABLE_METRICS: bool = Field(True, description="Enable Prometheus metrics")
    ENABLE_TRACING: bool = Field(True, description="Enable distributed tracing")
    ENABLE_PROFILING: bool = Field(False, description="Enable performance profiling")
    
    # ============================================================================
    # Business Configuration
    # ============================================================================
    
    DEFAULT_CURRENCY: str = Field("USD", description="Default currency code")
    SUPPORTED_CURRENCIES: List[str] = Field(
        default=["USD", "EUR", "GBP", "INR", "JPY"],
        description="Supported currency codes"
    )
    
    MAX_PAYMENT_AMOUNT: float = Field(100000.0, description="Maximum payment amount")
    MIN_PAYMENT_AMOUNT: float = Field(0.01, description="Minimum payment amount")
    
    # Transaction Limits
    DAILY_TRANSACTION_LIMIT: float = Field(50000.0, description="Daily transaction limit per user")
    MONTHLY_TRANSACTION_LIMIT: float = Field(500000.0, description="Monthly transaction limit per user")
    
    # Fraud Detection
    FRAUD_DETECTION_THRESHOLD: float = Field(75.0, description="Fraud risk score threshold (0-100)")
    
    # ============================================================================
    # File Upload Configuration
    # ============================================================================
    
    MAX_FILE_SIZE: int = Field(10 * 1024 * 1024, description="Max file size in bytes (10MB)")
    ALLOWED_FILE_TYPES: List[str] = Field(
        default=["pdf", "jpg", "jpeg", "png", "doc", "docx"],
        description="Allowed file extensions"
    )
    UPLOAD_PATH: str = Field("./uploads", description="File upload directory")
    
    # ============================================================================
    # Email Configuration
    # ============================================================================
    
    SMTP_HOST: Optional[str] = Field(None, description="SMTP server host")
    SMTP_PORT: int = Field(587, description="SMTP server port")
    SMTP_USERNAME: Optional[str] = Field(None, description="SMTP username")
    SMTP_PASSWORD: Optional[str] = Field(None, description="SMTP password")
    SMTP_USE_TLS: bool = Field(True, description="Use TLS for SMTP")
    
    FROM_EMAIL: str = Field(
        "noreply@payments.example.com",
        description="Default from email address"
    )
    
    # Webhook Configuration
    WEBHOOK_URL: Optional[str] = Field(None, description="Webhook notification URL")
    SLACK_WEBHOOK_URL: Optional[str] = Field(None, description="Slack webhook URL for notifications")
    
    # ============================================================================
    # Validation & Processing
    # ============================================================================
    
    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v):
        """Validate environment setting."""
        valid_envs = ["development", "staging", "production"]
        if v not in valid_envs:
            raise ValueError(f"Environment must be one of: {valid_envs}")
        return v
    
    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v):
        """Validate log level setting."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.upper()
    
    @field_validator("JWT_SECRET_KEY")
    @classmethod
    def validate_jwt_secret(cls, v):
        """Validate JWT secret key length."""
        if len(v) < 32:
            raise ValueError("JWT secret key must be at least 32 characters long")
        return v
    
    @field_validator("ENCRYPTION_KEY")
    @classmethod
    def validate_encryption_key(cls, v):
        """Validate encryption key length."""
        if len(v) < 32:
            raise ValueError("Encryption key must be at least 32 characters long")
        return v
    
    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v):
        """Validate database URL format."""
        if not v.startswith(("postgresql://", "postgresql+asyncpg://")):
            raise ValueError("Database URL must be a PostgreSQL connection string")
        return v
    
    @field_validator("REDIS_URL")
    @classmethod
    def validate_redis_url(cls, v):
        """Validate Redis URL format."""
        if not v.startswith("redis://"):
            raise ValueError("Redis URL must start with redis://")
        return v
    
    # ============================================================================
    # Computed Properties
    # ============================================================================
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT == "production"
    
    @property
    def is_staging(self) -> bool:
        """Check if running in staging environment."""
        return self.ENVIRONMENT == "staging"
    
    @property
    def database_echo(self) -> bool:
        """Should SQLAlchemy echo queries."""
        return self.DEBUG and self.is_development
    
    @property
    def cors_origins(self) -> List[str]:
        """Get CORS origins based on environment."""
        if self.is_production:
            return ["https://payments.yourdomain.com"]
        return self.ALLOWED_ORIGINS


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get global settings instance."""
    return settings
