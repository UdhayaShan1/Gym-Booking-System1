document.addEventListener("DOMContentLoaded", function() {
    var equipmentButton = document.getElementById("equipment")
    equipmentButton.addEventListener("click", function(event) {
        event.preventDefault()
        window.location.href = "/equipmentpage"
    })



    var reportButton = document.getElementById("reports")
    reportButton.addEventListener("click", function(event) {
        event.preventDefault();
        window.location.href = "/report";
    })

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
            document.getElementById("profileDirector").textContent = "Proceed to book by clicking Booking!";
            document.getElementById("email").textContent = data.name;
        }
    })
    .catch(error => {console.error("Error", error)});

    var profileButton = document.getElementById("profileButton");
    profileButton.addEventListener("click", function(event) {
        event.preventDefault();
        window.location.href = "/profile";
    });

    var bookingButton = document.getElementById("bookingButton");
    bookingButton.addEventListener("click", function(event) {
        event.preventDefault()
        fetch("/profile_completed")
        .then(response => response.json())
        .then(data => 
            {
                if (data.status === "success") {
                    window.location.href = "/booking_page";
                }
                else {
                    window.alert(data.message)
                    window.location.href = "/profile"
                }
            })
        .catch(error => {console.error("Error", error);
        window.alert("Error, try again");
        })
    });

    var editBookingButton = document.getElementById("editBookingButton");
    editBookingButton.addEventListener("click", function(event) {
        event.preventDefault();
        window.location.href = "/edit_bookings";
    });

    var changePassword = document.getElementById("changePassword");
    changePassword.addEventListener("click", function(event) {
        event.preventDefault();
        fetch("/send_otp_changepwd")
        .then(response => response.json())
        .then(data => {
            window.alert("OTP sent to your email!")
            window.location.href = "/change_pwd";
        })
    })

    



});