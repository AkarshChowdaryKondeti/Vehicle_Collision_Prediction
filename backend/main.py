from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os

try:
    from .database import Base, engine, get_db
    from .ml import predict_status
    from .models import PredictionRecord
    from .schemas import HistoryRecord, PredictionResponse, SensorInput
except ImportError:
    from database import Base, engine, get_db
    from ml import predict_status
    from models import PredictionRecord
    from schemas import HistoryRecord, PredictionResponse, SensorInput

app = FastAPI(
    title="Vehicle Safety Prediction API",
    description="Predicts vehicle safety status from sensor data using a trained Random Forest model.",
    version="1.0.0",
)

cors_origins = os.getenv(
    "CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
).split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in cors_origins if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "Vehicle Safety Prediction API is running."}


@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
def predict(sensor: SensorInput, db: Session = Depends(get_db)):
    sensor_values = sensor.model_dump()
    try:
        prediction = predict_status(sensor_values)
    except KeyError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Model feature mismatch: missing field `{exc.args[0]}`.",
        ) from exc

    record = PredictionRecord(
        distance=sensor.distance,
        ttc=sensor.ttc,
        axis=sensor.axis,
        speed=sensor.speed,
        steering_angle=sensor.steering_angle,
        relative_velocity=sensor.relative_velocity,
        predicted_status=prediction,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    messages = {
        "SAFE": "✅ Vehicle is operating safely.",
        "RISK": "⚠️  Warning: Caution advised, risky conditions detected.",
        "HIGH RISK": "🚨 DANGER: Immediate action required!",
    }

    return PredictionResponse(
        predicted_status=prediction,
        message=messages.get(prediction, "Status predicted."),
    )


@app.get("/history", response_model=list[HistoryRecord], tags=["History"])
def get_history(limit: int = 50, db: Session = Depends(get_db)):
    records = (
        db.query(PredictionRecord)
        .order_by(PredictionRecord.timestamp.desc())
        .limit(limit)
        .all()
    )
    return records
