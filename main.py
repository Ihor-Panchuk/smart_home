from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import database
from fastapi.staticfiles import StaticFiles


class DeviceData(BaseModel):
    name: str
    device_type: str
    brightness: int | None = Field(default=None, ge=0, le=100)
    temperature: int | None = Field(default=None, ge=10, le=30)
    is_on: bool = False
    is_locked: bool | None = None


class NameData(BaseModel):
    name: str


class BrightnessData(BaseModel):
    brightness: int = Field(ge=0, le=100)


class TemperatureData(BaseModel):
    temperature: int = Field(ge=10, le=30)


app = FastAPI()
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")


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
def add_device(data: DeviceData):
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
