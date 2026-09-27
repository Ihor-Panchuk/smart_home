const button = document.getElementById("loadButton");
const devices = document.getElementById("devices")

button.addEventListener('click', function() {
    devices.textContent = "";
    fetch("/devices")
        .then(response => {
            response.json().then(data => {
                for (let i = 0; i < data.length; i++) {
                    devices.innerHTML += data[i].name + "<br>";
                };
            });
        });
});