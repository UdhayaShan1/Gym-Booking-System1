//Vanilla JS

document.addEventListener("DOMContentLoaded", function() {
    var registerForm = document.getElementById("registerForm");
    registerForm.addEventListener('submit', function(event) {
        event.preventDefault();
        var email = document.getElementById("email").value;
        var otp = document.getElementById("OTP").value;
        var password = document.getElementById("password").value;
        var confirmPassword = document.getElementById("confirmPass").value;
        if (email.length == 0 || otp.length == 0 || password.length == 0 || confirmPassword.length == 0) {
            window.alert("Some fields are empty!")
            return;
        }
        if (password != confirmPassword) {
            window.alert("Passwords do not match")
            document.getElementById('password').value = '';
            document.getElementById('confirmPass').value = '';
            return;
        }
        var formData = new FormData();
        formData.append('email', email);
        formData.append('password', password);
        formData.append('otp', otp);

        fetch("/register", {
            method: "POST",
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            if (data.status === "success") {
                window.alert(data.message);
                window.location.href = "/login";
            }
            else {
                window.alert(data.message);
                document.getElementById('email').value = '';
            }
        })
        .catch(error => {console.error("Error", error)});
    });


    var verifyButton = document.getElementById("verifyButton");
    verifyButton.addEventListener("click", function(event) {
        event.preventDefault();
        var email = document.getElementById("email").value;
        var formData = new FormData();
        formData.append('email', email);

        fetch("/send_otp", {
            method: "POST",
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            if (data.status === "success") {
                window.alert("OTP sent to your email");
            }
            else {
                window.alert(data.message);
            }
        })
        .catch(error => {
            console.error("Error", error);
            window.alert(data.message);
        });
    });

});