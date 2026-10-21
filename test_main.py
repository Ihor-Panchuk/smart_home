from fastapi.testclient import TestClient
from main import DeviceData, app, create_access_token
import pytest


def test_device_name():
    device = DeviceData(name="  Kitchen Light  ", device_type="light")

    assert device.name == "Kitchen Light"


def test_empty_device_name():
    with pytest.raises(ValueError):
        DeviceData(name="   ", device_type="light")


def test_invalid_brightness():
    with pytest.raises(ValueError):
        DeviceData(name="Kitchen Light", device_type="light", brightness=150)


def test_zero_brightness():
    device = DeviceData(name="  Kitchen Light  ",
                        device_type="light", brightness=0)

    assert device.brightness == 0


def test_max_brightness():
    device = DeviceData(name="Kitchen Light",
                        device_type="light", brightness=100)

    assert device.brightness == 100


def test_invalid_temperature():
    with pytest.raises(ValueError):
        DeviceData(name="Kitchen Thermostat",
                   device_type="thermostat", temperature=5)


def test_max_temperature():
    device = DeviceData(name="Kitchen Thermostat",
                        device_type="thermostat", temperature=30)

    assert device.temperature == 30


def test_min_temperature():
    device = DeviceData(name="Kitchen Thermostat",
                        device_type="thermostat", temperature=10)

    assert device.temperature == 10


client = TestClient(app)


def test_devices_require_auth():
    response = client.get("/devices")

    assert response.status_code == 401


def test_devices_invalid_token():
    response = client.get(
        "/devices", headers={"Authorization": "Bearer invalid-token"})

    assert response.status_code == 401


def test_devices_valid_token(monkeypatch):
    monkeypatch.setattr("main.JWT_SECRET_KEY", "test-secret")

    token = create_access_token(user_id=1, username="test_user")
    monkeypatch.setattr("main.database.get_devices", lambda user_id: [])
    response = client.get(
        "/devices",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
