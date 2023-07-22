document.addEventListener("DOMContentLoaded", function() {
    var emailCell = document.getElementById("email1");
    var nameCell = document.getElementById("name");
    var roomCell = document.getElementById("room");
    var spotterNameCell = document.getElementById("spotterName");
    var spotterRoomCell = document.getElementById("spotterRoom");

    var reportButton = document.getElementById("reports");
    reportButton.addEventListener("click", function(e) {
        e.preventDefault();
        window.location.href = "/report";
    })

    var equipmentButton = document.getElementById("equipment")
    equipmentButton.addEventListener("click", function(e) {
        e.preventDefault();
        window.location.href = "/equipmentpage"
    })

    var editBookingButton = document.getElementById("editBookingButton");
    editBookingButton.addEventListener("click", function(e) {
        e.preventDefault();
        window.location.href = "/edit_bookings";
    });

    var profileButton = document.getElementById("profileButton");
    profileButton.addEventListener("click", function(event) {
        event.preventDefault();
        window.location.href = "/profile";
    });




    let logoutButton = document.getElementById("logoutButton");
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
            if (data.email === null) {
                emailCell.textContent = "No Email Set";
            } else {
                emailCell.textContent = data.email;
            }


            if (data.name === null) {
                nameCell.textContent = "No Name Set";
            } else {
                nameCell.textContent = data.name;
            }


            if (data.roomNo === null) {
                roomCell.textContent = "No RC Room Number Set";
            } else {
                roomCell.textContent = data.roomNo;
            }


            if (data.spotterName === null) {
                spotterNameCell.textContent = "No Spotter Name Set";
            } else {
                spotterNameCell.textContent = data.spotterName;
            }


            if (data.spotterRoomNo === null) {
                spotterRoomCell.textContent = "No Spotter Room Number Set";
            } else {
                spotterRoomCell.textContent = data.spotterRoomNo;
            }


        })
        .catch(error => {
            console.error("Error", error);
            window.alert(data.message);
        });


    var nameChange = document.getElementById("nameButton")
    nameChange.addEventListener("click", function(event) {
        event.preventDefault();
        var nameText = document.createElement("input");
        nameText.setAttribute("id", "nameText");
        nameText.setAttribute("type", "text");

        var nameSubmit = document.createElement("button");
        nameSubmit.setAttribute("id", "nameSubmit");
        nameSubmit.textContent = "Submit";

        var checkFirst = document.querySelector("#name input");
        if (!checkFirst) {
            nameCell.appendChild(nameText);
            nameCell.appendChild(nameSubmit);
        }

        nameSubmit.addEventListener("click", function(event) {
            event.preventDefault();
            var formData = new FormData();
            var newName = nameText.value;
            if (newName.length == 0) {
                window.alert("Empty name..")
                return;
            }
            formData.append("name", nameText.value);
            fetch("/update_name", {
                method : "POST",
                body : formData
            })
            .then(response => response.json())
            .then(data => {window.alert(data.message);
                if (data.status === "success") {
                    nameCell.removeChild(nameText);
                    nameCell.removeChild(nameSubmit)
                    nameCell.textContent = newName;
                }
                else {
                    window.location.href = "/profile";
                }

                
            })
        })

    });

    var roomChange = document.getElementById("roomButton")
    roomChange.addEventListener("click", function(event) {
        event.preventDefault();
        var roomText = document.createElement("input");
        roomText.setAttribute("id", "roomText");
        roomText.setAttribute("type", "text");

        var roomSubmit = document.createElement("button");
        roomSubmit.setAttribute("id", "roomSubmit");
        roomSubmit.textContent = "Submit";

        var checkFirst = document.querySelector("#room input");
        if (!checkFirst) {
            roomCell.appendChild(roomText);
            roomCell.appendChild(roomSubmit);
        }

        roomSubmit.addEventListener("click", function(event) {
            event.preventDefault();
            var formData = new FormData();
            var newRoom = roomText.value;
            if (newRoom.length == 0) {
                window.alert("Empty room number..")
                return;
            }
            formData.append("room", newRoom);
            fetch("/update_room", {
                method : "POST",
                body : formData
            })
            .then(response => response.json())
            .then(data => {window.alert(data.message);
                if (data.status === "success") {
                    roomCell.removeChild(roomText);
                    roomCell.removeChild(roomSubmit)
                    roomCell.textContent = newRoom;
                }
                else {
                    window.location.href = "/profile";
                }   
            })
        })

    });

    var spotterChange = document.getElementById("spotterNameButton")
    spotterChange.addEventListener("click", function(event) {
        event.preventDefault();
        var spotterText = document.createElement("input");
        spotterText.setAttribute("id", "spotterText");
        spotterText.setAttribute("type", "text");

        var spotterSubmit = document.createElement("button");
        spotterSubmit.setAttribute("id", "spotterSubmit");
        spotterSubmit.textContent = "Submit";

        var checkFirst = document.querySelector("#spotterName input");
        if (!checkFirst) {
            spotterNameCell.appendChild(spotterText);
            spotterNameCell.appendChild(spotterSubmit);
        }

        spotterSubmit.addEventListener("click", function(event) {
            event.preventDefault();
            var formData = new FormData();
            var newSpotter = spotterText.value;
            if (newSpotter.length == 0) {
                window.alert("Empty spotter name..")
                return;
            }
            formData.append("spotterName", spotterText.value);
            fetch("/update_spotter", {
                method : "POST",
                body : formData
            })
            .then(response => response.json())
            .then(data => {window.alert(data.message);
                if (data.status === "success") {
                    spotterNameCell.removeChild(spotterText);
                    spotterNameCell.removeChild(spotterSubmit)
                    spotterNameCell.textContent = newSpotter;
                }
                else {
                    window.location.href = "/profile";
                }   
            })
        })

    });

    var spotterRoomChange = document.getElementById("spotterRoomButton")
    spotterRoomChange.addEventListener("click", function(event) {
        event.preventDefault();
        var spotterRoomText = document.createElement("input");
        spotterRoomText.setAttribute("id", "spotterRoomText");
        spotterRoomText.setAttribute("type", "text");

        var spotterRoomSubmit = document.createElement("button");
        spotterRoomSubmit.setAttribute("id", "spotterRoomSubmit");
        spotterRoomSubmit.textContent = "Submit";

        var checkFirst = document.querySelector("#spotterRoom input");
        if (!checkFirst) {
            spotterRoomCell.appendChild(spotterRoomText);
            spotterRoomCell.appendChild(spotterRoomSubmit);
        }

        spotterRoomSubmit.addEventListener("click", function(event) {
            event.preventDefault();
            var formData = new FormData();
            var newSpotterRoom = spotterRoomText.value;
            if (newSpotterRoom.length == 0) {
                window.alert("Empty spotter room number..")
                return;
            }
            formData.append("spotterRoom", spotterRoomText.value);
            fetch("/update_spotter_room", {
                method : "POST",
                body : formData
            })
            .then(response => response.json())
            .then(data => {window.alert(data.message);
                if (data.status === "success") {
                    spotterRoomCell.removeChild(spotterRoomText);
                    spotterRoomCell.removeChild(spotterRoomSubmit)
                    spotterRoomCell.textContent = newSpotterRoom;
                }
                else {
                    window.location.href = "/profile";
                }   
            })
        })

    });

    var backButton = document.getElementById("goBack");
    backButton.addEventListener("click", function(event) {
        event.preventDefault();
        window.location.href = "/main";
    });

    var changePassword = document.getElementById("changePwd");
    changePassword.addEventListener("click", function(event) {
        event.preventDefault();
        fetch("/send_otp_changepwd")
        .then(response => response.json())
        .then(data => {
            window.alert("OTP sent to your email!")
            window.location.href = "/change_pwd";
        })
    })



    //Nav-Bar Buttons
    var bookingButton = document.getElementById("bookingButton");
    bookingButton.addEventListener("click", function(event) {
        event.preventDefault();
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
