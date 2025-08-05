// === Initialize Map ===
const map = L.map('map').setView([37.8, -96], 4);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

let carriers = [];
let markers = [];

// === Load Data from Flask Endpoint ===
fetch("/data")
  .then(response => response.json())
  .then(data => {
    carriers = data.filter(d => d.Lat && d.Lng);
    populateStateDropdown(carriers);
    plotPoints(carriers);
  });

// === Populate State Dropdown ===
function populateStateDropdown(data) {
  const states = [...new Set(data.map(d => d.State))].sort();
  const dropdown = document.getElementById('stateFilter');
  dropdown.innerHTML = `<option value="">All States</option>` +
                       states.map(s => `<option value="${s}">${s}</option>`).join("");
  dropdown.addEventListener('change', () => {
    const filtered = dropdown.value ? data.filter(d => d.State === dropdown.value) : data;
    plotPoints(filtered);
  });
}

// === Color by Product Type ===
function getMarkerColor(d) {
  if (d.Petroleum_Products === 1 || d.Petroleum_Products === "1") return "red";
  if (d.Chemical_Products === 1 || d.Chemical_Products === "1") return "blue";
  if (d.Biofuel === 1 || d.Biofuel === "1") return "green";
  return "gray";
}

// === Plot Points ===
function plotPoints(data) {
  markers.forEach(m => map.removeLayer(m));
  markers = [];

  data.forEach(d => {
    if (!d.Lat || !d.Lng) return;

    const marker = L.circleMarker([d.Lat, d.Lng], {
      radius: 6,
      fillColor: getMarkerColor(d),
      color: "#000",
      weight: 1,
      opacity: 1,
      fillOpacity: 0.8
    }).addTo(map);

    marker.bindPopup(`
      <b>${d.Operator_Name}</b><br>
      Facility: ${d.Facility_Name || "N/A"}<br>
      Address: ${d.Physical_Facility_Address || "N/A"}, ${d.State}<br>
      Liquid: ${d.Liquid_Type_Detail || "N/A"}<br>
      Capacity: ${d.Capacity_Gallons || "N/A"} gallons
    `);

    markers.push(marker);
  });
}
