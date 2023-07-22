document.addEventListener("DOMContentLoaded", function() {
    let backButton = document.getElementById("backButton");
    backButton.addEventListener("click", function(event) {
        event.preventDefault();
        window.location.href = "/report";
    })



    let reportContainer = document.getElementById("reportContainer");
    fetch("/fetchreports", {
        method: "POST"
    })
    .then(response => response.json())
    .then(data => {
        for (let i = 0; i < data.length; i += 1) {
            let report = data[i][0];
            let reportId = data[i][1];
            let responded = data[i][2];
            
            // Create the header element
            let reportHeader = document.createElement("h3");
            if (responded === 0) {
                reportHeader.textContent = "Report ID: " + reportId + " | Report has no responses yet";
            } else {
                reportHeader.textContent = "Report ID: " + reportId + " | Report has " + responded + " responses";
            }
            reportHeader.classList.add("report-header"); // Add the CSS class
            
            // Create the element for the report
            let textButton = document.createElement("button")
            textButton.textContent = report;
            //let textReport = document.createTextNode(report);
            textButton.addEventListener("click", function(event) {
                event.preventDefault();
                let formData = new FormData();
                formData.append("id", reportId);
                fetch("/selectedreport", {
                    method:"POST",
                    body : formData
                })
                .then(response => response.json())
                .then(data => {
                    window.location.href = "/viewresponses"
                })




            })


            // Append the header and value to the container
            reportContainer.appendChild(reportHeader);
            reportContainer.appendChild(textButton);
            
            // Add a <br> element for the blank line
            let lineBreak = document.createElement("br");
            reportContainer.appendChild(lineBreak);
        }
    });
});
