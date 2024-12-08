from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost:5432/db1'  # !!! НЕ ДЕЛАЙТЕ ТАК В PRODUCTION !!!
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'admin'  # Важно! Замените на случайную строку
db = SQLAlchemy(app)

# Модели данных
class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    appointments = db.relationship('Appointment', backref='service', lazy=True)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    client_name = db.Column(db.String(100), nullable=False)
    client_phone = db.Column(db.String(20), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(50), default='Pending')

with app.app_context():
    db.create_all()  # Создает таблицы в БД при первом запуске


@app.route('/services')
def get_services():
    services = Service.query.all()
    return jsonify([{'id': s.id, 'name': s.name, 'description': s.description} for s in services])


@app.route('/appointments', methods=['GET'])
def get_appointments():
    appointments = Appointment.query.all()
    return jsonify([{'id': a.id, 'service_id': a.service_id, 'client_name': a.client_name,
                     'client_phone': a.client_phone, 'date': str(a.date), 'time': str(a.time),
                     'status': a.status} for a in appointments])


@app.route('/appointments', methods=['POST'])
def add_appointment():
    try:
        data = request.get_json()
        # Простая проверка, нужна более строгая валидация!
        if not all(k in data for k in ['service_id', 'client_name', 'client_phone', 'date', 'time']):
            return jsonify({'error': 'Missing data'}), 400

        appointment = Appointment(**data)
        db.session.add(appointment)
        db.session.commit()
        return jsonify({'message': 'Appointment added successfully'}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error adding appointment: {e}")  # Важно логировать ошибки!
        return jsonify({'error': 'Failed to add appointment'}), 500


if __name__ == '__main__':
    app.run(debug=True)