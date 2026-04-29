"""
Application Settings
────────────────────
All configuration loaded from environment variables.
Uses pydantic-settings for validation and type coercion.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ── Kafka ──────────────────────────────────────────────────────────
    KAFKA_BOOTSTRAP_SERVERS: str          = "kafka:29092"
    KAFKA_BOOTSTRAP_SERVERS_EXTERNAL: str = "localhost:9092"
    KAFKA_TOPIC_RAW: str                  = "iocs.raw"
    KAFKA_TOPIC_ENRICHED: str             = "iocs.enriched"
    KAFKA_TOPIC_ALERTS: str               = "alerts.critical"
    KAFKA_GROUP_ID: str                   = "threat-intel-group"

    # ── PostgreSQL ─────────────────────────────────────────────────────
    POSTGRES_HOST: str     = "postgres"
    POSTGRES_PORT: int     = 5432
    POSTGRES_DB: str       = "threatintel"
    POSTGRES_USER: str     = "threatintel"
    POSTGRES_PASSWORD: str = "changeme"

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def JDBC_URL(self) -> str:
        return (
            f"jdbc:postgresql://{self.POSTGRES_HOST}:{self.POSTGRES_PORT}"
            f"/{self.POSTGRES_DB}"
        )

    # ── FastAPI ────────────────────────────────────────────────────────
    API_HOST: str  = "0.0.0.0"
    API_PORT: int  = 8000
    API_DEBUG: bool = False

    # ── Auth ───────────────────────────────────────────────────────────
    JWT_SECRET: str         = "change_this_secret"
    JWT_ALGORITHM: str      = "HS256"
    JWT_EXPIRE_MINUTES: int = 480
    ADMIN_EMAIL: str        = "admin@threatintel.local"
    ADMIN_PASSWORD: str     = "changeme"

    # ── Spark ──────────────────────────────────────────────────────────
    SPARK_MASTER: str          = "local[*]"
    SPARK_APP_NAME: str        = "ThreatIntelPipeline"
    SPARK_CHECKPOINT_DIR: str  = "/tmp/spark-checkpoints"
    SPARK_LOG_LEVEL: str       = "WARN"

    # ── OSINT API Keys (optional) ──────────────────────────────────────
    ABUSEIPDB_API_KEY: str  = ""
    VIRUSTOTAL_API_KEY: str = ""
    OTX_API_KEY: str        = ""

    # ── Mock Feed ──────────────────────────────────────────────────────
    MOCK_FEED_ENABLED: bool         = True
    MOCK_FEED_INTERVAL_SECONDS: float = 3.0
    MOCK_FEED_BATCH_SIZE: int       = 5


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


# Singleton instance used throughout the app
settings = get_settings()
