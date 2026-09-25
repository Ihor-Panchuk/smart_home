import json

# ============================================================
# БАЗОВЫЙ КЛАСС
# ============================================================


class Device:
    # Атрибут класса.
    # Общий счётчик для всех создаваемых устройств.
    next_id = 1


def __init__(self, name, device_type):
    # self — конкретный объект, который сейчас создаётся.
    # Каждое устройство получает собственные значения этих атрибутов.
    self.id = Device.next_id
    self.name = name
    self.device_type = device_type
    self.is_on = False

    # После создания устройства увеличиваем общий счётчик.
    # Поэтому следующее устройство получит следующий id.
    Device.next_id += 1


def turn_on(self):
    # Меняем состояние конкретного объекта.
    self.is_on = True
    return f"{self.name} включен!"


def turn_off(self):
    self.is_on = False
    return f"{self.name} выключен!"


def status(self):
    # Проверяем состояние объекта и возвращаем сообщение.
    if self.is_on:
        return f"{self.name} включен!"
    else:
        return f"{self.name} выключен!"


def to_dict(self):
    # Преобразуем объект в обычный словарь.
    # Это удобно для дальнейшего сохранения в JSON.
    return {
        "id": self.id,
        "name": self.name,
        "device_type": self.device_type,
        "is_on": self.is_on
    }
# ============================================================
# НАСЛЕДОВАНИЕ: LIGHT
# ============================================================


class Light(Device):
    # Light наследуется от Device.
    # Поэтому получает его атрибуты и методы.

    def __init__(self, name, brightness):
        # super() вызывает __init__ родительского класса Device.
        # Не нужно повторно писать создание id, name, device_type и is_on.
        super().__init__(name, "light")

    # Добавляем собственное свойство, которого нет у Device.
        self.brightness = brightness


def set_brightness(self, brightness):
    # Яркость можно менять только у включённого света.
    if not self.is_on:
        return "Для изменения яркости включите свет!"

    # Проверяем допустимый диапазон.
    if brightness < 0 or brightness > 100:
        return "Яркость должна быть в диапазоне 0 - 100!"

    # Если проверки пройдены — изменяем состояние объекта.
    self.brightness = brightness
    return "Яркость установлена!"


def to_dict(self):
    # Получаем словарь с базовыми данными от Device.
    # Это повторное использование родительской логики.
    data = super().to_dict()

    # Добавляем специфичное для Light поле.
    data["brightness"] = self.brightness

    return data
# ============================================================
# НАСЛЕДОВАНИЕ: THERMOSTAT
# ============================================================


class Thermostat(Device):

    def __init__(self, name, temperature):
        # Передаём базовую часть объекта родительскому классу.
        super().__init__(name, "thermostat")

    # Собственное свойство Thermostat.
        self.temperature = temperature


def set_temperature(self, temperature):
    # Температуру можно регулировать только у включённого термостата.
    if not self.is_on:
        return "Для регулировки температуры включите термостат"

    # Проверяем допустимый диапазон температуры.
    if temperature < 10 or temperature > 30:
        return "Значение температуры должно быть в диапазоне 10 - 30"

    self.temperature = temperature
    return f"Температура успешно измененна! Текущее значенние {self.temperature}"


def to_dict(self):
    # Берём базовые данные Device.
    data = super().to_dict()

    # Добавляем собственное поле Thermostat.
    data["temperature"] = self.temperature

    return data
# ============================================================
# НАСЛЕДОВАНИЕ: DOOR LOCK
# ============================================================


class DoorLock(Device):

    def __init__(self, name):
        # Используем конструктор родительского класса.
        super().__init__(name, "door_lock")

    # Замок при создании считается закрытым.
        self.is_locked = True


def unlock(self):
    # Если замок уже открыт — ничего менять не нужно.
    if not self.is_locked:
        return "Дверь уже открыта!"

    self.is_locked = False
    return "Front Door разблокирована!"


def lock(self):
    # Проверяем, не закрыт ли замок уже.
    if self.is_locked:
        return "Дверь уже закрыта!"

    self.is_locked = True
    return f"{self.name} заблокирована!"


