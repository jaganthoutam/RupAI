from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    mcp_server_host: str = Field("0.0.0.0", env="MCP_SERVER_HOST")
    mcp_server_port: int = Field(8000, env="MCP_SERVER_PORT")
    mcp_log_level: str = Field("INFO", env="MCP_LOG_LEVEL")

    database_url: str = Field(..., env="DATABASE_URL")
    database_pool_size: int = Field(20, env="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(30, env="DATABASE_MAX_OVERFLOW")

    redis_url: str = Field(..., env="REDIS_URL")
    redis_pool_size: int = Field(10, env="REDIS_POOL_SIZE")

    rabbitmq_url: str = Field(..., env="RABBITMQ_URL")
    rabbitmq_exchange: str = Field("payments", env="RABBITMQ_EXCHANGE")

    jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")
    encryption_key: str = Field(..., env="ENCRYPTION_KEY")
    api_rate_limit: str = Field("1000/hour", env="API_RATE_LIMIT")

    stripe_api_key: str = Field(..., env="STRIPE_API_KEY")
    stripe_webhook_secret: str = Field(..., env="STRIPE_WEBHOOK_SECRET")
    razorpay_key_id: str = Field(..., env="RAZORPAY_KEY_ID")
    razorpay_key_secret: str = Field(..., env="RAZORPAY_KEY_SECRET")

    otel_exporter_otlp_endpoint: str = Field("http://jaeger:4317", env="OTEL_EXPORTER_OTLP_ENDPOINT")
    prometheus_metrics_port: int = Field(9090, env="PROMETHEUS_METRICS_PORT")

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
