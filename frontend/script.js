console.log("script.js запустился");
const devices = document.getElementById("devices");

const deviceName = document.getElementById("device-name");
const deviceType = document.getElementById("device-type");

const deviceBrightness = document.getElementById("device-brightness");
const deviceTemperature = document.getElementById("device-temperature");

const usernameInput = document.getElementById("username");
const passwordInput = document.getElementById("password"); 
const registerBtn = document.getElementById("registerBtn");
const registerMessage = document.getElementById("registerMessage");

const loginUsername = document.getElementById("loginUsername")
const loginPassword = document.getElementById("loginPassword")
const loginBtn = document.getElementById("loginBtn")
const loginMessage = document.getElementById("loginMessage")

console.log(registerBtn);

registerBtn.addEventListener("click", function() {
    const username = usernameInput.value;
    const password = passwordInput.value;

    console.log(username);
    console.log(password);

    console.log(JSON.stringify({
        username: username,
        password: password
    }));

    fetch("/register", {
        method: "POST",
        headers: {
            "Content-Type": "application/json" 
        },
        body: JSON.stringify({
            username: username,
            password: password
        })
    })
    .then(function(response) {
        return response.json().then(function(data) {
            return {
                ok: response.ok,
                data: data
            };
        });
    })
    .then(function(result) {
        if (result.ok) {
            registerMessage.textContent = result.data.message;
            registerMessage.className = "register-success";
        } else {
            registerMessage.textContent = result.data.detail;
            registerMessage.className = "register-error"
        }
    });
});

loginBtn.addEventListener("click", function() {
    const username = loginUsername.value;
    const password = loginPassword.value;

    fetch("/login", {
        method: "POST",
        headers: {
            "Content-type": "application/json"
        },
        body: JSON.stringify({
            username: username,
            password: password
        })
    })
    .then(function(response) {
        return response.json();
    })
    .then(function(data) {
        console.log(data);
        localStorage.setItem("token", data.access_token);
    
        fetch("/me", {
            headers: {
                "Authorization": "Bearer " + localStorage.getItem("token")
            }
        })
        .then(function(response) {
            return response.json();
        })
        .then(function(data) {
            console.log(data);
        });
    });
});
const brightnessField = document.getElementById("brightness-field");
const temperatureField = document.getElementById("temperature-field");
deviceType.addEventListener("change", function() {
    if (deviceType.value === "light") {
        brightnessField.style.display = "block";
        temperatureField.style.display = "none";
    }
    if (deviceType.value === "thermostat") {
        brightnessField.style.display = "none";
        temperatureField.style.display = "block";
    }
    if (deviceType.value === "door_lock") {
        brightnessField.style.display = "none";
        temperatureField.style.display = "none";
    }
});
brightnessField.style.display = "block";
temperatureField.style.display = "none";

const addDeviceButton = document.getElementById("add-device-button")

const lights = document.getElementById("lights");
const thermostats = document.getElementById("thermostats");
const locks = document.getElementById("locks");

addDeviceButton.addEventListener("click", function() {
    const name = deviceName.value;
    const type = deviceType.value;

    if (name.trim() === "") {
        alert("Введите название устройства");
        return;
    }

    if (type === "light" && deviceBrightness.value === "") {
        alert("Введите яркость");
        return;
    }
    if (type === "thermostat" && deviceTemperature.value === "") {
        alert("Введите температуру");
        return;
    }

    let brightness = null;
    let temperature = null;
    let is_locked = null;

    if (type === "light") {
        brightness = deviceBrightness.value;
    }
    if (type === "thermostat") {
        temperature = deviceTemperature.value;
    }
    if (type === "door_lock") {
        is_locked = false;
    }

    fetch("/devices", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            name: name,
            device_type: type,
            brightness: brightness,
            temperature: temperature,
            is_locked: is_locked
        })
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(error => {
                alert(error.detail[0].msg);
                return null;
            });
        }

        return response.json();
    })

    .then(data => {
        if (data === null) {
            return;
        }

    console.log(data);
    loadDevices();

    deviceName.value = "";
    deviceBrightness.value = "";
    deviceTemperature.value = "";
});
});

function getPowerStatus(isOn) {
    if (isOn) {
        return "● Включено";
    } else {
        return "● Выключено";
    }
}

function getBrightnessText(brightness) {
    return "Яркость: " + brightness + "%"
}

function getTemperatureText(temperature) {
    return "Темп: " + temperature + "°C"
}

