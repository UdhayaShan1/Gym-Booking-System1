document.addEventListener("DOMContentLoaded", function() {
    var buttonContainer = document.getElementById("buttonContainer");
  
    fetch("/fetch_dates", {
      method: "POST"
    })
    .then(response => response.json())
    .then(data => {
      console.log(data);
      for (let i = 0; i < data.length; i += 1) {
        {
          let newDateButton = document.createElement("button");
          newDateButton.setAttribute("id", i);
          newDateButton.textContent = data[i];
          buttonContainer.appendChild(newDateButton);
  
          // Add event listener to each button
          newDateButton.addEventListener("click", function(event) {
            event.preventDefault();
            let formData = new FormData();
            formData.append("date", newDateButton.textContent);
  
            fetch("/selected_date", {
              method: "POST",
              body: formData
            })
            .then(response => response.json())
            .then(data => {
              if (data.status === "success") {
                window.location.href = "/booking_times";
              }
            })
            .catch(error => {
              console.error("Error", error);
            });
          });
        };
      }
    })
    .catch(error => {
      console.error("Error", error);
      window.alert("Failed to fetch dates");
    });
  });
  