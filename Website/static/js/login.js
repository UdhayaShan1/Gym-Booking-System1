document.addEventListener("DOMContentLoaded", function() {
    var loginButton = document.getElementById("loginForm");
    loginButton.addEventListener("submit", function(event) {
        event.preventDefault();
        var email = document.getElementById("email").value;
        var password = document.getElementById("password").value;
        if (email.length == 0 || password.length == 0) {
            window.alert("Some fields are empty");
            return;
        }
        var formData = new FormData();
        formData.append("email", email);
        formData.append("password", password);

        fetch("/login", {
            method:"POST",
            body:formData
        })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            if (data.status == "success") {
                window.location.href = "/main";
            } 
            else {
                window.alert(data.message)
            }

        })
        .catch(error => {console.error("Error", error);
        window.alert("Login failed");
    });
    });

});