def to_dict(self):
    # Получаем базовые данные Device.
    data = super().to_dict()

    # Добавляем состояние замка.
    data["is_locked"] = self.is_locked

    return data
# ============================================================
# КЛАСС-КОНТЕЙНЕР ДЛЯ УСТРОЙСТВ
# ============================================================


class SmartHome:

    def __init__(self):
        # Словарь хранит устройства по их id.
        #
        # Пример:
        # {
        #     1: light_object,
        #     2: thermostat_object
        # }
        self.devices = {}


def add_device(self, device):
    # Добавляем объект в словарь.
    # Ключом выступает id устройства.
    self.devices[device.id] = device


def get_device(self, device_id):
    # Проверяем наличие устройства в словаре.
    if device_id in self.devices:
        return self.devices[device_id]

    # Если устройства нет — выбрасываем собственное исключение.
    raise DeviceNotFoundError("Устройство не найдено!")


def list_devices(self):
    # values() возвращает все объекты устройств.
    # list() превращает их в обычный список.
    return list(self.devices.values())


def turn_on(self, device_id):
    # Сначала получаем объект устройства.
    device = self.get_device(device_id)

    # Затем вызываем его метод.
    return device.turn_on()


def turn_off(self, device_id):
    device = self.get_device(device_id)
    return device.turn_off()


def status(self, device_id):
    device = self.get_device(device_id)
    return device.status()


def remove_device(self, device_id):
    # Получаем устройство.
    device = self.get_device(device_id)

    if device:
        # pop() удаляет устройство из словаря.
        self.devices.pop(device_id, None)
        return "Устройство удалено!"
    else:
        return "Устройство не найдено!"

# ========================================================
# СЕРИАЛИЗАЦИЯ
# ========================================================


def save_devices(self):
    # Создаём список обычных словарей.
    devices = []

    # Перебираем все объекты устройств.
    for device in self.devices.values():

        # Каждый объект сам преобразует себя в словарь
        # через свой метод to_dict().
        devices.append(device.to_dict())

    return devices


def save_to_file(self):
    # Открываем файл для записи.
    with open("devices.json", "w") as file:

        # Получаем список словарей.
        devices = self.save_devices()

        # Сохраняем Python-объекты в JSON.
        json.dump(devices, file)

# ========================================================
# ДЕСЕРИАЛИЗАЦИЯ
# ========================================================


def load_from_file(self):
    # Открываем JSON-файл для чтения.
    with open("devices.json", "r") as file:

        # JSON превращается обратно в Python-объекты:
        # JSON → список словарей.
        devices = json.load(file)

        # Здесь будем собирать восстановленные объекты.
        loaded_devices = {}

        # Перебираем сохранённые словари.
        for device in devices:

            # По device_type определяем,
            # объект какого класса нужно создать.
            if device["device_type"] == "light":
                loaded_devices[device["id"]] = Light(
                    device["name"],
                    device["brightness"]
                )

            if device["device_type"] == "thermostat":
                loaded_devices[device["id"]] = Thermostat(
                    device["name"],
                    device["temperature"]
                )

            if device["device_type"] == "door_lock":
                loaded_devices[device["id"]] = DoorLock(
                    device["name"]
                )

        return loaded_devices
# ============================================================
# СОБСТВЕННОЕ ИСКЛЮЧЕНИЕ
# ============================================================


class DeviceNotFoundError(Exception):
    # Пустой класс-исключение.
    # Он нужен, чтобы отдельно обозначить ситуацию,
    # когда запрошенного устройства нет.
    pass

# 1. Device → базовый класс
# 2. Light, Thermostat, DoorLock → наследники
# 3. super() → обращение к родительской логике
# 4. to_dict() → объект → словарь
# 5. json.dump() → Python → JSON
# 6. json.load() → JSON → Python
# 7. SmartHome → композиция: объект хранит другие объекты
# 8. DeviceNotFoundError → собственное исключение
