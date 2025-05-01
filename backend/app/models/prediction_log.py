from sqlalchemy import Column, Integer, String, DateTime, JSON
from app.models.base import Base
import datetime

class PredictionLog(Base):
    __tablename__ = 'prediction_logs'
    id                 = Column(Integer, primary_key=True, index=True)
    username           = Column(String(50), nullable=False)
    ticker             = Column(String(10), nullable=False)
    days               = Column(Integer, nullable=False)
    forecast_direction = Column(String(10), nullable=False)
    request_body       = Column(JSON, nullable=False)
    response_body      = Column(JSON, nullable=False)
    timestamp          = Column(DateTime, default=datetime.datetime.utcnow)
