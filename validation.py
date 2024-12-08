import re

def validate_name(name):
    """Проверяет, что имя не пустое и содержит только буквы и пробелы."""
    if not name:
        return False, "Имя не может быть пустым."
    if not re.fullmatch(r"[a-zA-Zа-яА-ЯёЁ\s]+", name):
        return False, "Имя должно содержать только буквы и пробелы."
    return True, ""

def validate_phone(phone):
    """Проверяет, что номер телефона соответствует определенному формату."""
    # Здесь можно использовать более сложное регулярное выражение в зависимости от требуемого формата
    if not phone:
        return False, "Телефон не может быть пустым."
    if not re.fullmatch(r"\+?\d{10,15}", phone): #Пример,  нужно  адаптировать  под  нужный  формат
        return False, "Неверный формат телефона."
    return True, ""

def validate_date(date_str):
    """Проверяет, что дата имеет формат ГГГГ-ММ-ДД."""
    try:
        from datetime import datetime
        datetime.strptime(date_str, '%Y-%m-%d')
        return True, ""
    except ValueError:
        return False, "Неверный формат даты (ГГГГ-ММ-ДД)."

def validate_time(time_str):
    """Проверяет, что время имеет формат ЧЧ:ММ."""
    try:
        from datetime import datetime
        datetime.strptime(time_str, '%H:%M')
        return True, ""
    except ValueError:
        return False, "Неверный формат времени (ЧЧ:ММ)."

def validate_service_id(service_id, services):
    """Проверяет, что ID услуги существует."""
    try:
        service_id = int(service_id)
        if service_id <=0 or service_id > len(services):
            return False, "Услуга не найдена."
        return True, ""
    except ValueError:
        return False, "Неверный ID услуги."