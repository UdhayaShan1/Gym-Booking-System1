document.addEventListener("DOMContentLoaded", function() {
    var form = document.getElementById("eminemRecovery");
    form.addEventListener("submit", function(event) {
        event.preventDefault();
        let otpField = document.getElementById("otp");
        let pwdField = document.getElementById("newPwd");
        let cfmpwdField = document.getElementById("newPwdCfm");
        if (otpField.value.length == 0 || pwdField.value.length == 0 || cfmpwdField.value.length == 0) {
            window.alert("Some fields empty");
            return;
        }
        if (pwdField.value != cfmpwdField.value) {
            window.alert("Passwords do not match!")
            return;
        }
        let formData = new FormData();
        formData.append("otp", otpField.value)
        formData.append("pwd", pwdField.value)
        formData.append("cfmpwd", cfmpwdField.value)
        fetch("/send_newpwd", {
            method:"POST",
            body:formData
        })
        .then(response => response.json())
        .then(data => {
            window.alert(data.message)
            window.location.href = "/login";
        })
        .catch(error => {console.error("Error", error);
    });
        
    })
});