# FastAPI primitives for API app, dependency injection, and HTTP errors.
from fastapi import Depends, FastAPI, HTTPException
# Middleware used to allow browser cross-origin requests.
from fastapi.middleware.cors import CORSMiddleware
# SQLAlchemy session type for request-scoped DB operations.
from sqlalchemy.orm import Session
# Read environment variables such as CORS_ORIGINS.
import os

try:
    # Package-style imports when running as module.
    from .database import Base, engine, get_db
    from .ml import predict_status
    from .models import PredictionRecord
    from .schemas import HistoryRecord, PredictionResponse, SensorInput
except ImportError:
    # Fallback imports when running files directly.
    from database import Base, engine, get_db
    from ml import predict_status
    from models import PredictionRecord
    from schemas import HistoryRecord, PredictionResponse, SensorInput

# Create FastAPI application metadata shown in API docs.
app = FastAPI(
    title="Vehicle Safety Prediction API",
    description="Predicts vehicle safety status from sensor data using a trained Random Forest model.",
    version="1.0.0",
)

# Read allowed frontend origins from env and split comma-separated values.
cors_origins = os.getenv(
    "CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
).split(",")
# Register CORS policy so browser clients can call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in cors_origins if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables if they do not already exist.
Base.metadata.create_all(bind=engine)


@app.get("/", tags=["Health"])
def root():
    # Simple health endpoint confirming API process is alive.
    return {"status": "ok", "message": "Vehicle Safety Prediction API is running."}


@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
def predict(sensor: SensorInput, db: Session = Depends(get_db)):
    # Convert validated Pydantic input into plain dictionary for ML model.
    sensor_values = sensor.model_dump()
    try:
        # Predict safety status using loaded model artifact.
        prediction = predict_status(sensor_values)
    except KeyError as exc:
        # Return readable API error if model expects a missing feature.
        raise HTTPException(
            status_code=500,
            detail=f"Model feature mismatch: missing field `{exc.args[0]}`.",
        ) from exc

    # Build ORM object for audit/history persistence.
    record = PredictionRecord(
        distance=sensor.distance,
        ttc=sensor.ttc,
        axis=sensor.axis,
        speed=sensor.speed,
        steering_angle=sensor.steering_angle,
        relative_velocity=sensor.relative_velocity,
        predicted_status=prediction,
    )
    # Persist prediction row in database.
    db.add(record)
    db.commit()
    db.refresh(record)

    # Map predicted status to user-friendly message text.
    messages = {
        "SAFE": "✅ Vehicle is operating safely.",
        "RISK": "⚠️  Warning: Caution advised, risky conditions detected.",
        "HIGH RISK": "🚨 DANGER: Immediate action required!",
    }

    # Return normalized status and readable message to frontend.
    return PredictionResponse(
        predicted_status=prediction,
        message=messages.get(prediction, "Status predicted."),
    )


@app.get("/history", response_model=list[HistoryRecord], tags=["History"])
def get_history(limit: int = 50, db: Session = Depends(get_db)):
    # Fetch latest prediction rows in descending timestamp order.
    records = (
        db.query(PredictionRecord)
        .order_by(PredictionRecord.timestamp.desc())
        .limit(limit)
        .all()
    )
    # Let FastAPI serialize ORM rows into HistoryRecord schema.
    return records
