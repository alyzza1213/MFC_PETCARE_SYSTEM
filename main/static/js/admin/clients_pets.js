// Functions for client/pet buttons
function viewClient(name) {
    alert('View Client: ' + name);
}

function viewPet(name) {
    alert('View Pet: ' + name);
}

document.addEventListener("DOMContentLoaded", function () {
    const searchInput = document.getElementById("searchInput");
    const cards = document.querySelectorAll(".searchable");

    searchInput.addEventListener("keyup", function () {
        const filter = searchInput.value.toLowerCase();

        cards.forEach(card => {
            const text = card.innerText.toLowerCase();
            card.style.display = text.includes(filter) ? "flex" : "none";
        });
    });
});
