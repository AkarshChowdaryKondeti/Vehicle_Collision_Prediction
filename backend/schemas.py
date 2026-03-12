# Datetime type used for history response timestamp field.
from datetime import datetime
# Pydantic models and field metadata for request/response validation.
from pydantic import BaseModel, Field


class SensorInput(BaseModel):
    # Distance to nearest obstacle in meters.
    distance: float = Field(
        ...,
        ge=0,
        example=15.4,
        description="Distance to nearest object (m)",
    )
    # Relative closing/opening velocity in m/s.
    relative_velocity: float = Field(
        ...,
        example=10.0,
        description="Relative velocity to object (m/s). Positive means closing in.",
    )


class PredictionResponse(BaseModel):
    # ADAS-like risk category derived from TTC bands.
    predicted_status: str
    # Computed TTC in seconds when closing speed is positive.
    ttc: float | None
    # Human-readable message corresponding to computed TTC and severity.
    message: str


class HistoryRecord(BaseModel):
    # Stored prediction row primary key.
    id: int
    # Persisted input features used for that prediction.
    distance: float
    ttc: float | None
    axis: float
    speed: float
    steering_angle: float
    relative_velocity: float
    # Persisted predicted class.
    predicted_status: str
    # UTC creation time of prediction record.
    timestamp: datetime

    class Config:
        # Allow direct serialization from SQLAlchemy ORM objects.
        from_attributes = True
