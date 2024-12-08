import json
import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QComboBox, QPushButton, QVBoxLayout,
                             QGridLayout, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView)
import requests
import subprocess
import os
import time

from app import Service
from validation import validate_date, validate_name, validate_phone, validate_service_id, validate_time


class ServiceCenterApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.start_flask_server()

    def initUI(self):
        grid_layout = QGridLayout()
        service_label = QLabel("Услуга:")
        self.service_combo = QComboBox()
        name_label = QLabel("ФИО:")
        self.name_edit = QLineEdit()
        phone_label = QLabel("Телефон:")
        self.phone_edit = QLineEdit()
        date_label = QLabel("Дата (ГГГГ-ММ-ДД):")
        self.date_edit = QLineEdit()
        time_label = QLabel("Время (ЧЧ:ММ):")
        self.time_edit = QLineEdit()
        submit_button = QPushButton("Записаться")
        submit_button.clicked.connect(self.submit_appointment)
        self.appointment_table = QTableWidget()
        self.appointment_table.setColumnCount(6)
        self.appointment_table.setHorizontalHeaderLabels(["ID", "Услуга", "Клиент", "Телефон", "Дата", "Время"])
        self.appointment_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        grid_layout.addWidget(service_label, 0, 0)
        grid_layout.addWidget(self.service_combo, 0, 1)
        grid_layout.addWidget(name_label, 1, 0)
        grid_layout.addWidget(self.name_edit, 1, 1)
        grid_layout.addWidget(phone_label, 2, 0)
        grid_layout.addWidget(self.phone_edit, 2, 1)
        grid_layout.addWidget(date_label, 3, 0)
        grid_layout.addWidget(self.date_edit, 3, 1)
        grid_layout.addWidget(time_label, 4, 0)
        grid_layout.addWidget(self.time_edit, 4, 1)
        grid_layout.addWidget(submit_button, 5, 1)

        v_layout = QVBoxLayout()
        v_layout.addLayout(grid_layout)
        v_layout.addWidget(self.appointment_table)
        self.setLayout(v_layout)
        self.fetch_services()
        self.fetch_appointments() # Загрузка записей при запуске


    def start_flask_server(self):
        try:
            self.flask_process = subprocess.Popen(["python", "flask_server.py"],
                                                 creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                                                 stdout=subprocess.PIPE,
                                                 stderr=subprocess.PIPE)

            time.sleep(3)

            stdout, stderr = self.flask_process.communicate()
            if stdout or stderr:
                err_message = str(stderr, encoding='utf-8') if stderr else str(stdout, encoding='utf-8')
                QMessageBox.critical(self, "Ошибка", f"Ошибка запуска сервера: {err_message.strip()}")
                return

            print("Сервер Flask запущен успешно.")

        except FileNotFoundError:
            QMessageBox.critical(self, "Ошибка", "Файл flask_server.py не найден!")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось запустить сервер: {e}")

    def fetch_services(self):
        try:
            response = requests.get('http://localhost:5432/services', timeout=10)
            response.raise_for_status()
            services = response.json()
            self.service_combo.clear()
            self.service_combo.addItems([service['name'] for service in services])
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при получении услуг: {e}")
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "Ошибка", f"Неверный формат данных: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Непредвиденная ошибка: {e}")

    def submit_appointment(self):
        name = self.name_edit.text()
        phone = self.phone_edit.text()
        date_str = self.date_edit.text()
        time_str = self.time_edit.text()
        service_id = self.service_combo.currentIndex() + 1

        name_valid, name_error = validate_name(name)
        phone_valid, phone_error = validate_phone(phone)
        date_valid, date_error = validate_date(date_str)
        time_valid, time_error = validate_time(time_str)
        service_valid, service_error = validate_service_id(service_id, Service) # services нужно получить из fetch_services


        if not (name_valid and phone_valid and date_valid and time_valid and service_valid):
            errors = []
            if not name_valid: errors.append(name_error)
            if not phone_valid: errors.append(phone_error)
            if not date_valid: errors.append(date_error)
            if not time_valid: errors.append(time_error)
            if not service_valid: errors.append(service_error)

            QMessageBox.warning(self, "Ошибка", "\n".join(errors))
            return

        try:
            data = {
                'service_id': self.service_combo.currentIndex() + 1,
                'client_name': self.name_edit.text(),
                'client_phone': self.phone_edit.text(),
                'date': self.date_edit.text(),
                'time': self.time_edit.text()
            }

            response = requests.post('http://localhost:5432/appointments', json=data, timeout=10)
            response.raise_for_status()
            QMessageBox.information(self, "Успех", "Запись успешно добавлена!")
            self.fetch_appointments()
            self.clear_fields()
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении записи: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Непредвиденная ошибка: {e}")


    def fetch_appointments(self):
        try:
            response = requests.get('http://localhost:5432/appointments', timeout=10)
            response.raise_for_status()
            appointments = response.json()
            self.update_table(appointments)
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при получении записей: {e}")
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "Ошибка", f"Неверный формат данных: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Непредвиденная ошибка: {e}")

    def update_table(self, appointments):
        self.appointment_table.setRowCount(len(appointments))
        for row, appointment in enumerate(appointments):
            items = [
                QTableWidgetItem(str(appointment.get('id', ''))),
                QTableWidgetItem(str(appointment.get('service_id', ''))),
                QTableWidgetItem(str(appointment.get('client_name', ''))),
                QTableWidgetItem(str(appointment.get('client_phone', ''))),
                QTableWidgetItem(str(appointment.get('date', ''))),
                QTableWidgetItem(str(appointment.get('time', ''))),
            ]
            for col, item in enumerate(items):
                self.appointment_table.setItem(row, col, item)

    def clear_fields(self):
        self.name_edit.clear()
        self.phone_edit.clear()
        self.date_edit.clear()
        self.time_edit.clear()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ServiceCenterApp()
    window.show()
    sys.exit(app.exec_())