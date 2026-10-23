import pytest
from fastapi.testclient import TestClient

import main
from main import DeviceData, app, create_access_token

client = TestClient(app)

USER_ID = 7
DEVICE = {
    "id": 1,
    "name": "Kitchen Light",
    "device_type": "light",
    "is_on": False,
    "brightness": 50,
    "temperature": None,
    "is_locked": None,
    "user_id": USER_ID,
}


@pytest.fixture
def auth_headers(monkeypatch):
    """Return authorization headers signed with a test-only JWT secret."""
    monkeypatch.setattr(main, "JWT_SECRET_KEY", "test-secret")
    token = create_access_token(user_id=USER_ID, username="test_user")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def device():
    return DEVICE.copy()


# Device model validation


def test_device_name_is_trimmed():
    parsed = DeviceData(name="  Kitchen Light  ", device_type="light")

    assert parsed.name == "Kitchen Light"


@pytest.mark.parametrize("name", ["", "   ", "\t\n"])
def test_device_name_cannot_be_blank(name):
    with pytest.raises(ValueError):
        DeviceData(name=name, device_type="light")


@pytest.mark.parametrize("brightness", [-1, 101])
def test_brightness_must_be_between_zero_and_one_hundred(brightness):
    with pytest.raises(ValueError):
        DeviceData(name="Kitchen Light", device_type="light", brightness=brightness)


@pytest.mark.parametrize("brightness", [0, 100])
def test_brightness_accepts_boundary_values(brightness):
    parsed = DeviceData(name="Kitchen Light", device_type="light", brightness=brightness)

    assert parsed.brightness == brightness


@pytest.mark.parametrize("temperature", [9, 31])
def test_temperature_must_be_between_ten_and_thirty(temperature):
    with pytest.raises(ValueError):
        DeviceData(
            name="Kitchen Thermostat",
            device_type="thermostat",
            temperature=temperature,
        )


@pytest.mark.parametrize("temperature", [10, 30])
def test_temperature_accepts_boundary_values(temperature):
    parsed = DeviceData(
        name="Kitchen Thermostat",
        device_type="thermostat",
        temperature=temperature,
    )

    assert parsed.temperature == temperature


# Authentication and user endpoints


def test_devices_require_authentication():
    response = client.get("/devices")

    assert response.status_code == 401


