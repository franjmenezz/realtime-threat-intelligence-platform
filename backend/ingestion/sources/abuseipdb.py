"""
AbuseIPDB Source Producer
─────────────────────────
Fetches recently reported malicious IPs from AbuseIPDB
and produces them to Kafka as IoC events.

Requires: ABUSEIPDB_API_KEY en el .env
"""

import json
import time
import uuid
from datetime import datetime, timezone
from typing import Any

import httpx
import structlog
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

from config.settings import settings

logger = structlog.get_logger(__name__)


def _fetch_blacklist(limit: int = 100) -> list[dict]:
    """
    Fetch the AbuseIPDB blacklist (IPs con score >= 90).
    Devuelve lista de entradas o lista vacía si falla.
    """
    api_key = settings.ABUSEIPDB_API_KEY
    if not api_key:
        logger.warning("abuseipdb_key_missing")
        return []

    try:
        response = httpx.get(
            "https://api.abuseipdb.com/api/v2/blacklist",
            headers={"Key": api_key, "Accept": "application/json"},
            params={
                "confidenceMinimum": 90,
                "limit": limit,
            },
            timeout=10.0,
        )
        if response.status_code == 200:
            return response.json().get("data", [])
        elif response.status_code == 429:
            logger.warning("abuseipdb_rate_limited")
        else:
            logger.warning("abuseipdb_unexpected_status",
                           status=response.status_code)
    except Exception as exc:
        logger.error("abuseipdb_fetch_error", error=str(exc))

    return []


def _to_ioc_event(entry: dict[str, Any]) -> dict[str, Any]:
    """
    Convierte una entrada del blacklist de AbuseIPDB
    al formato estándar de IoC que usa el pipeline.
    """
    ip = entry.get("ipAddress", "")
    score = entry.get("abuseConfidenceScore", 0)

    # Inferir tags desde el score
    tags = ["abuseipdb"]
    if score >= 90:
        tags.append("high-confidence")
    if entry.get("isTor", False):
        tags.append("tor-exit-node")
    if entry.get("usageType") in ("VPN Service",):
        tags.append("vpn")
    if entry.get("usageType") == "Hosting/Data Center":
        tags.append("datacenter")

    return {
        "event_id":   str(uuid.uuid4()),
        "ioc_type":   "ip",
        "ioc_value":  ip,
        "source":     "abuseipdb",
        "confidence": round(score / 100.0, 2),
        "tags":       tags,
        "raw_data":   json.dumps({
            "reporter":    "abuseipdb",
            "reported_at": datetime.now(timezone.utc).isoformat(),
            "categories":  tags,
            "country":     entry.get("countryCode", ""),
            "usage_type":  entry.get("usageType", ""),
            "abuse_score": score,
        }),
        "ingested_at": int(time.time() * 1000),
    }


def _create_producer(retries: int = 10, delay: int = 5) -> KafkaProducer:
    """Crea un KafkaProducer con reintentos para el arranque de Docker."""
    for attempt in range(1, retries + 1):
        try:
            producer = KafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS_EXTERNAL,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                key_serializer=lambda k: k.encode("utf-8") if k else None,
                acks="all",
                retries=3,
                compression_type="gzip",
            )
            logger.info("kafka_producer_connected")
            return producer
        except NoBrokersAvailable:
            logger.warning("kafka_not_ready", attempt=attempt,
                           retrying_in_seconds=delay)
            time.sleep(delay)

    raise RuntimeError("No se pudo conectar a Kafka tras varios reintentos.")


def run(interval_minutes: int = 60) -> None:
    """
    Fetch el blacklist de AbuseIPDB cada `interval_minutes` minutos
    y produce los eventos a Kafka.

    El plan gratuito permite 1.000 req/día, así que con 1 fetch/hora
    usamos solo 24 de esas 1.000 peticiones diarias.
    """
    logger.info("abuseipdb_producer_starting",
                interval_minutes=interval_minutes)

    producer = _create_producer()

    try:
        while True:
            entries = _fetch_blacklist(limit=100)
            if entries:
                events = [_to_ioc_event(e) for e in entries]
                for event in events:
                    producer.send(
                        topic=settings.KAFKA_TOPIC_RAW,
                        key=event["event_id"],
                        value=event,
                    )
                producer.flush()
                logger.info("abuseipdb_batch_sent", count=len(events))
            else:
                logger.info("abuseipdb_no_data_fetched")

            time.sleep(interval_minutes * 60)

    except KeyboardInterrupt:
        logger.info("abuseipdb_producer_stopped")
    finally:
        producer.close()


if __name__ == "__main__":
    run()