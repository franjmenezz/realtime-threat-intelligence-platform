"""
Risk Scorer
───────────
Computes a 0–100 risk score for each IoC based on enrichment signals.

In production this would load a trained PySpark MLlib model (Random Forest).
For the initial version, a deterministic weighted formula is used so the
pipeline works without a trained model artifact.

The training script (train_model.py) generates a proper MLlib model once
enough labeled data has been collected in PostgreSQL.
"""

import math
from typing import Optional


# ── Risk level thresholds ─────────────────────────────────────────────────

RISK_THRESHOLDS = {
    "CRITICAL": 80.0,
    "HIGH":     60.0,
    "MEDIUM":   40.0,
    "LOW":      20.0,
    "INFO":      0.0,
}


def compute_risk_score(
    abuse_score:   Optional[int],
    vt_detections: Optional[int],
    vt_total:      Optional[int],
    confidence:    Optional[float],
    is_tor:        Optional[bool],
    is_vpn:        Optional[bool],
) -> float:
    """
    Weighted risk score computation.

    Args:
        abuse_score:   AbuseIPDB confidence score (0–100).
        vt_detections: Number of VirusTotal engines that flagged the IoC.
        vt_total:      Total number of VirusTotal engines that scanned it.
        confidence:    Source confidence (0.0–1.0).
        is_tor:        Whether the IP is a known Tor exit node.
        is_vpn:        Whether the IP belongs to a VPN provider.

    Returns:
        Risk score between 0.0 and 100.0.
    """
    score = 0.0

    # ── AbuseIPDB score (weight: 35%) ─────────────────────────────────
    if abuse_score is not None:
        score += (abuse_score / 100.0) * 35.0

    # ── VirusTotal detection ratio (weight: 35%) ──────────────────────
    if vt_detections is not None and vt_total and vt_total > 0:
        vt_ratio = vt_detections / vt_total
        score += vt_ratio * 35.0

    # ── Source confidence (weight: 15%) ───────────────────────────────
    if confidence is not None:
        score += confidence * 15.0

    # ── Behavioral flags (weight: 15%) ────────────────────────────────
    flag_score = 0.0
    if is_tor:
        flag_score += 8.0
    if is_vpn:
        flag_score += 7.0
    score += min(flag_score, 15.0)

    return round(min(max(score, 0.0), 100.0), 2)


def risk_level_from_score(score: Optional[float]) -> str:
    """
    Map a numeric risk score to a named severity level.

    Args:
        score: Risk score between 0.0 and 100.0.

    Returns:
        One of: CRITICAL, HIGH, MEDIUM, LOW, INFO
    """
    if score is None:
        return "INFO"

    for level, threshold in RISK_THRESHOLDS.items():
        if score >= threshold:
            return level

    return "INFO"
