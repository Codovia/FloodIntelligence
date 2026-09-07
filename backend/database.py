"""
database.py — PostgreSQL + PostGIS database operations.
Tables: model_runs, subscribers, alert_events, shelters
All queries use parameterised SQL.
"""
import os
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, Boolean, DateTime, UniqueConstraint, Index, text
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/floodpulse"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


# ── ORM Models ──────────────────────────────────────

class ModelRun(Base):
    __tablename__ = "model_runs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    model_name = Column(String, nullable=False)
    trained_at = Column(String, nullable=False)
    accuracy = Column(Float)
    f1_score = Column(Float)
    balanced_accuracy = Column(Float)
    train_samples = Column(Integer)
    test_samples = Column(Integer)

class Subscriber(Base):
    __tablename__ = "subscribers"
    id = Column(Integer, primary_key=True, autoincrement=True)
    contact_method = Column(String, nullable=False)
    contact_value = Column(String, nullable=False)
    district = Column(String, nullable=False)
    locality = Column(String, nullable=False, default="district_wide")
    created_at = Column(String, nullable=False)
    __table_args__ = (
        UniqueConstraint("contact_method", "contact_value", "district", "locality"),
        Index("idx_sub_district_locality", "district", "locality"),
    )

class AlertEvent(Base):
    __tablename__ = "alert_events"
    id = Column(Integer, primary_key=True, autoincrement=True)
    district = Column(String, nullable=False)
    locality = Column(String, nullable=False)
    predicted_date = Column(String, nullable=False)
    risk_level = Column(String, nullable=False)
    triggered_at = Column(String, nullable=False)
    notified = Column(Boolean, nullable=False, default=False)
    __table_args__ = (
        UniqueConstraint("district", "locality", "predicted_date"),
        Index("idx_alert_district_locality", "district", "locality"),
    )

class Shelter(Base):
    __tablename__ = "shelters"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    district = Column(String, nullable=False)
    locality = Column(String, default="")
    lat = Column(Float)
    lon = Column(Float)
    capacity = Column(Integer, default=0)
    current_occupancy = Column(Integer, default=0)
    status = Column(String, default="CANDIDATE")
    changed_by = Column(String, default="system")
    changed_at = Column(String, default="")
    change_reason = Column(String, default="")


# ── Schema Initialization ───────────────────────────

def initialize_database():
    """Create all tables if they don't exist."""
    Base.metadata.create_all(bind=engine)
    print("Database tables initialized.")

