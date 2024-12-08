import os
import logging
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import BadRequest, NotFound
from werkzeug.security import generate_password_hash, check_password_hash
from config import config


app = Flask(__name__)
app.config.from_object(config['default'])
config_name = os.environ.get('FLASK_CONFIG') or 'default'
app.config.from_object(config[config_name])

# Настройка логирования
logging.basicConfig(level=logging.INFO, filename='flask_server.log', filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s')

db = SQLAlchemy(app)

# Модели (models.py - отдельный файл)
from models import Service, Appointment


@app.route('/services', methods=['GET'])
def get_services():
    try:
        services = Service.query.all()
        return jsonify([s.to_dict() for s in services])
    except Exception as e:
        app.logger.exception(f"Ошибка при получении услуг: {e}")
        return jsonify({'error': 'Ошибка при получении услуг'}), 500


@app.route('/appointments', methods=['GET'])
def get_appointments():
    try:
        appointments = Appointment.query.all()
        return jsonify([a.to_dict() for a in appointments])
    except Exception as e:
        app.logger.exception(f"Ошибка при получении записей: {e}")
        return jsonify({'error': 'Ошибка при получении записей'}), 500


@app.route('/appointments', methods=['POST'])
def create_appointment():
    try:
        data = request.get_json()
        if not all(k in data for k in ['service_id', 'client_name', 'client_phone', 'date', 'time']):
            raise BadRequest("Не все необходимые поля заполнены.")

        service = Service.query.get(data['service_id'])
        if not service:
            raise NotFound("Услуга не найдена.")

        appointment = Appointment(**data)
        db.session.add(appointment)
        db.session.commit()
        return jsonify({'message': 'Запись добавлена'}), 201
    except BadRequest as e:
        return jsonify({'error': str(e)}), 400
    except NotFound as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        db.session.rollback()
        app.logger.exception(f"Ошибка при добавлении записи: {e}")
        return jsonify({'error': 'Ошибка при добавлении записи'}), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.logger.info('Запуск сервера Flask...')
    app.run(debug=app.config['DEBUG'], port=app.config['5432'], host='127.0.0.1')