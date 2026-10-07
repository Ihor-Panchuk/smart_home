from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
import database
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pwdlib import PasswordHash
import os
import jwt
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"


def create_access_token(user_id, username):
    payload = {
        "sub": username,
        "user_id": user_id
    }

    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=ALGORITHM)

    return token


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        return {
            "username": payload["sub"],
            "user_id": payload["user_id"]
        }

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Недействительный токен"
        )


password_hash = PasswordHash.recommended()


class DeviceData(BaseModel):
    name: str
    device_type: str
    brightness: int | None = Field(default=None, ge=0, le=100)
    temperature: int | None = Field(default=None, ge=10, le=30)
    is_on: bool = False
    is_locked: bool | None = None


class UserData(BaseModel):
    username: str
    password: str


class LoginData(BaseModel):
    username: str
    password: str


class NameData(BaseModel):
    name: str


class BrightnessData(BaseModel):
    brightness: int = Field(ge=0, le=100)


class TemperatureData(BaseModel):
    temperature: int = Field(ge=10, le=30)


app = FastAPI()


@app.get("/")
def home():
    return RedirectResponse("/frontend/index.html")


app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")


@app.get("/devices")
def get_devices(current_user=Depends(get_current_user)):
    return database.get_devices(current_user["user_id"])


@app.get("/devices/{device_id}")
def get_device(device_id: int):
    device = database.get_device(device_id)
    if device is None:
        raise HTTPException(status_code=404, detail="Устройство не найдено")
    return device


@app.get("/devices/type/{device_type}")
def get_device_by_type(device_type: str):
    devices = database.get_devices_by_type(device_type)
    return devices


@app.get("/devices/is_on/{is_on}")
def get_devices_by_status(is_on: bool):
    devices = database.get_devices_by_status(is_on)
    return devices


@app.get("/devices/{device_id}/status")
def device_status(device_id: int):
    device = database.get_device(device_id)
    if device is None:
        raise HTTPException(status_code=404, detail="Устройство не найдено")
    if device["device_type"] == "light":
        status = {"id": device["id"],
                  "is_on": device["is_on"],
                  "brightness": device["brightness"]}
        return status
    elif device["device_type"] == "thermostat":
        status = {"id": device["id"],
                  "is_on": device["is_on"],
                  "temperature": device["temperature"]}
        return status
    elif device["device_type"] == "door_lock":
        status = {"id": device["id"],
                  "is_locked": device["is_locked"]}
        return status
    else:
        raise HTTPException(
            status_code=400, detail="Неизвестный тип устройства")


# удаление устройств


@app.delete("/devices/{device_id}")
def del_device(device_id: int):
    device = database.delete_device(device_id)
    if device is None:
        raise HTTPException(status_code=404, detail="Устройство не найдено")
    return device

# добавленние устройства


@app.post("/devices")
def add_device(data: DeviceData, current_user=Depends(get_current_user)):
    if data.device_type == "light" and data.temperature is not None:
        raise HTTPException(
            status_code=400, detail="Девайсы класа light не имеют параметра temperature")

    if data.device_type == "thermostat" and data.brightness is not None:
        raise HTTPException(
            status_code=400, detail="Девайсы класа thermostat не имеют параметра brightness")

    if data.device_type == "door_lock" and data.temperature is not None:
        raise HTTPException(
            status_code=400, detail="Девайсы класа door_lock не имеют параметра temperature")

    if data.device_type == "door_lock" and data.brightness is not None:
        raise HTTPException(
            status_code=400, detail="Девайсы класа door_lock не имеют параметра brightness")

    if data.device_type != "door_lock" and data.is_locked is not None:
        raise HTTPException(
            status_code=400, detail="Параметр is_locked имеют только девайсы класса door_lock")

    device = database.add_device(
        data.name, data.device_type, data.is_on, data.brightness, data.temperature, data.is_locked, current_user["user_id"])
    return device

# редактирование устройства


@app.put("/devices/{device_id}")
def change_device(device_id: int, data: NameData):
    device = database.update_device_name(device_id, data.name)
    if device is None:
        raise HTTPException(status_code=404, detail="Устройство не найдено")
    return device

# включенние - выключенние девайса is_on


@app.put("/devices/{device_id}/on")
def turn_on(device_id: int):
    device = database.turn_on_device(device_id)
    if device is None:
        raise HTTPException(status_code=404, detail="Устройство не найдено")
    return device


@app.put("/devices/{device_id}/off")
def turn_off(device_id: int):
    device = database.turn_off_device(device_id)
    if device is None:
        raise HTTPException(status_code=404, detail="Устройство не найдено")
    return device
# ==============================================================================

# управление настройками устройств
# яркость


@app.put("/devices/{device_id}/brightness")
def change_brightness(device_id: int, data: BrightnessData):
    device = database.get_device(device_id)
    if device is None:
        raise HTTPException(status_code=404, detail="Устройство не найдено")
    if device["device_type"] != "light":
        raise HTTPException(
            status_code=400, detail="Параметр brightness можно применять только к девайсам класса light")
    result = database.update_brightness(device_id, data.brightness)
    return result


# температура
@app.put("/devices/{device_id}/temperature")
def change_temperature(device_id: int, data: TemperatureData):
    device = database.get_device(device_id)
    if device is None:
        raise HTTPException(status_code=404, detail="Устройство не найдено")
    if device["device_type"] != "thermostat":
        raise HTTPException(
            status_code=400, detail="Параметр temperature можно применять только к девайсам класса thermostat")
    result = database.update_temperature(device_id, data.temperature)
    return result
# ==============================================================================

# endpoints для измененния состояния устройства класа DoorLock
# endpoint для закрытия замка


@app.put("/devices/{device_id}/lock")
def lock(device_id: int):
    device = database.get_device(device_id)
    if device is None:
        raise HTTPException(status_code=404, detail="Устройство не найдено")
    if device["device_type"] != "door_lock":
        raise HTTPException(
            status_code=400, detail="Параметр is_locked можно применять только к девайсам класса door_lock")
    result = database.lock_device(device_id)
    return result

# endpoint для открытия замка


@app.put("/devices/{device_id}/unlock")
def unlock(device_id: int):
    device = database.get_device(device_id)
    if device is None:
        raise HTTPException(status_code=404, detail="Устройство не найдено")
    if device["device_type"] != "door_lock":
        raise HTTPException(
            status_code=400, detail="Параметр is_locked можно применять только к девайсам класса door_lock")
    result = database.unlock_device(device_id)
    return result
# ==============================================================================

# endpoint для регистрации пользователя


@app.post("/register")
def register(user: UserData):
    print(user.username)
    hashed_password = password_hash.hash(user.password)
    created = database.create_user(user.username, hashed_password)
    if not created:
        raise HTTPException(
            status_code=400, detail="Пользователь с таким именем уже существует")

    return {"message": "Пользователь создан"}

# endpoint для входа пользователя
# проверка логина и пароля


@app.post("/login")
def login(user: LoginData):
    db_user = database.get_user_by_username(user.username)
    if db_user is None:
        raise HTTPException(
            status_code=401, detail="Неверное имя пользователя или пароль")
    if not password_hash.verify(user.password, db_user[2]):
        raise HTTPException(
            status_code=401, detail="Неверное имя пользователя или пароль")
    token = create_access_token(db_user[0], user.username)

    return {
        "message": "Вход выполнен",
        "access_token": token
    }

# ==============================================================================


@app.get("/me")
def me(current_user: str = Depends(get_current_user)):
    return {"username": current_user["username"]}
