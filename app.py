from flask import Flask, render_template_string, request
import pandas as pd
import folium

# === Load Data ===
csv_path = "Liquid_Bulk_Carriers_With_Coords.csv"
df = pd.read_csv(csv_path)

# Ensure Lat/Lng are numeric
df["Lat"] = pd.to_numeric(df["Lat"], errors="coerce")
df["Lng"] = pd.to_numeric(df["Lng"], errors="coerce")
df = df.dropna(subset=["Lat", "Lng"])

# === Flask App ===
app = Flask(__name__)

# === HTML Template (No JS) ===
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Bulk Liquid Carrier Lookup</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; }
        h2 { text-align: center; }
        form { text-align: center; margin: 10px; }
        #map { height: 90vh; width: 100%; }
    </style>
</head>
<body>
    <h2>Bulk Liquid Carrier Lookup</h2>
    <form method="GET" action="/">
        <label for="state">Filter by State:</label>
        <select name="state">
            <option value="">All States</option>
            {% for s in states %}
            <option value="{{s}}" {% if selected == s %}selected{% endif %}>{{s}}</option>
            {% endfor %}
        </select>
        <button type="submit">Filter</button>
    </form>
    <div id="map">{{ map|safe }}</div>
</body>
</html>
"""

def create_map(filtered_df):
    # Create folium map centered on US
    fmap = folium.Map(location=[37.8, -96], zoom_start=4)

    # Add markers
    for _, row in filtered_df.iterrows():
        color = "gray"
        if row.get("Petroleum_Products") == 1: color = "red"
        elif row.get("Chemical_Products") == 1: color = "blue"
        elif row.get("Biofuel") == 1: color = "green"

        popup_html = f"""
        <b>{row['Operator_Name']}</b><br>
        Facility: {row['Facility_Name']}<br>
        Address: {row['Physical_Facility_Address']}, {row['State']}<br>
        Liquid: {row.get('Liquid_Type_Detail','N/A')}<br>
        Capacity: {row.get('Capacity_Gallons','N/A')} gallons
        """
        folium.CircleMarker(
            location=[row["Lat"], row["Lng"]],
            radius=5,
            color="black",
            fill=True,
            fill_color=color,
            fill_opacity=0.8,
            popup=popup_html
        ).add_to(fmap)

    return fmap._repr_html_()

@app.route("/")
def home():
    state = request.args.get("state")
    states = sorted(df["State"].dropna().unique())

    if state:
        filtered_df = df[df["State"] == state]
    else:
        filtered_df = df

    map_html = create_map(filtered_df)
    return render_template_string(HTML_TEMPLATE, map=map_html, states=states, selected=state)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
