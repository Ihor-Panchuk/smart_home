const button = document.getElementById("loadButton");
const devices = document.getElementById("devices");

function loadDevices() {
    devices.textContent = "";

    fetch("/devices")
        .then(response => {
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
                                is_on.textContent = 'is_on: ' + updatedDevice.is_on;  
                                
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
                                is_on.classList.remove("device-on", "device-off");

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
                    is_on.textContent = 'is_on: ' + data[i].is_on;
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
                                brightness.textContent = 'brightness: ' + updatedDevice.brightness;
                            })
                        });
                        brightness.textContent = 'brightness: ' + data[i].brightness;
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
                                temperature.textContent = "temperature: " + updatedDevice.temperature;
                            })
                        });
                        temperature.textContent = 'temperature: ' + data[i].temperature;
                        card.appendChild(temperature);
                        card.appendChild(temperatureButton);
                    }
                    if (data[i].device_type === 'door_lock') {
                        const is_locked = document.createElement("p");
                        is_locked.textContent = 'is_locked: ' + data[i].is_locked;
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
                                    is_locked.textContent = 'is_locked: ' + updatedDevice.is_locked;
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
                                    is_locked.textContent = 'is_locked: ' + updatedDevice.is_locked;
                                })
                            }
                        })
                    }
                    devices.appendChild(card);
                };
        });
}

loadDevices();