function getLockStatus(isLocked) {
    if (isLocked) {
        return "🔒 Заблокировано";
    } else {
        return "🔓 Разблокировано";
    }
}

function loadDevices() {
    lights.textContent = "";
    thermostats.textContent = "";
    locks.textContent = "";

    fetch("/devices", {
        headers: {
            "Authorization": "Bearer " + localStorage.getItem("token")
        }
    })
        .then(response => {
            if (!response.ok) {
                console.log("Пользователь не авторизован");
                return;
            }
            return response.json();
        })
        .then(data => {
            for (let i = 0; i < data.length; i++) {
                    const card = document.createElement("div");

                    if (data[i].device_type === "light") {
                        card.classList.add("card-light");
                    }
                    if (data[i].device_type === "thermostat") {
                        card.classList.add("card-thermostat");
                    }
                    if (data[i].device_type === "door_lock") {
                        card.classList.add("card-door");
                    }

                    const button = document.createElement("button");
                    const deleteButton = document.createElement("button");
                    deleteButton.textContent = "Удалить"
                    deleteButton.addEventListener("click", function() {
                        if (!confirm("Удалить устройство?")) {
                            return;
                        }
                        fetch("/devices/" + data[i].id, {
                            method: "DELETE"
                        })
                        .then(response => {
                            return response.json();
                        })
                        .then(deletedDevice => {
                            console.log(deletedDevice);
                            loadDevices();
                        });
                    });

                    button.addEventListener("click", function() {
                        if (data[i].is_on) {
                            fetch("/devices/" + data[i].id + "/off", {
                                method: "PUT"
                            })
                            .then(response => {
                                return response.json();
                            })
                            .then(updatedDevice => {
                                data[i].is_on = updatedDevice.is_on;
                                is_on.textContent = getPowerStatus(updatedDevice.is_on);  
                                
                                is_on.classList.remove("device-on", "device-off");
                                if (updatedDevice.is_on) {
                                    is_on.classList.add("device-on");
                                }  else {
                                    is_on.classList.add("device-off");
                                }

                                button.classList.remove("button-on", "button-off");

                                if (updatedDevice.is_on) {
                                    button.classList.add("button-on");
                                } else {
                                    button.classList.add("button-off");
                                }

                                if (updatedDevice.is_on) {
                                    button.textContent = "Выключить";
                                } else {
                                    button.textContent = "Включить"
                                }
                            })
                        } else {
                            fetch("/devices/" + data[i].id + "/on", {
                                method: "PUT"
                                })
                                .then(response => {
                                    return response.json();
                            })
                            .then(updatedDevice => {
                                data[i].is_on = updatedDevice.is_on;
                                is_on.textContent = 'is_on: ' + updatedDevice.is_on;
                                is_on.textContent = getPowerStatus(updatedDevice.is_on);

                                button.classList.remove("button-on", "button-off");

                                if (updatedDevice.is_on) {
                                    button.classList.add("button-on");
                                } else {
                                    button.classList.add("button-off");
                                }

                                if (updatedDevice.is_on) {
                                    is_on.classList.add("device-on");
                                } else {
                                    is_on.classList.add("device-off");
                                }

                                if (updatedDevice.is_on) {
                                    button.textContent = "Выключить";
                                } else {
                                    button.textContent = "Включить"
                                }
                                console.log(updatedDevice);
                            });
                        }
                    });
                    const title = document.createElement("h3");
                    const type = document.createElement("p");
                    const id = document.createElement("p");
                    const is_on = document.createElement("p");
                    
                    title.textContent = data[i].name;
                    type.textContent = data[i].device_type;
                    id.textContent = 'ID: ' + data[i].id;
                    is_on.textContent = getPowerStatus(data[i].is_on);
                    if (data[i].is_on) {
                        button.textContent = "Выключить";
                    } else {
                        button.textContent = "Включить";
                    }
                    if (data[i].is_on) {
                        is_on.classList.add("device-on");
                    } else {
                        is_on.classList.add("device-off");
                    }
                    if (data[i].is_on) {
                        button.classList.add("button-on");
                    } else {
                        button.classList.add("button-off");
                    }

                    console.log(button.className);

                    card.appendChild(title);
                    card.appendChild(type);
                    card.appendChild(id);
                    card.appendChild(is_on);
                    card.appendChild(button);
                    card.appendChild(deleteButton);
                    if (data[i].device_type === 'light') {
                        const brightness = document.createElement("p");
                        const brightnessInput = document.createElement("input");
                        brightnessInput.type = "number";
                        brightnessInput.min = 0;
                        brightnessInput.max = 100;
                        brightnessInput.value = data[i].brightness;
                        card.appendChild(brightnessInput);
                        const brightnessButton = document.createElement("button");
                        brightnessButton.textContent = "Изменить яркость";
                        brightnessButton.addEventListener("click", function() {
                            fetch("/devices/" + data[i].id + "/brightness", {
                                method: "PUT",
                                headers: {
                                    "Content-Type": "application/json"
                                },
                                body: JSON.stringify({
                                    brightness: brightnessInput.value
                                })
                            })
                            .then(response => {
                                return response.json();
                            })
                            .then(updatedDevice => {
                                console.log(updatedDevice);
                                data[i].brightness = updatedDevice.brightness;
                                brightness.textContent = getBrightnessText(updatedDevice.brightness);
                            })
                        });
                        brightness.textContent = getBrightnessText(data[i].brightness);
                        card.appendChild(brightness);
                        card.appendChild(brightnessButton);
                    }
                    if (data[i].device_type === 'thermostat') {
                        const temperature = document.createElement("p");
                        const temperatureInput = document.createElement("input")
                        temperatureInput.type = "number"
                        temperatureInput.min = 10;
                        temperatureInput.max = 30;
                        temperatureInput.value = data[i].temperature;
                        card.appendChild(temperatureInput);
                        const temperatureButton = document.createElement("button");
                        temperatureButton.textContent = "Изменить температуру";
                        temperatureButton.addEventListener("click", function() {
                            fetch("/devices/" + data[i].id + "/temperature", {
                                method: "PUT",
                                headers: {
                                    "Content-type": "application/json"
                                },
                                body: JSON.stringify({
                                    temperature: temperatureInput.value
                                })
                            })
                            .then(response => {
                                return response.json();
                            })
                            .then(updatedDevice => {
                                console.log(updatedDevice);
                                data[i].temperature = updatedDevice.temperature;
                                temperature.textContent = getTemperatureText(updatedDevice.temperature);
                            })
                        });
                        temperature.textContent = getTemperatureText(data[i].temperature);
                        card.appendChild(temperature);
                        card.appendChild(temperatureButton);
                    }
                    if (data[i].device_type === 'door_lock') {
                        const is_locked = document.createElement("p");
                        is_locked.textContent = getLockStatus(data[i].is_locked);
                        if (data[i].is_locked) {
                            is_locked.classList.add("device-locked");
                        } else {
                            is_locked.classList.add("device-unlocked");
                        }
                        card.appendChild(is_locked);
                        const door_lockButton = document.createElement("button")
                        door_lockButton.textContent = "Изменить состояние замка"
                        card.appendChild(door_lockButton)
                        door_lockButton.addEventListener("click", function() {
                            if (data[i].is_locked) {
                                fetch("/devices/" + data[i].id + "/unlock", {
                                    method: "PUT"
                                })
                                .then(response => {
                                    return response.json();
                                })
                                .then(updatedDevice => {
                                    console.log(updatedDevice);
                                    data[i].is_locked = updatedDevice.is_locked;
                                    is_locked.textContent = getLockStatus(updatedDevice.is_locked);
                                    is_locked.classList.remove("device-locked");
                                    is_locked.classList.add("device-unlocked");
                                })
                            } else {
                                fetch("/devices/" + data[i].id + "/lock", {
                                    method: "PUT"
                                })
                                .then(response => {
                                    return response.json()
                                })
                                .then(updatedDevice => {
                                    console.log(updatedDevice);
                                    data[i].is_locked = updatedDevice.is_locked;
                                    is_locked.textContent = getLockStatus(updatedDevice.is_locked);
                                    is_locked.classList.remove("device-unlocked");
                                    is_locked.classList.add("device-locked");
                                })
                            }
                        })
                    }
                    if (data[i].device_type === "light") {
                        lights.appendChild(card);
                    }
                    if (data[i].device_type === "thermostat") {
                        thermostats.appendChild(card);
                    }
                    if (data[i].device_type === "door_lock") {
                        locks.appendChild(card);
                    }
                };
        });
}

loadDevices();

const categoryButtons = document.querySelectorAll(".category-button");

categoryButtons.forEach(function(button) {
    button.addEventListener("click", function() {
        const category = button.parentElement;
        const content = category.querySelector("div");
        const arrow = button.querySelector("span");

        if (content.style.display === "none") {
            content.style.display = "grid";
            arrow.textContent = "▼";
        } else {
            content.style.display = "none";
            arrow.textContent = "▲";
        }
    });
});
