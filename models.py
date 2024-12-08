from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Date, Time, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import NUMERIC, INTERVAL

db = SQLAlchemy()

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    price_range = db.Column(NUMERIC(10, 2))
    estimated_time = db.Column(INTERVAL)
    appointments = db.relationship('Appointment', backref='service', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price_range': str(self.price_range),
            'estimated_time': str(self.estimated_time)
        }


class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, ForeignKey('service.id'), nullable=False)
    client_name = db.Column(db.String(100), nullable=False)
    client_phone = db.Column(db.String(20), nullable=False)
    date = db.Column(Date, nullable=False)
    time = db.Column(Time, nullable=False)
    status = db.Column(db.String(50), default='Pending')

    def to_dict(self):
        return {
            'id': self.id,
            'service_id': self.service_id,
            'client_name': self.client_name,
            'client_phone': self.client_phone,
            'date': str(self.date),
            'time': str(self.time),
            'status': self.status
        }