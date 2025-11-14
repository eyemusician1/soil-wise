"""Validation helpers for soil inputs."""

def validate_ph(value) -> bool:
    try:
        v = float(value)
    except Exception:
        return False
    return 0.0 <= v <= 14.0


def validate_non_negative(value) -> bool:
    try:
        v = float(value)
    except Exception:
        return False
    return v >= 0.0
