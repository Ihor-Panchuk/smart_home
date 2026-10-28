
import json


class Device:
    next_id = 1

    def __init__(self, name, device_type):
        self.id = Device.next_id
        self.name = name
        self.device_type = device_type
        self.is_on = False
        Device.next_id += 1

    def turn_on(self):
        self.is_on = True
        return f"{self.name} включен!"

    def turn_off(self):
        self.is_on = False
        return f"{self.name} выключен!"

    def status(self):
        if self.is_on:
            return f"{self.name} включен!"
        return f"{self.name} выключен!"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "device_type": self.device_type,
            "is_on": self.is_on
        }


class Light(Device):
    def __init__(self, name, brightness):
        super().__init__(name, "light")
        self.brightness = brightness

    def set_brightness(self, brightness):
        if not self.is_on:
            return "Для изменения яркости включите свет!"

        if brightness < 0 or brightness > 100:
            return "Яркость должна быть в диапазоне 0 - 100!"

        self.brightness = brightness
        return "Яркость установлена!"

    def to_dict(self):
        data = super().to_dict()
        data["brightness"] = self.brightness
        return data


class Thermostat(Device):
    def __init__(self, name, temperature):
        super().__init__(name, "thermostat")
        self.temperature = temperature

    def set_temperature(self, temperature):
        if not self.is_on:
            return "Для регулировки температуры включите термостат"

        if temperature < 10 or temperature > 30:
            return "Значение температуры должно быть в диапазоне 10 - 30"

        self.temperature = temperature
        return f"Температура успешно изменена! Текущее значение: {self.temperature}"

    def to_dict(self):
        data = super().to_dict()
        data["temperature"] = self.temperature
        return data


class DoorLock(Device):
    def __init__(self, name):
        super().__init__(name, "door_lock")
        self.is_locked = True

    def unlock(self):
        if not self.is_locked:
            return "Дверь уже открыта!"

        self.is_locked = False
        return f"{self.name} разблокирована!"

    def lock(self):
        if self.is_locked:
            return "Дверь уже закрыта!"

        self.is_locked = True
        return f"{self.name} заблокирована!"

    def to_dict(self):
        data = super().to_dict()
        data["is_locked"] = self.is_locked
        return data


class SmartHome:
    def __init__(self):
        self.devices = {}

    def add_device(self, device):
        self.devices[device.id] = device

    def get_device(self, device_id):
        if device_id not in self.devices:
            raise DeviceNotFoundError("Устройство не найдено!")

        return self.devices[device_id]

    def list_devices(self):
        return list(self.devices.values())

    def turn_on(self, device_id):
        return self.get_device(device_id).turn_on()

    def turn_off(self, device_id):
        return self.get_device(device_id).turn_off()

    def status(self, device_id):
        return self.get_device(device_id).status()

    def remove_device(self, device_id):
        self.get_device(device_id)
        self.devices.pop(device_id)
        return "Устройство удалено!"

    def save_devices(self):
        devices = []

        for device in self.devices.values():
            devices.append(device.to_dict())

        return devices

    def save_to_file(self):
        with open("devices.json", "w", encoding="utf-8") as file:
            json.dump(self.save_devices(), file, ensure_ascii=False, indent=4)

    def load_from_file(self):
        with open("devices.json", "r", encoding="utf-8") as file:
            devices = json.load(file)

        loaded_devices = {}

        for device in devices:
            if device["device_type"] == "light":
                obj = Light(device["name"], device["brightness"])
                obj.is_on = device["is_on"]

            elif device["device_type"] == "thermostat":
                obj = Thermostat(device["name"], device["temperature"])
                obj.is_on = device["is_on"]

            elif device["device_type"] == "door_lock":
                obj = DoorLock(device["name"])
                obj.is_on = device["is_on"]
                obj.is_locked = device["is_locked"]

            else:
                continue

            obj.id = device["id"]
            loaded_devices[obj.id] = obj

        self.devices = loaded_devices

        if loaded_devices:
            Device.next_id = max(loaded_devices) + 1


class DeviceNotFoundError(Exception):
    pass
