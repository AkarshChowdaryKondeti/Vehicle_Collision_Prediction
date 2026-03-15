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
    # Allow direct script execution.
    from database import Base, engine, get_db
    from ml import predict_status
    from models import PredictionRecord
    from schemas import HistoryRecord, PredictionResponse, SensorInput

app = FastAPI(
    title="Vehicle Safety Prediction API",
    description="Uses the trained model.pkl artifact to predict vehicle safety.",
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

DEFAULT_AXIS = 0.0
DEFAULT_SPEED = 60.0
DEFAULT_STEERING_ANGLE = 0.0
NO_COLLISION_TTC = 999.0
IMMINENT_DISTANCE_M = 2.0
HIGH_RISK_TTC_S = 2.0
RISK_TTC_S = 4.0
HIGH_RISK_DISTANCE_M = 3.0
RISK_DISTANCE_M = 5.0
STATUS_PRIORITY = {
    "SAFE": 0,
    "RISK": 1,
    "HIGH RISK": 2,
    "COLLIDED": 3,
}
STATUS_GUIDANCE = {
    "SAFE": "No immediate collision risk detected. Keep a safe buffer and continue monitoring traffic.",
    "RISK": "Caution advised. Reduce speed slightly and prepare to brake if the gap closes.",
    "HIGH RISK": "High collision risk detected. Brake firmly and increase following distance now.",
    "COLLIDED": "Collision state detected. Stop the vehicle and assess the surroundings immediately.",
}


def check_edge_case(distance: float, relative_velocity: float) -> tuple[str, float | None, str] | None:
    if distance == 0:
        return (
            "COLLIDED",
            0.0,
            "Distance is 0 m. The vehicle is already in collision with the obstacle.",
        )

    # Override the model for immediate hazard cases.
    if distance <= IMMINENT_DISTANCE_M and relative_velocity > 0:
        ttc = round(distance / relative_velocity, 2)
        return (
            "HIGH RISK",
            ttc,
            f"Obstacle is extremely close. Estimated TTC is {ttc:.2f} seconds. Brake immediately.",
        )

    if distance <= IMMINENT_DISTANCE_M and relative_velocity <= 0:
        return (
            "RISK",
            None,
            "Obstacle is very close. Maintain braking distance and avoid moving forward.",
        )

    return None


def derive_ttc(distance: float, relative_velocity: float) -> float:
    if distance == 0:
        return 0.0
    # The model expects a numeric TTC even when there is no closing speed.
    if relative_velocity <= 0:
        return NO_COLLISION_TTC
    return round(distance / relative_velocity, 2)


def derive_rule_based_status(distance: float, relative_velocity: float, ttc: float) -> str | None:
    if relative_velocity <= 0:
        if distance <= HIGH_RISK_DISTANCE_M:
            return "RISK"
        return None

    if distance <= HIGH_RISK_DISTANCE_M or ttc <= HIGH_RISK_TTC_S:
        return "HIGH RISK"

    if distance <= RISK_DISTANCE_M or ttc <= RISK_TTC_S:
        return "RISK"

    return None


def apply_safety_guardrails(
    model_prediction: str, distance: float, relative_velocity: float, ttc: float
) -> str:
    rule_based_status = derive_rule_based_status(distance, relative_velocity, ttc)
    if rule_based_status is None:
        return model_prediction

    model_priority = STATUS_PRIORITY.get(model_prediction, -1)
    rule_priority = STATUS_PRIORITY[rule_based_status]

    if distance <= RISK_DISTANCE_M and relative_velocity > 0 and ttc <= RISK_TTC_S:
        return rule_based_status

    if rule_priority > model_priority:
        return rule_based_status

    return model_prediction


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
        sensor_values = build_model_input(sensor.distance, sensor.relative_velocity)
        try:
            model_prediction = predict_status(sensor_values)
        except KeyError as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Model feature mismatch: missing field `{exc.args[0]}`.",
            ) from exc

        ttc = sensor_values["ttc"]
        prediction = apply_safety_guardrails(
            model_prediction,
            sensor.distance,
            sensor.relative_velocity,
            ttc,
        )
        if ttc == NO_COLLISION_TTC:
            message = build_prediction_message(prediction, None)
            response_ttc = None
        else:
            message = build_prediction_message(prediction, ttc)
            response_ttc = ttc

    record = PredictionRecord(
        distance=sensor.distance,
        ttc=ttc,
        axis=sensor_values["axis"],
        speed=sensor_values["speed"],
        steering_angle=sensor_values["steering_angle"],
        relative_velocity=sensor.relative_velocity,
        predicted_status=prediction,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return PredictionResponse(
        predicted_status=prediction,
        ttc=response_ttc,
        message=message,
    )


@app.get("/history", response_model=list[HistoryRecord], tags=["History"])
def get_history(limit: int | None = None, db: Session = Depends(get_db)):
    query = db.query(PredictionRecord).order_by(PredictionRecord.timestamp.desc())

    if limit is not None:
        query = query.limit(limit)

    records = query.all()
    return records
