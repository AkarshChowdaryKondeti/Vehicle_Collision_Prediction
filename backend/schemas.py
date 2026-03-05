# Datetime type used for history response timestamp field.
from datetime import datetime
# Pydantic models and field metadata for request/response validation.
from pydantic import BaseModel, Field


class SensorInput(BaseModel):
    # Distance to nearest obstacle in meters.
    distance: float = Field(..., example=15.4, description="Distance to nearest object (m)")
    # Time-to-collision estimate in seconds.
    ttc: float = Field(..., example=1.8, description="Time-to-collision (s)")
    # Lateral axis deviation value from sensor.
    axis: float = Field(..., example=0.3, description="Lateral axis deviation")
    # Vehicle speed in km/h at inference time.
    speed: float = Field(..., example=72.0, description="Vehicle speed (km/h)")
    # Steering angle in degrees.
    steering_angle: float = Field(..., example=5.0, description="Steering wheel angle (°)")
    # Relative closing/opening velocity in m/s.
    relative_velocity: float = Field(..., example=-10.0, description="Relative velocity to object (m/s)")


class PredictionResponse(BaseModel):
    # Final predicted risk class returned by API.
    predicted_status: str
    # Human-readable message corresponding to predicted class.
    message: str


class HistoryRecord(BaseModel):
    # Stored prediction row primary key.
    id: int
    # Persisted input features used for that prediction.
    distance: float
    ttc: float
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
