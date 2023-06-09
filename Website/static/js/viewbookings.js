document.addEventListener("DOMContentLoaded", function() {
    var buttonContainer = document.getElementById("buttonContainer");
    fetch("/fetch_bookings", {
        method:"POST"
    })
    .then(response => response.json())
    .then(data => {
        if (data.length == 0){
            let bookingDirector = document.getElementById("bookingDirector");
            bookingDirector.textContent = "You do not have any booked slots at the moment!";
        }
        else {
            for (let i = 0; i < data.length; i += 1) {
                let slotButton = document.createElement("button");
                slotButton.setAttribute("id", data[i]);
                slotButton.textContent = data[i];
                buttonContainer.appendChild(slotButton);
                slotButton.addEventListener("click", function(event) {
                    event.preventDefault();
                    let formData = new FormData();
                    let date = slotButton.textContent.split(" ")[0]
                    let time = slotButton.textContent.split(" ")[1]
                    formData.append("date", date);
                    formData.append("time", time);
                    fetch("/unbook", {
                        method:"POST",
                        body:formData
                    })
                    .then(response => response.json())
                    .then(data => 
                    {
                    window.alert(data.message)
                    window.location.href = "/edit_bookings"})
                })
            }
    }
    })

    var goBack = document.getElementById("backButton");
    goBack.addEventListener("click", function(event) {
        event.preventDefault();
        window.location.href = "/main";
    })

    var logoutButton = document.getElementById("logout");
    logoutButton.addEventListener("click", function(event) {
      event.preventDefault();
      fetch("/logout", {
        method: "POST"
      })
      .then(response => response.json())
      .then(data => {
        if (data.status === "success") {
          window.alert(data.message)
          window.location.href = "/";
        }
      })
    })
});