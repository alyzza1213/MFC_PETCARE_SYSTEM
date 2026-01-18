function confirmAction(action, id) {
    const modal = document.getElementById("confirmModal");
    const text = document.getElementById("modalText");
    const form = document.getElementById("modalForm");

    if (action === "approve") {
        text.innerText = "Approve this appointment?";
        form.action = `/appointments/${id}/approve/`;
    } else {
        text.innerText = "Cancel this appointment?";
        form.action = `/appointments/${id}/cancel/`;
    }

    modal.style.display = "block";
}

function closeModal() {
    document.getElementById("confirmModal").style.display = "none";
}

function openReschedule(id) {
    window.location.href = `/appointments/${id}/reschedule/`;
}
