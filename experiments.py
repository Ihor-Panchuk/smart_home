import database

keys = ["id", "name", "device_type", "is_on"]
device = (5, "Kitchen Thermostat", "thermostat", False)
devices = [
    (1, "Kitchen Light", "light", True),
    (5, "Kitchen Thermostat", "thermostat", False),
    (6, "Front Door", "door_lock", True)
]


def get_devices():
    devices = database.get_devices()
    return devices


print(database.lock_device(1))
