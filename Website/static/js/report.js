document.addEventListener("DOMContentLoaded", function() {
    var form = document.getElementById("feedbackForm");
    form.addEventListener("submit", function(event) {
        event.preventDefault();
        let formData = new FormData(form);

        fetch("/report", {
            method:"POST",
            body:formData
        })
        .then(response => response.json())
        .then(data => {
            window.alert(data.message);
        })

    });

    var viewReport = document.getElementById("viewReports");
    viewReport.addEventListener("click", function(event) {
        event.preventDefault();
        window.location.href = "/viewreports";
    })
});