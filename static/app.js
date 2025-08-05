const map = L.map('map').setView([37.8, -96], 4);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

let carriers = [];
let markersLayer = L.markerClusterGroup().addTo(map);

// Fetch data from Flask
fetch("/data")
    .then(res => res.json())
    .then(data => {
        carriers = data.filter(d => d.Lat && d.Lng);
        populateStateDropdown(carriers);
        plotPoints(carriers);
    });

function populateStateDropdown(data) {
    const states = [...new Set(data.map(d => d.State))].sort();
    const dropdown = document.getElementById('stateFilter');
    dropdown.innerHTML = `<option value="">All States</option>` +
                         states.map(s => `<option value="${s}">${s}</option>`).join("");
    
    dropdown.addEventListener('change', () => applyFilters());
    document.getElementById('searchBox').addEventListener('input', () => applyFilters());
}

function getMarkerColor(d) {
    if (d.Petroleum_Products == 1 || d.Petroleum_Products == "1") return "red";
    if (d.Chemical_Products == 1 || d.Chemical_Products == "1") return "blue";
    if (d.Biofuel == 1 || d.Biofuel == "1") return "green";
    return "gray";
}

function plotPoints(data) {
    markersLayer.clearLayers();

    data.forEach(d => {
        const lat = parseFloat(d.Lat), lng = parseFloat(d.Lng);
        if (!lat || !lng) return;

        const marker = L.circleMarker([lat, lng], {
            radius: 6,
            fillColor: getMarkerColor(d),
            color: "#000",
            weight: 1,
            opacity: 1,
            fillOpacity: 0.8
        });

        marker.bindPopup(`
            <b>${d.Operator_Name}</b><br>
            Facility: ${d.Facility_Name || "N/A"}<br>
            Address: ${d.Physical_Facility_Address || "N/A"}, ${d.State}<br>
            Liquid: ${d.Liquid_Type_Detail || "N/A"}<br>
            Capacity: ${d.Capacity_Gallons || "N/A"} gallons
        `);

        markersLayer.addLayer(marker);
    });

    map.addLayer(markersLayer);
}

function applyFilters() {
    const stateFilter = document.getElementById('stateFilter').value;
    const searchTerm = document.getElementById('searchBox').value.toLowerCase();

    const filtered = carriers.filter(d => {
        const matchState = stateFilter ? d.State === stateFilter : true;
        const matchSearch = searchTerm ? d.Operator_Name.toLowerCase().includes(searchTerm) : true;
        return matchState && matchSearch;
    });

    plotPoints(filtered);
}
