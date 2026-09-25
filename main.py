from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import database


class DeviceData(BaseModel):
    name: str
    device_type: str
    brightness: int | None = None
    temperature: int | None = None
    is_on: bool = False
    is_locked: bool | None = None


class NameData(BaseModel):
    name: str


class BrightnessData(BaseModel):
    brightness: int = Field(ge=0, le=100)


class TemperatureData(BaseModel):
    temperature: int = Field(ge=10, le=30)


app = FastAPI()


@app.get("/devices")
def get_devices():
    return database.get_devices()


@app.get("/devices/{device_id}")
def get_device(device_id: int):
    device = database.get_device(device_id)
    if device is None:
        raise HTTPException(status_code=404, detail="Устройство не найдено")
    return device


@app.get("/devices/{device_id}/status")
def device_status(device_id: int):
    device = database.get_device(device_id)
    if device is None:
        raise HTTPException(status_code=404, detail="Устройство не найдено")
    return device


# удаление устройств


@app.delete("/devices/{device_id}")
def del_device(device_id: int):
    device = database.delete_device(device_id)
    if device is None:
        raise HTTPException(status_code=404, detail="Устройство не найдено")
    return device

# добавленние устройства


@app.post("/devices")
def add_device(data: DeviceData):
    device = database.add_device(
        data.name, data.device_type, data.is_on, data.brightness, data.temperature, data.is_locked)
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
    device = database.update_brightness(device_id, data.brightness)
    if device is None:
        raise HTTPException(status_code=404, detail="Устройство не найдено")
    return device


# температура
@app.put("/devices/{device_id}/temperature")
def change_temperature(device_id: int, data: TemperatureData):
    device = database.update_temperature(device_id, data.temperature)
    if device is None:
        raise HTTPException(status_code=404, detail="Устройство не найдено")
    return device
# ==============================================================================

# endpoints для измененния состояния устройства класа DoorLock
# endpoint для закрытия замка


@app.put("/devices/{device_id}/lock")
def lock(device_id: int):
    device = database.lock_device(device_id)
    if device is None:
        raise HTTPException(status_code=404, detail="Устройство не найдено")
    return device

# endpoint для открытия замка


@app.put("/devices/{device_id}/unlock")
def unlock(device_id: int):
    device = database.unlock_device(device_id)
    if device is None:
        raise HTTPException(status_code=404, detail="Устройство не найдено")
    return device


# Git test
