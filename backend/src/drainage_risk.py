"""
drainage_risk.py — Threshold functions for drainage and reservoir status.
Source: KSNDMC operational guidelines.
"""

def drainage_level(score: float) -> str:
    """Classify drainage risk from composite drainage score (0-100)."""
    if score >= 70:
        return "High"
    elif score >= 40:
        return "Medium"
    return "Low"

def reservoir_status(storage_percent: float) -> str:
    """Classify reservoir pressure from storage percentage."""
    if storage_percent >= 85:
        return "Critical"
    elif storage_percent >= 65:
        return "High"
    elif storage_percent >= 40:
        return "Moderate"
    return "Normal"
