
document.addEventListener('DOMContentLoaded', function () {
    var calendarEl = document.getElementById('calendar');

    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        height: 600,
        events: "{% url 'admin_appointments_json' %}",
        eventClick: function(info) {
            alert(
                "Client: " + info.event.extendedProps.client +
                "\nPet: " + info.event.extendedProps.pet +
                "\nStatus: " + info.event.extendedProps.status
            );
        }
    });

    calendar.render();
});
