//Vanilla JS

document.addEventListener("DOMContentLoaded", function() {
    var registerForm = document.getElementById("registerForm");
    registerForm.addEventListener('submit', function(event) {
        event.preventDefault();
        var email = document.getElementById("email").value;
        var password = document.getElementById("password").value;
        var confirmPassword = document.getElementById("confirmPass").value;
        if (password != confirmPassword) {
            window.alert("Passwords do not match")
            document.getElementById('password').value = '';
            document.getElementById('confirmPass').value = '';
            return;
        }
        var formData = new FormData();
        formData.append('email', email)
        formData.append('password', password)

        fetch("/register", {
            method: "POST",
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            if (data.status === "success") {
                window.alert(data.message)
                window.location.href = "/login"
            }
            else {
                window.alert(data.message)
                document.getElementById('email').value = '';
            }
        })
        .catch(error => {console.error("Error", error)});
    });

});