def test_devices_reject_invalid_token():
    response = client.get(
        "/devices",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401


def test_valid_token_lists_only_current_users_devices(monkeypatch, auth_headers, device):
    calls = []

    def fake_get_devices(user_id):
        calls.append(user_id)
        return [device]

    monkeypatch.setattr(main.database, "get_devices", fake_get_devices)

    response = client.get("/devices", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == [device]
    assert calls == [USER_ID]


def test_me_returns_authenticated_username(auth_headers):
    response = client.get("/me", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == {"username": "test_user"}


def test_register_creates_user_with_hashed_password(monkeypatch):
    monkeypatch.setattr(main.password_hash, "hash", lambda password: f"hashed:{password}")
    calls = []
    monkeypatch.setattr(
        main.database,
        "create_user",
        lambda username, password_hash: calls.append((username, password_hash)) or True,
    )

    response = client.post(
        "/register",
        json={"username": "  new_user  ", "password": "secret"},
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Пользователь создан"}
    assert calls == [("new_user", "hashed:secret")]


def test_register_rejects_duplicate_username(monkeypatch):
    monkeypatch.setattr(main.password_hash, "hash", lambda password: "hashed")
    monkeypatch.setattr(main.database, "create_user", lambda username, password_hash: False)

    response = client.post(
        "/register",
        json={"username": "existing_user", "password": "secret"},
    )

    assert response.status_code == 400


def test_register_rejects_blank_credentials():
    response = client.post("/register", json={"username": "   ", "password": "secret"})

    assert response.status_code == 422


def test_login_returns_access_token(monkeypatch):
    monkeypatch.setattr(
        main.database,
        "get_user_by_username",
        lambda username: (USER_ID, username, "stored-hash"),
    )
    monkeypatch.setattr(main.password_hash, "verify", lambda password, stored: True)
    monkeypatch.setattr(main, "JWT_SECRET_KEY", "test-secret")

    response = client.post(
        "/login",
        json={"username": "test_user", "password": "secret"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "Вход выполнен"
    assert isinstance(body["access_token"], str)
    assert body["access_token"]


@pytest.mark.parametrize(
    "user_record",
    [None, (USER_ID, "test_user", "stored-hash")],
    ids=["unknown-user", "wrong-password"],
)
def test_login_rejects_invalid_credentials(monkeypatch, user_record):
    monkeypatch.setattr(main.database, "get_user_by_username", lambda username: user_record)
    monkeypatch.setattr(main.password_hash, "verify", lambda password, stored: False)

    response = client.post(
        "/login",
        json={"username": "test_user", "password": "wrong"},
    )

    assert response.status_code == 401


# Device read endpoints


def test_get_device_returns_device(monkeypatch, auth_headers, device):
    calls = []
    monkeypatch.setattr(
        main.database,
        "get_device",
        lambda device_id, user_id: calls.append((device_id, user_id)) or device,
    )

    response = client.get("/devices/1", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == device
    assert calls == [(1, USER_ID)]


def test_get_missing_device_returns_404(monkeypatch, auth_headers):
    monkeypatch.setattr(main.database, "get_device", lambda device_id, user_id: None)

    response = client.get("/devices/999", headers=auth_headers)

    assert response.status_code == 404


def test_get_devices_by_type(monkeypatch, auth_headers, device):
    monkeypatch.setattr(
        main.database,
        "get_devices_by_type",
        lambda device_type, user_id: [device] if device_type == "light" and user_id == USER_ID else [],
    )

    response = client.get("/devices/type/light", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == [device]


def test_get_devices_by_power_status(monkeypatch, auth_headers, device):
    monkeypatch.setattr(
        main.database,
        "get_devices_by_status",
        lambda is_on, user_id: [device] if is_on is False and user_id == USER_ID else [],
    )

    response = client.get("/devices/is_on/false", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == [device]


@pytest.mark.parametrize(
    ("device_type", "expected"),
    [
        ("light", {"id": 1, "is_on": False, "brightness": 50}),
        ("thermostat", {"id": 1, "is_on": True, "temperature": 21}),
        ("door_lock", {"id": 1, "is_locked": True}),
    ],
)
def test_device_status_returns_type_specific_fields(
    monkeypatch, auth_headers, device, device_type, expected
):
    device.update(expected)
    device["device_type"] = device_type
    monkeypatch.setattr(main.database, "get_device", lambda device_id, user_id: device)

    response = client.get("/devices/1/status", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == expected


def test_device_status_rejects_unknown_device_type(monkeypatch, auth_headers, device):
    device["device_type"] = "unknown"
    monkeypatch.setattr(main.database, "get_device", lambda device_id, user_id: device)

    response = client.get("/devices/1/status", headers=auth_headers)

    assert response.status_code == 400


# Device creation and validation


def test_create_light(monkeypatch, auth_headers, device):
    calls = []

    def fake_add_device(*args):
        calls.append(args)
        return device

    monkeypatch.setattr(main.database, "add_device", fake_add_device)

    response = client.post(
        "/devices",
        headers=auth_headers,
        json={"name": "Kitchen Light", "device_type": "light", "brightness": 50},
    )

    assert response.status_code == 200
    assert response.json() == device
    assert calls == [("Kitchen Light", "light", False, 50, None, None, USER_ID)]


@pytest.mark.parametrize(
    "payload",
    [
        {"name": "Lamp", "device_type": "unknown"},
        {"name": "Lamp", "device_type": "light", "temperature": 20},
        {"name": "Thermostat", "device_type": "thermostat", "brightness": 50},
        {"name": "Lock", "device_type": "door_lock", "temperature": 20},
        {"name": "Lock", "device_type": "door_lock", "brightness": 50},
        {"name": "Lamp", "device_type": "light", "is_locked": True},
    ],
)
def test_create_device_rejects_invalid_type_or_properties(
    monkeypatch, auth_headers, payload
):
    monkeypatch.setattr(
        main.database,
        "add_device",
        lambda *args: pytest.fail("database.add_device must not be called"),
    )

    response = client.post("/devices", headers=auth_headers, json=payload)

    assert response.status_code == 400


@pytest.mark.parametrize(
    "payload",
    [
        {"name": "Lamp", "device_type": "light", "brightness": 101},
        {"name": "Thermostat", "device_type": "thermostat", "temperature": 5},
        {"name": "   ", "device_type": "light"},
    ],
)
def test_create_device_rejects_invalid_field_values(auth_headers, payload):
    response = client.post("/devices", headers=auth_headers, json=payload)

    assert response.status_code == 422


# Device updates and deletion


def test_update_device_name(monkeypatch, auth_headers, device):
    calls = []
    monkeypatch.setattr(
        main.database,
        "update_device_name",
        lambda device_id, name, user_id: calls.append((device_id, name, user_id)) or device,
    )

    response = client.put(
        "/devices/1",
        headers=auth_headers,
        json={"name": "Updated Light"},
    )

    assert response.status_code == 200
    assert response.json() == device
    assert calls == [(1, "Updated Light", USER_ID)]


def test_update_missing_device_returns_404(monkeypatch, auth_headers):
    monkeypatch.setattr(main.database, "update_device_name", lambda *args: None)

    response = client.put(
        "/devices/999",
        headers=auth_headers,
        json={"name": "Missing"},
    )

    assert response.status_code == 404


@pytest.mark.parametrize(
    ("endpoint", "database_function", "expected_state"),
    [
        ("on", "turn_on_device", True),
        ("off", "turn_off_device", False),
    ],
)
def test_switch_device_power(
    monkeypatch, auth_headers, device, endpoint, database_function, expected_state
):
    updated = {**device, "is_on": expected_state}
    calls = []
    monkeypatch.setattr(
        main.database,
        database_function,
        lambda device_id, user_id: calls.append((device_id, user_id)) or updated,
    )

    response = client.put(f"/devices/1/{endpoint}", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == updated
    assert calls == [(1, USER_ID)]


@pytest.mark.parametrize(
    ("endpoint", "device_type", "payload", "database_function", "expected_key"),
    [
        ("brightness", "light", {"brightness": 75}, "update_brightness", "brightness"),
        ("temperature", "thermostat", {"temperature": 22}, "update_temperature", "temperature"),
    ],
)
def test_update_device_setting(
    monkeypatch,
    auth_headers,
    device,
    endpoint,
    device_type,
    payload,
    database_function,
    expected_key,
):
    device["device_type"] = device_type
    updated = {**device, **payload}
    calls = []
    monkeypatch.setattr(main.database, "get_device", lambda device_id, user_id: device)
    monkeypatch.setattr(
        main.database,
        database_function,
        lambda device_id, value, user_id: calls.append((device_id, value, user_id)) or updated,
    )

    response = client.put(f"/devices/1/{endpoint}", headers=auth_headers, json=payload)

    assert response.status_code == 200
    assert response.json() == updated
    assert calls == [(1, payload[expected_key], USER_ID)]


@pytest.mark.parametrize(
    ("endpoint", "device_type", "payload"),
    [
        ("brightness", "thermostat", {"brightness": 60}),
        ("temperature", "light", {"temperature": 20}),
    ],
)
def test_setting_cannot_be_applied_to_wrong_device_type(
    monkeypatch, auth_headers, device, endpoint, device_type, payload
):
    device["device_type"] = device_type
    monkeypatch.setattr(main.database, "get_device", lambda device_id, user_id: device)

    response = client.put(f"/devices/1/{endpoint}", headers=auth_headers, json=payload)

    assert response.status_code == 400


@pytest.mark.parametrize(
    ("endpoint", "database_function"),
    [
        ("lock", "lock_device"),
        ("unlock", "unlock_device"),
    ],
)
def test_lock_state_endpoints(monkeypatch, auth_headers, device, endpoint, database_function):
    device["device_type"] = "door_lock"
    updated = {**device, "is_locked": endpoint == "lock"}
    calls = []
    monkeypatch.setattr(main.database, "get_device", lambda device_id, user_id: device)
    monkeypatch.setattr(
        main.database,
        database_function,
        lambda device_id, user_id: calls.append((device_id, user_id)) or updated,
    )

    response = client.put(f"/devices/1/{endpoint}", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == updated
    assert calls == [(1, USER_ID)]


@pytest.mark.parametrize("endpoint", ["lock", "unlock"])
def test_lock_state_endpoints_reject_non_lock_device(
    monkeypatch, auth_headers, device, endpoint
):
    device["device_type"] = "light"
    monkeypatch.setattr(main.database, "get_device", lambda device_id, user_id: device)

    response = client.put(f"/devices/1/{endpoint}", headers=auth_headers)

    assert response.status_code == 400


def test_delete_device(monkeypatch, auth_headers, device):
    calls = []
    monkeypatch.setattr(
        main.database,
        "delete_device",
        lambda device_id, user_id: calls.append((device_id, user_id)) or device,
    )

    response = client.delete("/devices/1", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == device
    assert calls == [(1, USER_ID)]


def test_delete_missing_device_returns_404(monkeypatch, auth_headers):
    monkeypatch.setattr(main.database, "delete_device", lambda device_id, user_id: None)

    response = client.delete("/devices/999", headers=auth_headers)

    assert response.status_code == 404
