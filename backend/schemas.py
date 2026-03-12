from datetime import datetime
from pydantic import BaseModel, Field


class SensorInput(BaseModel):
    distance: float = Field(
        ...,
        ge=0,
        example=15.4,
        description="Distance to nearest object (m)",
    )
    relative_velocity: float = Field(
        ...,
        example=10.0,
        description="Relative velocity to object (m/s). Positive means closing in.",
    )


class PredictionResponse(BaseModel):
    predicted_status: str
    ttc: float | None
    message: str


class HistoryRecord(BaseModel):
    id: int
    distance: float
    ttc: float | None
    axis: float
    speed: float
    steering_angle: float
    relative_velocity: float
    predicted_status: str
    timestamp: datetime

    class Config:
        from_attributes = True
