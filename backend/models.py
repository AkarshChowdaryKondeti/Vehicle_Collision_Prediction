# Timestamp type for default record creation time.
from datetime import datetime
# SQLAlchemy column and type definitions for ORM model.
from sqlalchemy import Column, DateTime, Float, Integer, String

try:
    # Package-style import when running backend as a module.
    from .database import Base
except ImportError:
    # Fallback import when running files directly.
    from database import Base


class PredictionRecord(Base):
    # Physical DB table name.
    __tablename__ = "predictions"

    # Auto-increment primary key for each prediction row.
    id = Column(Integer, primary_key=True, index=True)
    # Sensor feature columns used by model inference.
    distance = Column(Float)
    ttc = Column(Float)
    axis = Column(Float)
    speed = Column(Float)
    steering_angle = Column(Float)
    relative_velocity = Column(Float)
    # Predicted safety status output by model.
    predicted_status = Column(String)
    # Creation timestamp captured in UTC for ordering/history.
    timestamp = Column(DateTime, default=datetime.utcnow)
