
function sortTable(n) {
    const table = document.getElementById("serviceTable");
    let switching = true, dir = "asc", switchcount = 0;
    while (switching) {
        switching = false;
        let rows = table.rows;
        for (let i = 1; i < rows.length - 1; i++) {
            let shouldSwitch = false;
            let x = rows[i].getElementsByTagName("TD")[n].firstElementChild.value.toLowerCase();
            let y = rows[i+1].getElementsByTagName("TD")[n].firstElementChild.value.toLowerCase();
            if ((dir === "asc" && x > y) || (dir === "desc" && x < y)) { shouldSwitch = true; break; }
        }
        if (shouldSwitch) {
            rows[i].parentNode.insertBefore(rows[i+1], rows[i]);
            switching = true; switchcount++;
        } else if (switchcount === 0 && dir === "asc") { dir = "desc"; switching = true; }
    }
}
