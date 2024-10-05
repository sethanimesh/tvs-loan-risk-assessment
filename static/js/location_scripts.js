if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(showPosition, showError);
        } else {
            alert("Geolocation is not supported by this browser.");
        }
    
        function showPosition(position) {
            const lat = position.coords.latitude;
            const long = position.coords.longitude;
    
            document.getElementById("lat").innerHTML = "Latitude: " + lat;
            document.getElementById("long").innerHTML = "Longitude: " + long;
    
            getCity(lat, long).then(city => {
                document.getElementById("city").innerHTML = "City: " + city;
                storeLocation(lat, long, city);
            });
        }
    
        function getCity(lat, long) {
            const url = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${long}`;
            return fetch(url)
                .then(response => response.json())
                .then(data => {
                    const city = data.address.city || data.address.town || data.address.village || 'Vellore';
                    return city;
                })
                .catch(() => 'Vellore'); // Default to Vellore in case of error
        }
    
        function showError(error) {
            switch(error.code) {
                case error.PERMISSION_DENIED:
                    alert("User denied the request for Geolocation. Showing default city.");
                    break;
                case error.POSITION_UNAVAILABLE:
                    alert("Location information is unavailable. Showing default city.");
                    break;
                case error.TIMEOUT:
                    alert("The request to get user location timed out. Showing default city.");
                    break;
                case error.UNKNOWN_ERROR:
                    alert("An unknown error occurred. Showing default city.");
                    break;
            }
        }
    
        function storeLocation(lat, long, city) {
            $.ajax({
                type: "POST",
                url: "/store_location", 
                data: JSON.stringify({ latitude: lat, longitude: long, city: city }),
                contentType: "application/json",
                success: function(response) {
                    console.log("Location stored successfully");
                },
                error: function(err) {
                    console.error("Error storing location", err);
                }
            });
        }
    
        function redirectToPsychometric() {
            window.location.href = "/psychometric";
        }