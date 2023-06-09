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
            //window.alert(data.status);
            //console.log(data);
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

    var forgotPasswordContainer = document.getElementById("forgotPwdContainer");
    var forgotPasswordButton = document.getElementById("forgotPasswordButton");
    forgotPasswordButton.addEventListener("click", function(event) {
        event.preventDefault();
        let label = document.createElement("label");
        label.textContent = "Enter your email:";
        let passwordTxt = document.createElement("input");
        passwordTxt.setAttribute("type", "text");
        let passwordSubmit = document.createElement("button")
        passwordSubmit.textContent = "Submit"
        
        //Ensure only one instance of the children is appended
        let check = document.querySelector("#forgotPwdContainer input")
        if (!check) {
            forgotPasswordContainer.appendChild(label);
            forgotPasswordContainer.appendChild(passwordTxt);
            forgotPasswordContainer.appendChild(passwordSubmit);
        }

        passwordSubmit.addEventListener("click", function(event) {
            event.preventDefault();
            if (passwordTxt.value.length == 0) {
                window.alert("Empty email!")
                return;
            }
            let formData = new FormData();
            formData.append("email", passwordTxt.value)
            fetch("/send_otp_forgot", {
                method:"POST",
                body:formData
            })
            .then(response => response.json())
            .then(data => {
                
                if (data.status === "success") {
                    window.alert("OTP sent to your email!")
                    window.location.href = "/change_pwd";
                } else {
                    window.alert(data.message);
                }
            })
            .catch(error => {
                console.error("Error", error);
            });
        });




    });

});