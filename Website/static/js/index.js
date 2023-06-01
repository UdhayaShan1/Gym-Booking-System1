document.addEventListener("DOMContentLoaded", function() {
    var registerButton = document.getElementById("registerButton");
    registerButton.addEventListener("click", function () {
      window.location.href = "/register"; // Redirect to the register page
    });

    var registerButton = document.getElementById("loginButton");
    registerButton.addEventListener("click", function () {
      window.location.href = "/login"; // Redirect to the register page
    });
});