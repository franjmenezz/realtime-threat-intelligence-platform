"""
Mock IoC Feed Generator
───────────────────────
Simulates realistic OSINT threat intelligence feeds for development.
Produces events to Kafka without requiring real API keys.

Run:
    python -m ingestion.mocks.feed_generator
"""

import json
import random
import time
import uuid
from datetime import datetime, timezone
from typing import Any

import structlog
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

from config.settings import settings

logger = structlog.get_logger(__name__)

# ── Realistic mock data pools ─────────────────────────────────────────────

MALICIOUS_IPS = [
    "185.220.101.47",  # Known Tor exit node
    "45.142.212.100",  # C2 server
    "91.108.4.1",
    "193.32.162.50",
    "194.165.16.11",
    "5.188.206.201",
    "103.75.190.100",
    "198.98.53.202",
    "178.128.23.9",
    "159.65.121.211",
]

MALICIOUS_DOMAINS = [
    "update-service-cdn.com",
    "secure-login-portal.net",
    "cdn-analytics-tracker.org",
    "microsoft-support-help.com",
    "paypal-security-alert.net",
    "dropbox-shared-file.info",
    "google-docs-viewer.xyz",
    "amazon-order-confirm.co",
    "steam-trade-offer.ru",
    "adobe-flash-update.pw",
]

MALICIOUS_HASHES = [
    "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "a87ff679a2f3e71d9181a67b7542122c",
    "d8e8fca2dc0f896fd7cb4cb0031ba249",
    "7215ee9c7d9dc229d2921a40e899ec5f",
    "aab3238922bcc25a6f606eb525ffdc56",
    "9bf31c7ff062936a96d3c8bd1f8f2ff3",
    "c4ca4238a0b923820dcc509a6f75849b",
    "eccbc87e4b5ce2fe28308fd9f2a7baf3",
]

MALICIOUS_URLS = [
    "http://185.220.101.47/payload.exe",
    "https://update-service-cdn.com/install/setup.msi",
    "http://91.108.4.1:8080/c2/beacon",
    "https://secure-login-portal.net/admin/login.php",
    "http://cdn-analytics-tracker.org/js/track.js",
]

SOURCES = ["abuseipdb", "virustotal", "alienvault_otx", "feodo_tracker", "urlhaus"]

TAGS_POOL = [
    "malware", "ransomware", "c2", "phishing", "botnet",
    "tor-exit-node", "scanner", "brute-force", "ddos",
    "cryptominer", "trojan", "spam", "exploit-kit",
]

IOC_TYPES = {
    "ip": MALICIOUS_IPS,
    "domain": MALICIOUS_DOMAINS,
    "hash": MALICIOUS_HASHES,
    "url": MALICIOUS_URLS,
}


def generate_ioc_event() -> dict[str, Any]:
    """Generate a single realistic IoC event."""
    ioc_type  = random.choice(list(IOC_TYPES.keys()))
    ioc_value = random.choice(IOC_TYPES[ioc_type])

    # Add slight variation to simulate different sources seeing the same IoC
    if ioc_type == "ip":
        # Occasionally generate random IPs too
        if random.random() < 0.3:
            ioc_value = ".".join(str(random.randint(1, 254)) for _ in range(4))

    tags   = random.sample(TAGS_POOL, k=random.randint(1, 4))
    source = random.choice(SOURCES)

    return {
        "event_id":   str(uuid.uuid4()),
        "ioc_type":   ioc_type,
        "ioc_value":  ioc_value,
        "source":     source,
        "confidence": round(random.uniform(0.4, 1.0), 2),
        "tags":       tags,
        "raw_data":   json.dumps({
            "reporter": source,
            "reported_at": datetime.now(timezone.utc).isoformat(),
            "categories": tags,
        }),
        "ingested_at": int(time.time() * 1000),
    }


def create_producer(retries: int = 10, delay: int = 5) -> KafkaProducer:
    """Create a Kafka producer with retry logic for Docker startup."""
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
            logger.warning(
                "kafka_not_ready",
                attempt=attempt,
                retrying_in_seconds=delay,
            )
            time.sleep(delay)

    raise RuntimeError("Could not connect to Kafka after multiple retries.")


def run(
    interval: float = settings.MOCK_FEED_INTERVAL_SECONDS,
    batch_size: int  = settings.MOCK_FEED_BATCH_SIZE,
) -> None:
    """
    Continuously produce mock IoC events to Kafka.

    Args:
        interval:   Seconds between each batch.
        batch_size: Number of events per batch.
    """
    logger.info(
        "mock_feed_starting",
        topic=settings.KAFKA_TOPIC_RAW,
        interval=interval,
        batch_size=batch_size,
    )

    producer = create_producer()
    total_sent = 0

    try:
        while True:
            batch = [generate_ioc_event() for _ in range(batch_size)]

            for event in batch:
                producer.send(
                    topic=settings.KAFKA_TOPIC_RAW,
                    key=event["event_id"],
                    value=event,
                )
                total_sent += 1

            producer.flush()

            logger.info(
                "batch_sent",
                batch_size=len(batch),
                total_sent=total_sent,
                types={e["ioc_type"] for e in batch},
            )

            time.sleep(interval)

    except KeyboardInterrupt:
        logger.info("mock_feed_stopped", total_sent=total_sent)
    finally:
        producer.close()


if __name__ == "__main__":
    run()
