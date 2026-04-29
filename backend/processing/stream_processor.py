"""
Stream Processor
────────────────
Core PySpark Structured Streaming pipeline.

Flow:
  Kafka (iocs.raw)
    → deserialize JSON
    → enrich (geo, ASN, reputation)
    → ML risk scoring
    → write to PostgreSQL
    → forward CRITICAL alerts to Kafka (alerts.critical)

Run:
    python -m processing.stream_processor
"""

import json
import signal
import sys
from typing import Iterator

import structlog
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StringType, FloatType, IntegerType, BooleanType

from config.settings import settings
from processing.spark_session import create_spark_session, stop_spark_session
from processing.schemas import RAW_IOC_SCHEMA, ENRICHED_IOC_SCHEMA
from enrichment.geo_enricher import enrich_geo
from enrichment.asn_enricher import enrich_asn
from enrichment.reputation import enrich_reputation
from scoring.scorer import compute_risk_score, risk_level_from_score

logger = structlog.get_logger(__name__)

# ── UDF registrations ─────────────────────────────────────────────────────

_enrich_geo_udf = F.udf(
    lambda ip: json.dumps(enrich_geo(ip)) if ip else None,
    StringType(),
)

_enrich_asn_udf = F.udf(
    lambda ip: json.dumps(enrich_asn(ip)) if ip else None,
    StringType(),
)

_enrich_reputation_udf = F.udf(
    lambda value, ioc_type: json.dumps(enrich_reputation(value, ioc_type)),
    StringType(),
)

_risk_score_udf = F.udf(compute_risk_score, FloatType())
_risk_level_udf = F.udf(risk_level_from_score, StringType())


# ── Pipeline functions ────────────────────────────────────────────────────

def read_kafka_stream(spark: SparkSession) -> DataFrame:
    """Subscribe to the raw IoC Kafka topic and parse JSON messages."""
    logger.info("connecting_kafka", topic=settings.KAFKA_TOPIC_RAW)

    raw_df = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", settings.KAFKA_BOOTSTRAP_SERVERS)
        .option("subscribe", settings.KAFKA_TOPIC_RAW)
        .option("startingOffsets", "latest")
        .option("failOnDataLoss", "false")
        .option("maxOffsetsPerTrigger", 1000)
        .load()
    )

    # Kafka value is binary — cast to string then parse JSON
    parsed_df = raw_df.select(
        F.from_json(
            F.col("value").cast("string"),
            RAW_IOC_SCHEMA,
        ).alias("data"),
        F.col("timestamp").alias("kafka_timestamp"),
    ).select("data.*", "kafka_timestamp")

    return parsed_df


def enrich_stream(df: DataFrame) -> DataFrame:
    """
    Apply enrichment UDFs to each IoC row.

    For IP-type IoCs: geo lookup + ASN lookup + reputation.
    For non-IP types (domain, hash, url): reputation only.
    """
    logger.info("applying_enrichment_udfs")

    enriched = df

    # Geo & ASN only make sense for IP addresses
    enriched = enriched.withColumn(
        "_geo_json",
        F.when(
            F.col("ioc_type") == "ip",
            _enrich_geo_udf(F.col("ioc_value")),
        ).otherwise(F.lit(None)),
    )

    enriched = enriched.withColumn(
        "_asn_json",
        F.when(
            F.col("ioc_type") == "ip",
            _enrich_asn_udf(F.col("ioc_value")),
        ).otherwise(F.lit(None)),
    )

    enriched = enriched.withColumn(
        "_rep_json",
        _enrich_reputation_udf(F.col("ioc_value"), F.col("ioc_type")),
    )

    # ── Unpack geo JSON ──────────────────────────────────────────────────
    enriched = (
        enriched
        .withColumn("country_code",  F.get_json_object(F.col("_geo_json"), "$.country_code"))
        .withColumn("country_name",  F.get_json_object(F.col("_geo_json"), "$.country_name"))
        .withColumn("city",          F.get_json_object(F.col("_geo_json"), "$.city"))
        .withColumn("latitude",      F.get_json_object(F.col("_geo_json"), "$.latitude").cast(FloatType()))
        .withColumn("longitude",     F.get_json_object(F.col("_geo_json"), "$.longitude").cast(FloatType()))
    )

    # ── Unpack ASN JSON ──────────────────────────────────────────────────
    enriched = (
        enriched
        .withColumn("asn", F.get_json_object(F.col("_asn_json"), "$.asn"))
        .withColumn("isp", F.get_json_object(F.col("_asn_json"), "$.isp"))
        .withColumn("org", F.get_json_object(F.col("_asn_json"), "$.org"))
    )

    # ── Unpack reputation JSON ───────────────────────────────────────────
    enriched = (
        enriched
        .withColumn("abuse_score",   F.get_json_object(F.col("_rep_json"), "$.abuse_score").cast(IntegerType()))
        .withColumn("vt_detections", F.get_json_object(F.col("_rep_json"), "$.vt_detections").cast(IntegerType()))
        .withColumn("vt_total",      F.get_json_object(F.col("_rep_json"), "$.vt_total").cast(IntegerType()))
        .withColumn("is_tor",        F.get_json_object(F.col("_rep_json"), "$.is_tor").cast(BooleanType()))
        .withColumn("is_vpn",        F.get_json_object(F.col("_rep_json"), "$.is_vpn").cast(BooleanType()))
        .withColumn("is_datacenter", F.get_json_object(F.col("_rep_json"), "$.is_datacenter").cast(BooleanType()))
    )

    # Drop intermediate JSON columns
    enriched = enriched.drop("_geo_json", "_asn_json", "_rep_json")

    return enriched