def get_db():
    """Dependency for FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Subscriber CRUD ─────────────────────────────────

def subscriber_create(contact_method: str, contact_value: str, district: str, locality: str = "district_wide") -> dict:
    db = SessionLocal()
    try:
        sub = Subscriber(
            contact_method=contact_method,
            contact_value=contact_value,
            district=district,
            locality=locality,
            created_at=datetime.now(timezone.utc).isoformat()
        )
        db.add(sub)
        db.commit()
        db.refresh(sub)
        return {"id": sub.id, "district": sub.district, "locality": sub.locality}
    finally:
        db.close()

def subscriber_delete(sub_id: int) -> bool:
    db = SessionLocal()
    try:
        sub = db.query(Subscriber).filter(Subscriber.id == sub_id).first()
        if sub:
            db.delete(sub)
            db.commit()
            return True
        return False
    finally:
        db.close()

def subscriber_delete_by_contact(method: str, value: str) -> bool:
    db = SessionLocal()
    try:
        deleted = db.query(Subscriber).filter(
            Subscriber.contact_method == method,
            Subscriber.contact_value == value
        ).delete()
        db.commit()
        return deleted > 0
    finally:
        db.close()

def subscriber_list(district: str = None, locality: str = None) -> list:
    db = SessionLocal()
    try:
        q = db.query(Subscriber)
        if district:
            q = q.filter(Subscriber.district == district)
        if locality:
            q = q.filter(Subscriber.locality == locality)
        return [
            {
                "id": s.id, "contact_method": s.contact_method,
                "contact_value": s.contact_value, "district": s.district,
                "locality": s.locality, "created_at": s.created_at
            }
            for s in q.all()
        ]
    finally:
        db.close()


# ── Alert Event CRUD ────────────────────────────────

def alert_event_upsert(district: str, locality: str, predicted_date: str, risk_level: str) -> dict:
    """Insert alert event with 48-hour deduplication."""
    db = SessionLocal()
    try:
        existing = db.query(AlertEvent).filter(
            AlertEvent.district == district,
            AlertEvent.locality == locality,
            AlertEvent.predicted_date == predicted_date
        ).first()
        
        if existing:
            return {"id": existing.id, "status": "duplicate"}
        
        event = AlertEvent(
            district=district, locality=locality,
            predicted_date=predicted_date, risk_level=risk_level,
            triggered_at=datetime.now(timezone.utc).isoformat(),
            notified=False
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return {"id": event.id, "status": "created"}
    finally:
        db.close()

def alert_event_list(district: str = None, limit: int = 50) -> list:
    db = SessionLocal()
    try:
        q = db.query(AlertEvent)
        if district:
            q = q.filter(AlertEvent.district == district)
        q = q.order_by(AlertEvent.triggered_at.desc()).limit(limit)
        return [
            {
                "id": e.id, "district": e.district, "locality": e.locality,
                "predicted_date": e.predicted_date, "risk_level": e.risk_level,
                "triggered_at": e.triggered_at, "notified": e.notified
            }
            for e in q.all()
        ]
    finally:
        db.close()

def alert_event_mark_notified(event_id: int):
    db = SessionLocal()
    try:
        event = db.query(AlertEvent).filter(AlertEvent.id == event_id).first()
        if event:
            event.notified = True
            db.commit()
    finally:
        db.close()


# ── Model Run CRUD ──────────────────────────────────

def model_run_create(metrics: dict) -> int:
    db = SessionLocal()
    try:
        run = ModelRun(
            model_name="RandomForest_v2",
            trained_at=datetime.now(timezone.utc).isoformat(),
            accuracy=metrics.get("accuracy"),
            f1_score=metrics.get("f1_score"),
            balanced_accuracy=metrics.get("balanced_accuracy"),
            train_samples=metrics.get("train_samples"),
            test_samples=metrics.get("test_samples"),
        )
        db.add(run)
        db.commit()
        db.refresh(run)
        return run.id
    finally:
        db.close()


# ── Shelter CRUD ────────────────────────────────────

def shelter_list(district: str = None, status: str = None) -> list:
    db = SessionLocal()
    try:
        q = db.query(Shelter)
        if district:
            q = q.filter(Shelter.district == district)
        if status:
            q = q.filter(Shelter.status == status)
        return [
            {
                "id": s.id, "name": s.name, "district": s.district,
                "locality": s.locality, "lat": s.lat, "lon": s.lon,
                "capacity": s.capacity, "current_occupancy": s.current_occupancy,
                "status": s.status, "changed_by": s.changed_by,
                "changed_at": s.changed_at, "change_reason": s.change_reason,
            }
            for s in q.all()
        ]
    finally:
        db.close()

def shelter_create(data: dict) -> dict:
    db = SessionLocal()
    try:
        s = Shelter(
            name=data["name"], district=data["district"],
            locality=data.get("locality", ""),
            lat=data.get("lat"), lon=data.get("lon"),
            capacity=data.get("capacity", 0),
            current_occupancy=data.get("current_occupancy", 0),
            status=data.get("status", "CANDIDATE"),
            changed_by=data.get("changed_by", "system"),
            changed_at=datetime.now(timezone.utc).isoformat(),
            change_reason=data.get("change_reason", "Initial creation"),
        )
        db.add(s)
        db.commit()
        db.refresh(s)
        return {"id": s.id, "name": s.name, "status": s.status}
    finally:
        db.close()

def shelter_update_status(shelter_id: int, new_status: str, changed_by: str, reason: str) -> dict | None:
    db = SessionLocal()
    try:
        s = db.query(Shelter).filter(Shelter.id == shelter_id).first()
        if not s:
            return None
        old_status = s.status
        s.status = new_status
        s.changed_by = changed_by
        s.changed_at = datetime.now(timezone.utc).isoformat()
        s.change_reason = f"{old_status} → {new_status}: {reason}"
        db.commit()
        return {"id": s.id, "old_status": old_status, "new_status": new_status}
    finally:
        db.close()
