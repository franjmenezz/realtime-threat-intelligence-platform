"""
DataFrame Schemas
─────────────────
Defines all PySpark StructType schemas used across the streaming pipeline.
Centralizing schemas prevents drift between producers and consumers.
"""

from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    FloatType,
    IntegerType,
    LongType,
    BooleanType,
    ArrayType,
    MapType,
    TimestampType,
)


# ── Raw IoC event from Kafka producer ─────────────────────────────────────
RAW_IOC_SCHEMA = StructType([
    StructField("event_id",    StringType(),    nullable=False),
    StructField("ioc_type",    StringType(),    nullable=False),  # ip, domain, hash, url
    StructField("ioc_value",   StringType(),    nullable=False),
    StructField("source",      StringType(),    nullable=True),   # abuseipdb, virustotal, mock
    StructField("confidence",  FloatType(),     nullable=True),   # 0.0 – 1.0
    StructField("tags",        ArrayType(StringType()), nullable=True),
    StructField("raw_data",    StringType(),    nullable=True),   # JSON string of original payload
    StructField("ingested_at", LongType(),      nullable=False),  # Unix timestamp millis
])


# ── Enriched IoC — output of enrichment UDFs ──────────────────────────────
ENRICHED_IOC_SCHEMA = StructType([
    # Core fields (carried over from raw)
    StructField("event_id",    StringType(),    nullable=False),
    StructField("ioc_type",    StringType(),    nullable=False),
    StructField("ioc_value",   StringType(),    nullable=False),
    StructField("source",      StringType(),    nullable=True),
    StructField("confidence",  FloatType(),     nullable=True),
    StructField("tags",        ArrayType(StringType()), nullable=True),
    StructField("ingested_at", LongType(),      nullable=False),

    # Geo enrichment
    StructField("country_code",   StringType(), nullable=True),
    StructField("country_name",   StringType(), nullable=True),
    StructField("city",           StringType(), nullable=True),
    StructField("latitude",       FloatType(),  nullable=True),
    StructField("longitude",      FloatType(),  nullable=True),

    # ASN enrichment
    StructField("asn",            StringType(), nullable=True),   # e.g. AS13335
    StructField("isp",            StringType(), nullable=True),
    StructField("org",            StringType(), nullable=True),

    # Reputation enrichment
    StructField("abuse_score",    IntegerType(), nullable=True),  # 0–100
    StructField("vt_detections",  IntegerType(), nullable=True),  # number of VT engines flagging
    StructField("vt_total",       IntegerType(), nullable=True),
    StructField("is_tor",         BooleanType(), nullable=True),
    StructField("is_vpn",         BooleanType(), nullable=True),
    StructField("is_datacenter",  BooleanType(), nullable=True),

    # ML features (computed)
    StructField("seen_count",     IntegerType(), nullable=True),  # times seen in last 24h
    StructField("first_seen",     LongType(),    nullable=True),
    StructField("last_seen",      LongType(),    nullable=True),

    # Risk scoring (filled by scorer)
    StructField("risk_score",     FloatType(),   nullable=True),  # 0.0 – 100.0
    StructField("risk_level",     StringType(),  nullable=True),  # CRITICAL/HIGH/MEDIUM/LOW/INFO
    StructField("enriched_at",    LongType(),    nullable=True),
])


# ── Alert event ───────────────────────────────────────────────────────────
ALERT_SCHEMA = StructType([
    StructField("alert_id",      StringType(),  nullable=False),
    StructField("event_id",      StringType(),  nullable=False),
    StructField("ioc_value",     StringType(),  nullable=False),
    StructField("ioc_type",      StringType(),  nullable=False),
    StructField("risk_level",    StringType(),  nullable=False),
    StructField("risk_score",    FloatType(),   nullable=False),
    StructField("rule_name",     StringType(),  nullable=True),
    StructField("description",   StringType(),  nullable=True),
    StructField("country_code",  StringType(),  nullable=True),
    StructField("created_at",    LongType(),    nullable=False),
])


# ── Kafka message envelope ─────────────────────────────────────────────────
KAFKA_VALUE_SCHEMA = StructType([
    StructField("value", StringType(), nullable=True),
])
