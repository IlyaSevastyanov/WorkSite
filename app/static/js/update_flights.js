function updateFlights(routeId) {
    const flightsContainer = document.getElementById('flightsContainer');
    const flightSelect = document.getElementById('flight');
    const flightDetails = document.getElementById('flightDetails');
    const busInfo = document.getElementById('busInfo');

    if (routeId) {
        flightsContainer.style.display = 'block';
        flightSelect.innerHTML = '<option value="">Загрузка рейсов...</option>';
        flightDetails.style.display = 'none';
        busInfo.innerHTML = '';

        fetch(`/get_flights/${routeId}`)
            .then(response => response.json())
            .then(data => {
                flightSelect.innerHTML = '<option value="">Выберите рейс</option>';
                data.flights.forEach(flight => {
                    const option = document.createElement('option');
                    option.value = flight.id;
                    option.textContent = `${flight.date} ${flight.time}`;
                    flightSelect.appendChild(option);
                });

                flightSelect.onchange = () => {
                    const selectedFlight = data.flights.find(f => f.id == flightSelect.value);
                    if (selectedFlight) {
                        flightDetails.style.display = 'block';
                        busInfo.innerHTML = `
                            <strong>Автобус:</strong> ${selectedFlight.bus_model} (${selectedFlight.bus_number})<br>
                            <strong>Вместимость:</strong> ${selectedFlight.capacity}<br>
                            <strong>Стоимость:</strong> ${selectedFlight.price} руб.
                        `;
                    } else {
                        flightDetails.style.display = 'none';
                        busInfo.innerHTML = '';
                    }
                };
            })
            .catch(error => {
                console.error('Ошибка загрузки рейсов:', error);
                flightSelect.innerHTML = '<option value="">Ошибка загрузки рейсов</option>';
            });
    } else {
        flightsContainer.style.display = 'none';
        flightDetails.style.display = 'none';
    }
}
