from datetime import datetime
from sqlalchemy import Column, DateTime, Float, Integer, String

try:
    from .database import Base
except ImportError:
    # Allow direct script execution.
    from database import Base


class PredictionRecord(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    distance = Column(Float)
    ttc = Column(Float)
    axis = Column(Float)
    speed = Column(Float)
    steering_angle = Column(Float)
    relative_velocity = Column(Float)
    predicted_status = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
