"""
models.py — Legacy ORM models (DEPRECATED).
The active ORM models are defined in database.py.
These Pydantic-style enum definitions are kept for reference only.
"""
import enum


class ProvenanceType(enum.Enum):
    """Provenance classification per record — used across the system."""
    REAL = "REAL"
    DERIVED_FROM_REAL = "DERIVED_FROM_REAL"
    MODEL_OUTPUT = "MODEL_OUTPUT"
    USER_REPORTED = "USER_REPORTED"
    UNKNOWN = "UNKNOWN"


class ShelterStatus(enum.Enum):
    """Shelter state machine: CANDIDATE → ACTIVE / FULL / CLOSED."""
    CANDIDATE = "CANDIDATE"
    ACTIVE = "ACTIVE"
    FULL = "FULL"
    CLOSED = "CLOSED"
