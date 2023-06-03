document.addEventListener("DOMContentLoaded", function() {
    var loginButton = document.getElementById("logoutButton");
    loginButton.addEventListener("click", function(event){
        event.preventDefault();
        fetch("/logout", {
            method: "POST"
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                window.alert("You have logged out");
                window.location.href = "/";
            }
            else {
                window.alert("Error logging out");
            }
        })
        .catch(error => {
            console.error("Error", error);
            window.alert("Error logging out");
        })
    });

    fetch("/user_details", {method:"POST"})
    .then(response => response.json())
    .then(data => {
        document.getElementById("email").textContent = data.email;
    })
    .catch(error => {console.error("Error", error)});



});