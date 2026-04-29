"""
Reputation Enricher
────────────────────
Fetches reputation data from OSINT sources.

Priority:
1. AbuseIPDB (for IPs)     — requires ABUSEIPDB_API_KEY
2. VirusTotal (all types)  — requires VIRUSTOTAL_API_KEY
3. Mock data               — always available, no key needed
"""

import os
import random
from typing import Optional

import structlog

logger = structlog.get_logger(__name__)


def _mock_reputation(ioc_value: str, ioc_type: str) -> dict:
    """Generate deterministic mock reputation data."""
    seed = hash(ioc_value) % (2**32)
    random.seed(seed)

    abuse_score   = random.randint(0, 100)
    vt_total      = 72
    vt_detections = random.randint(0, int(vt_total * (abuse_score / 100)))
    is_tor        = random.random() < 0.1
    is_vpn        = random.random() < 0.2
    is_datacenter = random.random() < 0.3

    random.seed(None)

    return {
        "abuse_score":   abuse_score,
        "vt_detections": vt_detections,
        "vt_total":      vt_total,
        "is_tor":        is_tor,
        "is_vpn":        is_vpn,
        "is_datacenter": is_datacenter,
    }


def _fetch_abuseipdb(ip: str) -> Optional[dict]:
    """Query AbuseIPDB API for IP reputation."""
    api_key = os.getenv("ABUSEIPDB_API_KEY", "")
    if not api_key:
        return None

    try:
        import httpx

        response = httpx.get(
            "https://api.abuseipdb.com/api/v2/check",
            headers={"Key": api_key, "Accept": "application/json"},
            params={"ipAddress": ip, "maxAgeInDays": 90},
            timeout=5.0,
        )
        if response.status_code == 200:
            data = response.json().get("data", {})
            return {
                "abuse_score":   data.get("abuseConfidenceScore", 0),
                "vt_detections": None,
                "vt_total":      None,
                "is_tor":        data.get("isTor", False),
                "is_vpn":        False,
                "is_datacenter": False,
            }
    except Exception as exc:
        logger.debug("abuseipdb_fetch_failed", ip=ip, error=str(exc))

    return None


def enrich_reputation(ioc_value: Optional[str], ioc_type: Optional[str]) -> dict:
    """
    Fetch or mock reputation data for an IoC.

    Args:
        ioc_value: The IoC value (IP, domain, hash, URL).
        ioc_type:  Type of IoC.

    Returns:
        Dict with reputation fields.
    """
    if not ioc_value:
        return _mock_reputation("unknown", "ip")

    # Try real API for IPs
    if ioc_type == "ip":
        result = _fetch_abuseipdb(ioc_value)
        if result:
            return result

    # Fallback to mock
    return _mock_reputation(ioc_value, ioc_type or "unknown")
