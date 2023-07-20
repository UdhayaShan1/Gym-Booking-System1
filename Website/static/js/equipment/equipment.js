document.addEventListener("DOMContentLoaded", function() {
    var equipmentContainer = document.getElementById("equipment");
    let weightHeader = document.createElement("h2");
    weightHeader.textContent = "Weights";
    equipmentContainer.appendChild(weightHeader);

    fetch("/fetchequipmentweight")
        .then(response => response.json())
        .then(data => {
            for (let key in data) {
                let equipmentDiv = document.createElement("div");
                equipmentDiv.classList.add("equipment-container");

                let equipmentName = document.createElement("h3");
                equipmentName.classList.add("equipment-name");
                equipmentName.textContent = key;

                equipmentDiv.appendChild(equipmentName);

                for (let weight in data[key]) {
                    let weightInfo = document.createElement("p");
                    weightInfo.classList.add("equipment-info");
                    weightInfo.textContent = weight + " kg Count: " + data[key][weight];

                    equipmentDiv.appendChild(weightInfo);
                }

                equipmentContainer.appendChild(equipmentDiv);
            }

            fetch("/fetchequipmentothers")
                .then(response => response.json())
                .then(data => {
                    let otherHeader = document.createElement("h2");
                    otherHeader.textContent = "Other Equipment";
                    equipmentContainer.appendChild(otherHeader);

                    for (let key in data) {
                        let equipmentDiv = document.createElement("div");
                        equipmentDiv.classList.add("equipment-container");

                        let equipmentName = document.createElement("h3");
                        equipmentName.classList.add("equipment-name");
                        equipmentName.textContent = key;

                        equipmentDiv.appendChild(equipmentName);

                        if (data[key][0] === 0) {
                            let equipmentStatus = document.createElement("p");
                            equipmentStatus.classList.add("equipment-status");
                            equipmentStatus.textContent = "Not Functioning";

                            let commentStatus = document.createElement("p");
                            commentStatus.classList.add("equipment-comment");
                            commentStatus.textContent = "Comments: " + data[key][1];

                            equipmentDiv.appendChild(equipmentStatus);
                            equipmentDiv.appendChild(commentStatus);
                        } else {
                            let equipmentStatus = document.createElement("p");
                            equipmentStatus.classList.add("equipment-info");
                            equipmentStatus.textContent = "Usable!";

                            equipmentDiv.appendChild(equipmentStatus);
                        }

                        equipmentContainer.appendChild(equipmentDiv);
                    }
                });
        });
});
