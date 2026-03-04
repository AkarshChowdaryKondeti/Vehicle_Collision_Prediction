from datetime import datetime
from pydantic import BaseModel, Field


class SensorInput(BaseModel):
    distance: float = Field(..., example=15.4, description="Distance to nearest object (m)")
    ttc: float = Field(..., example=1.8, description="Time-to-collision (s)")
    axis: float = Field(..., example=0.3, description="Lateral axis deviation")
    speed: float = Field(..., example=72.0, description="Vehicle speed (km/h)")
    steering_angle: float = Field(..., example=5.0, description="Steering wheel angle (°)")
    relative_velocity: float = Field(..., example=-10.0, description="Relative velocity to object (m/s)")


class PredictionResponse(BaseModel):
    predicted_status: str
    message: str


class HistoryRecord(BaseModel):
    id: int
    distance: float
    ttc: float
    axis: float
    speed: float
    steering_angle: float
    relative_velocity: float
    predicted_status: str
    timestamp: datetime

    class Config:
        from_attributes = True
