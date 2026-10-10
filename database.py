import psycopg
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

user = os.getenv("user")
password = os.getenv("password")
host = os.getenv("host")
port = os.getenv("port")
dbname = os.getenv("dbname")

# функции для подлюченния и отключенния от баззы данных


def get_connection():  # подключенние базы данных к питону
    connection = psycopg.connect(DATABASE_URL)
    return connection


def close_connection(cursor, connection):    # отключенние от базы данных
    cursor.close()
    connection.close()
# ========================================================================


# превращаем результат запроса из SQL в список словарей
keys = ["id", "name", "device_type", "is_on",
        "brightness", "temperature", "is_locked"]


def devices_to_dict(devices):
    result = []
    for device in devices:
        dct = dict(zip(keys, device))
        result.append(dct)
    return result


def device_to_dict(device):
    return dict(zip(keys, device))
# =========================================================


def get_devices(user_id):  # функция для возвращенния устройств(всех или нескольких)
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM devices WHERE user_id = %s", (user_id,))
    devices = cursor.fetchall()
    close_connection(cursor, connection)
    # превращаем результат запроса из SQL в список словарей
    return devices_to_dict(devices)


def get_device(device_id, user_id):  # функция для возвращенния устройста (одного)
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT * FROM devices WHERE id = %s AND user_id = %s", (device_id, user_id))
    device = cursor.fetchone()
    close_connection(cursor, connection)
    if device is None:
        return None
    return device_to_dict(device)


# функция для возвращенния устройста по типу девайса
def get_devices_by_type(device_type, user_id):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT * FROM devices WHERE device_type = %s AND user_id = %s", (device_type, user_id))
    devices = cursor.fetchall()
    close_connection(cursor, connection)
    return devices_to_dict(devices)

# функция для возвращенния устройста по статусу девайса


def get_devices_by_status(is_on, user_id):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT * FROM devices WHERE is_on = %s AND user_id = %s", (is_on, user_id))
    devices = cursor.fetchall()
    close_connection(cursor, connection)
    return devices_to_dict(devices)


# функция для добавленния новых устройств


def add_device(name, device_type, is_on, brightness, temperature, is_locked, user_id):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO devices (name, device_type, is_on, brightness, temperature, is_locked, user_id) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id, name, device_type, is_on, brightness, temperature, is_locked, user_id",
                   (name, device_type, is_on, brightness, temperature, is_locked, user_id))
    device = cursor.fetchone()
    connection.commit()
    close_connection(cursor, connection)
    return device_to_dict(device)


def delete_device(device_id, user_id):  # функция для удаленния устройства
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "DELETE FROM devices WHERE id = %s AND user_id = %s RETURNING id, name, device_type, is_on, brightness, temperature, is_locked", (device_id, user_id))
    device = cursor.fetchone()
    connection.commit()
    close_connection(cursor, connection)
    if device is None:
        return None
    return device_to_dict(device)


# функция для измененния имени устройства
def update_device_name(device_id, new_name):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE devices SET name = %s WHERE id = %s RETURNING id, name, device_type, is_on, brightness, temperature, is_locked",
                   (new_name, device_id))
    device = cursor.fetchone()
    connection.commit()
    close_connection(cursor, connection)
    if device is None:
        return None
    return device_to_dict(device)


def turn_on_device(device_id, user_id):    # функция для включенния устройства
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE devices SET is_on = TRUE WHERE id = %s AND user_id = %s  RETURNING id, name, device_type, is_on, brightness, temperature, is_locked", (device_id, user_id))
    device = cursor.fetchone()
    connection.commit()
    close_connection(cursor, connection)
    if device is None:
        return None
    return device_to_dict(device)


def turn_off_device(device_id, user_id):  # функция для выключенния устройства
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE devices SET is_on = FALSE WHERE id = %s AND user_id = %s  RETURNING id, name, device_type, is_on, brightness, temperature, is_locked", (device_id, user_id))
    device = cursor.fetchone()
    connection.commit()
    close_connection(cursor, connection)
    if device is None:
        return None
    return device_to_dict(device)


# функция для измененния яркости устройства
def update_brightness(device_id, brightness):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE devices SET brightness = %s WHERE id = %s RETURNING id, name, device_type, is_on, brightness, temperature, is_locked", (brightness, device_id))
    device = cursor.fetchone()
    connection.commit()
    close_connection(cursor, connection)
    if device is None:
        return None
    return device_to_dict(device)

# функция для измененния температуры устройства


def update_temperature(device_id, temperature):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE devices SET temperature = %s WHERE id = %s RETURNING id, name, device_type, is_on, brightness, temperature, is_locked", (temperature, device_id))
    device = cursor.fetchone()
    connection.commit()
    close_connection(cursor, connection)
    if device is None:
        return None
    return device_to_dict(device)

# функция для измененния состояния устройства класа DoorLock
# функция для закрытия замка


def lock_device(device_id, user_id):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE devices SET is_locked = TRUE WHERE id = %s AND user_id = %s RETURNING id, name, device_type, is_on, brightness, temperature, is_locked", (device_id, user_id))
    device = cursor.fetchone()
    connection.commit()
    close_connection(cursor, connection)
    if device is None:
        return None
    return device_to_dict(device)

# функция для открытия замка


def unlock_device(device_id, user_id):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE devices SET is_locked = FALSE WHERE id = %s AND user_id = %s RETURNING id, name, device_type, is_on, brightness, temperature, is_locked", (device_id, user_id))
    device = cursor.fetchone()
    connection.commit()
    close_connection(cursor, connection)
    if device is None:
        return None
    return device_to_dict(device)
# =======================================================================================================================

# функция для регистрации пользователя


def create_user(username, password_hash):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
            (username, password_hash))
        connection.commit()
    except psycopg.errors.UniqueViolation:
        connection.rollback()
        return False
    close_connection(cursor, connection)
    return True

# функция для входа пользователя


def get_user_by_username(username):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    close_connection(cursor, connection)
    if user is None:
        return None
    return user
