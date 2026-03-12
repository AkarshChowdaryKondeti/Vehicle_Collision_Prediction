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
    description="Uses the trained model.pkl artifact to predict vehicle safety.",
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

DEFAULT_AXIS = 0.0
DEFAULT_SPEED = 60.0
DEFAULT_STEERING_ANGLE = 0.0
NO_COLLISION_TTC = 999.0
IMMINENT_DISTANCE_M = 2.0
STATUS_GUIDANCE = {
    "SAFE": "No immediate collision risk detected. Keep a safe buffer and continue monitoring traffic.",
    "RISK": "Caution advised. Reduce speed slightly and prepare to brake if the gap closes.",
    "HIGH RISK": "High collision risk detected. Brake firmly and increase following distance now.",
    "COLLIDED": "Collision state detected. Stop the vehicle and assess the surroundings immediately.",
}


def check_edge_case(distance: float, relative_velocity: float) -> tuple[str, float | None, str] | None:
    # A zero gap is a collision regardless of model output.
    if distance == 0:
        return (
            "COLLIDED",
            0.0,
            "Distance is 0 m. The vehicle is already in collision with the obstacle.",
        )

    # A very small gap with positive closing speed is treated as an immediate hazard.
    if distance <= IMMINENT_DISTANCE_M and relative_velocity > 0:
        ttc = round(distance / relative_velocity, 2)
        return (
            "HIGH RISK",
            ttc,
            f"Obstacle is extremely close. Estimated TTC is {ttc:.2f} seconds. Brake immediately.",
        )

    # A very small gap is still risky even when the vehicles are not closing.
    if distance <= IMMINENT_DISTANCE_M and relative_velocity <= 0:
        return (
            "RISK",
            None,
            "Obstacle is very close. Maintain braking distance and avoid moving forward.",
        )

    return None


def derive_ttc(distance: float, relative_velocity: float) -> float:
    # Preserve an immediate-collision signal for zero-gap inputs.
    if distance == 0:
        return 0.0
    # Model requires a numeric TTC value even when the gap is stable/increasing.
    if relative_velocity <= 0:
        return NO_COLLISION_TTC
    return round(distance / relative_velocity, 2)


def build_model_input(distance: float, relative_velocity: float) -> dict:
    ttc = derive_ttc(distance, relative_velocity)
    return {
        "distance": distance,
        "ttc": ttc,
        "axis": DEFAULT_AXIS,
        "speed": DEFAULT_SPEED,
        "steering_angle": DEFAULT_STEERING_ANGLE,
        "relative_velocity": relative_velocity,
    }


def build_prediction_message(prediction: str, ttc: float | None) -> str:
    guidance = STATUS_GUIDANCE.get(
        prediction,
        "Drive cautiously and keep monitoring the obstacle distance.",
    )
    if ttc is None:
        return f"{prediction}: {guidance}"
    return f"{prediction}: TTC is {ttc:.2f} seconds. {guidance}"


@app.get("/", tags=["Health"])
def root():
    # Simple health endpoint confirming API process is alive.
    return {"status": "ok", "message": "Vehicle Safety Prediction API is running."}


@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
def predict(sensor: SensorInput, db: Session = Depends(get_db)):
    edge_case = check_edge_case(sensor.distance, sensor.relative_velocity)
    if edge_case is not None:
        prediction, response_ttc, message = edge_case
        ttc = 0.0 if response_ttc == 0.0 else None
        sensor_values = {
            "axis": DEFAULT_AXIS,
            "speed": DEFAULT_SPEED,
            "steering_angle": DEFAULT_STEERING_ANGLE,
        }
    else:
        # Build the full feature vector expected by model.pkl from user input plus defaults.
        sensor_values = build_model_input(sensor.distance, sensor.relative_velocity)
        try:
            prediction = predict_status(sensor_values)
        except KeyError as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Model feature mismatch: missing field `{exc.args[0]}`.",
            ) from exc

        ttc = sensor_values["ttc"]
        if ttc == NO_COLLISION_TTC:
            message = build_prediction_message(prediction, None)
            response_ttc = None
        else:
            message = build_prediction_message(prediction, ttc)
            response_ttc = ttc

    # Build ORM object for audit/history persistence.
    record = PredictionRecord(
        distance=sensor.distance,
        ttc=ttc,
        axis=sensor_values["axis"],
        speed=sensor_values["speed"],
        steering_angle=sensor_values["steering_angle"],
        relative_velocity=sensor.relative_velocity,
        predicted_status=prediction,
    )
    # Persist prediction row in database.
    db.add(record)
    db.commit()
    db.refresh(record)

    return PredictionResponse(
        predicted_status=prediction,
        ttc=response_ttc,
        message=message,
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