def score_stream(df: DataFrame) -> DataFrame:
    """Apply ML risk scoring to enriched IoCs."""
    scored = (
        df
        .withColumn(
            "risk_score",
            _risk_score_udf(
                F.col("abuse_score"),
                F.col("vt_detections"),
                F.col("vt_total"),
                F.col("confidence"),
                F.col("is_tor"),
                F.col("is_vpn"),
            ),
        )
        .withColumn("risk_level", _risk_level_udf(F.col("risk_score")))
        .withColumn("enriched_at", F.unix_timestamp() * 1000)
    )
    return scored


def write_to_postgres(df: DataFrame, batch_id: int) -> None:
    """
    Write each micro-batch to PostgreSQL.
    Uses foreachBatch for full JDBC control.
    """
    count = df.count()
    logger.info("writing_batch_postgres", batch_id=batch_id, row_count=count)

    if count == 0:
        return

    jdbc_url = (
        f"jdbc:postgresql://{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}"
        f"/{settings.POSTGRES_DB}"
    )

    df.write.format("jdbc").options(
        url=jdbc_url,
        dbtable="iocs",
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        driver="org.postgresql.Driver",
    ).mode("append").save()

    # Forward CRITICAL alerts to dedicated Kafka topic
    critical_df = df.filter(F.col("risk_level") == "CRITICAL")
    critical_count = critical_df.count()

    if critical_count > 0:
        logger.warning("critical_iocs_detected", count=critical_count)
        alert_df = critical_df.select(
            F.col("event_id").alias("key"),
            F.to_json(F.struct("*")).alias("value"),
        )
        alert_df.write.format("kafka").options(
            **{
                "kafka.bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
                "topic": settings.KAFKA_TOPIC_ALERTS,
            }
        ).save()


def run_pipeline(spark: SparkSession) -> None:
    """Build and start the full streaming pipeline."""
    logger.info("starting_pipeline")

    raw_stream     = read_kafka_stream(spark)
    enriched_stream = enrich_stream(raw_stream)
    scored_stream   = score_stream(enriched_stream)

    query = (
        scored_stream.writeStream
        .foreachBatch(write_to_postgres)
        .outputMode("append")
        .option("checkpointLocation", f"{settings.SPARK_CHECKPOINT_DIR}/iocs")
        .trigger(processingTime="5 seconds")
        .start()
    )

    logger.info("pipeline_running", query_id=query.id)
    query.awaitTermination()


# ── Entry point ──────────────────────────────────────────────────────────

def main() -> None:
    spark = create_spark_session()

    def _shutdown(sig, frame):
        logger.info("shutdown_signal_received")
        stop_spark_session(spark)
        sys.exit(0)

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    try:
        run_pipeline(spark)
    except Exception as exc:
        logger.exception("pipeline_crashed", error=str(exc))
        stop_spark_session(spark)
        sys.exit(1)


if __name__ == "__main__":
    main()
