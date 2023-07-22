document.addEventListener("DOMContentLoaded", function() {
    let homeButton = document.getElementById("homeButton");
    let profileButton = document.getElementById("profileButton");
    let bookingButton = document.getElementById("bookingButton");
    let editBookingButton = document.getElementById("editBookingButton");
    let reports = document.getElementById("reports");
    let equipment = document.getElementById("equipment");
    let logoutButton = document.getElementById("logoutButton");

    homeButton.addEventListener("click", function(event) {
        event.preventDefault();
        window.location.href = "/main";
    })

    equipment.addEventListener("click", function(event) {
        event.preventDefault()
        window.location.href = "/equipmentpage"
    })

    reports.addEventListener("click", function(event) {
        event.preventDefault();
        window.location.href = "/report";
    })

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

    profileButton.addEventListener("click", function(event) {
        event.preventDefault();
        window.location.href = "/profile";
    });

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

    editBookingButton.addEventListener("click", function(event) {
        event.preventDefault();
        window.location.href = "/edit_bookings";
    });
});