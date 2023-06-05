document.addEventListener("DOMContentLoaded", function() {
    var logoutButton = document.getElementById("logoutButton");
    logoutButton.addEventListener("click", function(event){
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

    fetch("/user_details")
    .then(response => response.json())
    .then(data => {
        if (data.name === null) {
            document.getElementById("profileDirector").textContent = "It appears your profile is not set, click Profile above!";
        }
        else {
            document.getElementById("email").textContent = ", " + data.name;
        }
    })
    .catch(error => {console.error("Error", error)});

    var profileButton = document.getElementById("profileButton");
    profileButton.addEventListener("click", function(event) {
        event.preventDefault();
        window.location.href = "/profile";
    })

    

    



});