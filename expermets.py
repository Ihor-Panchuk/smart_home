keys = ["id", "name", "device_type", "is_on"]
device = (5, "Kitchen Thermostat", "thermostat", False)
devices = [
    (1, "Kitchen Light", "light", True),
    (5, "Kitchen Thermostat", "thermostat", False),
    (6, "Front Door", "door_lock", True)
]


def devices_to_dict(devices):
    result = []
    for device in devices:
        dct = dict(zip(keys, device))
        result.append(dct)
    return result


print(devices_to_dict(devices))
