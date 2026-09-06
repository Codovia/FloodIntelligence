from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey
from geoalchemy2 import Geometry
from .database import Base
import enum
import datetime

class ProvenanceType(enum.Enum):
    REAL = "REAL"
    DERIVED_FROM_REAL = "DERIVED_FROM_REAL"
    MODEL_OUTPUT = "MODEL_OUTPUT"
    USER_REPORTED = "USER_REPORTED"
    UNKNOWN = "UNKNOWN"

class ShelterStatus(enum.Enum):
    CANDIDATE = "CANDIDATE"
    ACTIVE = "ACTIVE"
    FULL = "FULL"
    CLOSED = "CLOSED"

class Provenance(Base):
    __tablename__ = "provenance"
    id = Column(Integer, primary_key=True, index=True)
    classification = Column(Enum(ProvenanceType), nullable=False)
    source_url = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    notes = Column(String, nullable=True)

class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True, index=True)
    district_id = Column(String, index=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    flood_probability = Column(Float, nullable=False)
    geometry = Column(Geometry('POLYGON', srid=4326), nullable=True)
    provenance_id = Column(Integer, ForeignKey("provenance.id"), nullable=False)

class Shelter(Base):
    __tablename__ = "shelters"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    capacity = Column(Integer, nullable=False)
    current_occupancy = Column(Integer, default=0)
    status = Column(Enum(ShelterStatus), default=ShelterStatus.CANDIDATE, nullable=False)
    geometry = Column(Geometry('POINT', srid=4326), nullable=False)
    provenance_id = Column(Integer, ForeignKey("provenance.id"), nullable=False)
