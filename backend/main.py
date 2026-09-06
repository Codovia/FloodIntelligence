from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import models, database

app = FastAPI(
    title="FloodPulse API",
    description="API for the Flood Risk Mapping & Early Warning System",
    version="1.0.0"
)

# Configure CORS for Vite React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    # In a real production app we'd use Alembic, but for prototyping we create all tables here
    models.Base.metadata.create_all(bind=database.engine)

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "FloodPulse API is running"}

@app.get("/api/predictions/{district_id}")
def get_prediction(district_id: str, db: Session = Depends(database.get_db)):
    prediction = db.query(models.Prediction).filter(models.Prediction.district_id == district_id).order_by(models.Prediction.timestamp.desc()).first()
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found for district")
    
    return {
        "district_id": prediction.district_id,
        "flood_probability": prediction.flood_probability,
        "timestamp": prediction.timestamp
    }

@app.get("/api/shelters")
def get_shelters(db: Session = Depends(database.get_db)):
    shelters = db.query(models.Shelter).all()
    # Note: geoalchemy2 geometries need to be serialized to GeoJSON or WKT. 
    # For now, returning basic info.
    return [
        {
            "id": s.id,
            "name": s.name,
            "capacity": s.capacity,
            "current_occupancy": s.current_occupancy,
            "status": s.status.value
        }
        for s in shelters
    ]
