document.addEventListener("DOMContentLoaded", function() {
    let responseContainer = document.getElementById("responseContainer");

    fetch("/fetchresponses", {
        method: "POST"
    })
    .then(response => response.json())
    .then(data => {
        if (data.length === 0) {
            let responseHeader = document.createElement("h3");
            responseHeader.textContent = "No responses yet";
            responseContainer.appendChild(responseHeader);
        } else {
            for (let i = 0; i < data.length; i += 1) {
                let responseHeader = document.createElement("h3");
                responseHeader.textContent = data[i];
                responseHeader.classList.add("response-header"); // Add the CSS class
                responseContainer.appendChild(responseHeader);
            }
        }
    });
});
