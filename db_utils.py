import psycopg2 
from models import Service, Appointment # Импортируем модели из models.py
import os
from config import config

def get_db_connection():
    try:
        params = config.get('production').SQLALCHEMY_DATABASE_URI.split('/')
        conn = psycopg2.connect(database=params[3], user=params[1].split(':')[0], password=params[1].split(':')[1], host=params[2].split(':')[0], port=params[2].split(':')[1])
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return None

def close_connection(conn):
    if conn:
        conn.close()


def add_service(name, description):
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("INSERT INTO services (name, description) VALUES (%s, %s)", (name, description))
            conn.commit()
        except psycopg2.Error as e:
            conn.rollback()
            print(f"Error adding service: {e}")
        finally:
            close_connection(conn)
def get_service_by_id(service_id):
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM services WHERE id = %s", (service_id,))
            service = cur.fetchone()
            return dict(zip([column[0] for column in cur.description], service)) if service else None
        except psycopg2.Error as e:
            print(f"Error getting service by ID: {e}")
            return None
        finally:
            close_connection(conn)
    return None
def delete_service(service_id):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM services WHERE id = ?", (service_id,))
        conn.commit()
        return True
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Error deleting service: {e}")
        return False
    finally:
        close_connection(conn)

def update_service(service_id, name, description):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("UPDATE services SET name = ?, description = ? WHERE id = ?", (name, description, service_id))
        conn.commit()
        return True
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Error updating service: {e}")
        return False
    finally:
        close_connection(conn)

def get_appointment_by_id(appointment_id):
    # Аналогично get_service_by_id
    pass

def delete_appointment(appointment_id):
    # Аналогично delete_service
    pass

def update_appointment(appointment_id, service_id, client_name, client_phone, date, time, status):
    # Аналогично update_service
    pass