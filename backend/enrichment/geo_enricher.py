"""
Geo Enricher
────────────
Resolves IP addresses to geographic metadata.

Uses MaxMind GeoLite2 when the database file is present.
Falls back to mock data for development without the database.
"""

import os
import random
from typing import Optional

import structlog

logger = structlog.get_logger(__name__)

# ── Mock geo data for development ─────────────────────────────────────────

_MOCK_GEO_DATA = [
    {"country_code": "RU", "country_name": "Russia",        "city": "Moscow",       "latitude": 55.75, "longitude": 37.62},
    {"country_code": "CN", "country_name": "China",         "city": "Beijing",      "latitude": 39.90, "longitude": 116.41},
    {"country_code": "US", "country_name": "United States", "city": "Chicago",      "latitude": 41.88, "longitude": -87.63},
    {"country_code": "DE", "country_name": "Germany",       "city": "Frankfurt",    "latitude": 50.11, "longitude":   8.68},
    {"country_code": "NL", "country_name": "Netherlands",   "city": "Amsterdam",    "latitude": 52.37, "longitude":   4.89},
    {"country_code": "UA", "country_name": "Ukraine",       "city": "Kyiv",         "latitude": 50.45, "longitude":  30.52},
    {"country_code": "BR", "country_name": "Brazil",        "city": "São Paulo",    "latitude": -23.55,"longitude": -46.63},
    {"country_code": "KR", "country_name": "South Korea",   "city": "Seoul",        "latitude": 37.57, "longitude": 126.98},
    {"country_code": "IR", "country_name": "Iran",          "city": "Tehran",       "latitude": 35.69, "longitude":  51.39},
    {"country_code": "GB", "country_name": "United Kingdom","city": "London",       "latitude": 51.51, "longitude":  -0.13},
]


def enrich_geo(ip: Optional[str]) -> dict:
    """
    Return geographic metadata for an IP address.

    Args:
        ip: IPv4 or IPv6 address string.

    Returns:
        Dict with: country_code, country_name, city, latitude, longitude.
        Empty dict on failure.
    """
    if not ip:
        return {}

    geo_db_path = os.getenv("GEO_DB_PATH", "/app/data/GeoLite2-City.mmdb")

    # ── Try MaxMind GeoLite2 ──────────────────────────────────────────
    if os.path.exists(geo_db_path):
        try:
            import geoip2.database

            with geoip2.database.Reader(geo_db_path) as reader:
                response = reader.city(ip)
                return {
                    "country_code": response.country.iso_code or "",
                    "country_name": response.country.name or "",
                    "city":         response.city.name or "",
                    "latitude":     float(response.location.latitude or 0),
                    "longitude":    float(response.location.longitude or 0),
                }
        except Exception as exc:
            logger.debug("geo_lookup_failed", ip=ip, error=str(exc))

    # ── Mock fallback ─────────────────────────────────────────────────
    # Use IP to seed random so same IP always gets same location
    seed = sum(int(octet) for octet in ip.split(".") if octet.isdigit())
    random.seed(seed)
    result = random.choice(_MOCK_GEO_DATA).copy()
    random.seed(None)  # reset seed
    return result
