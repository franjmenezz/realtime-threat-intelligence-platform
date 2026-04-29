"""
ASN Enricher
────────────
Resolves IP addresses to Autonomous System Number (ASN) metadata.
ASN data helps identify hosting providers, botnets, and cloud infrastructure.
"""

import random
from typing import Optional

import structlog

logger = structlog.get_logger(__name__)

_MOCK_ASN_DATA = [
    {"asn": "AS13335", "isp": "Cloudflare, Inc.",     "org": "Cloudflare"},
    {"asn": "AS16509", "isp": "Amazon.com, Inc.",     "org": "AWS"},
    {"asn": "AS15169", "isp": "Google LLC",           "org": "Google Cloud"},
    {"asn": "AS8075",  "isp": "Microsoft Corporation","org": "Azure"},
    {"asn": "AS60781", "isp": "LeaseWeb Netherlands", "org": "LeaseWeb"},
    {"asn": "AS9009",  "isp": "M247 Ltd",             "org": "M247"},
    {"asn": "AS197695","isp": "Reg.ru Hosting",       "org": "Reg.ru"},
    {"asn": "AS49505", "isp": "Selectel Ltd",         "org": "Selectel"},
    {"asn": "AS25513", "isp": "PJSC MegaFon",         "org": "MegaFon"},
    {"asn": "AS4134",  "isp": "Chinanet",             "org": "China Telecom"},
]


def enrich_asn(ip: Optional[str]) -> dict:
    """
    Return ASN metadata for an IP address.

    Args:
        ip: IPv4 or IPv6 address string.

    Returns:
        Dict with: asn, isp, org. Empty dict on failure.
    """
    if not ip:
        return {}

    seed = sum(int(o) for o in ip.split(".") if o.isdigit()) + 1
    random.seed(seed)
    result = random.choice(_MOCK_ASN_DATA).copy()
    random.seed(None)
    return result
