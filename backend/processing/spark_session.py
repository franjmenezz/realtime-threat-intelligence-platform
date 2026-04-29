"""
Spark Session Factory
─────────────────────
Centralizes SparkSession creation with all required configurations
for the Threat Intelligence streaming pipeline.
"""

from pyspark.sql import SparkSession
from config.settings import settings
import structlog

logger = structlog.get_logger(__name__)


def create_spark_session(app_name: str | None = None) -> SparkSession:
    """
    Create and configure a SparkSession for the pipeline.

    Includes:
    - Kafka connector package
    - Delta Lake support
    - Optimized memory settings for streaming
    - PostgreSQL JDBC driver

    Args:
        app_name: Override the default application name.

    Returns:
        Configured SparkSession instance.
    """
    name = app_name or settings.SPARK_APP_NAME

    logger.info("creating_spark_session", app_name=name, master=settings.SPARK_MASTER)

    spark = (
        SparkSession.builder.appName(name)
        .master(settings.SPARK_MASTER)
        # ── Kafka connector ────────────────────────────────────────────
        .config(
            "spark.jars.packages",
            ",".join([
                "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1",
                "org.postgresql:postgresql:42.7.3",
            ]),
        )
        # ── Streaming micro-batch tuning ───────────────────────────────
        .config("spark.streaming.stopGracefullyOnShutdown", "true")
        .config("spark.sql.streaming.checkpointLocation", settings.SPARK_CHECKPOINT_DIR)
        .config("spark.sql.streaming.forceDeleteTempCheckpointLocation", "true")
        # ── Memory & performance ───────────────────────────────────────
        .config("spark.driver.memory", "2g")
        .config("spark.executor.memory", "2g")
        .config("spark.sql.adaptive.enabled", "true")
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
        # ── Serialization ──────────────────────────────────────────────
        .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
        # ── Logging ────────────────────────────────────────────────────
        .config("spark.eventLog.enabled", "false")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel(settings.SPARK_LOG_LEVEL)

    logger.info(
        "spark_session_created",
        version=spark.version,
        app_id=spark.sparkContext.applicationId,
    )

    return spark


def stop_spark_session(spark: SparkSession) -> None:
    """Gracefully stop the SparkSession."""
    logger.info("stopping_spark_session")
    spark.stop()
    logger.info("spark_session_stopped")
