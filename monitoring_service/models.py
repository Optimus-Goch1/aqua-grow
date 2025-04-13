from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class SensorValue(db.Model):
    """Stores sensor readings for each farm."""
    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, nullable=False)  # No FK (decoupled microservice)
    moisture = db.Column(db.Float, nullable=False)
    temperature = db.Column(db.Float, nullable=True)
    humidity = db.Column(db.Float, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)