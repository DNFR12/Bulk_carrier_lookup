from flask import Flask, render_template, request
import pandas as pd
import folium

# === Load Data ===
csv_path = "Liquid_Bulk_Carriers_With_Coords.csv"
df = pd.read_csv(csv_path)

# Clean up data
df["Lat"] = pd.to_numeric(df["Lat"], errors="coerce")
df["Lng"] = pd.to_numeric(df["Lng"], errors="coerce")
df = df.dropna(subset=["Lat", "Lng"])

app = Flask(__name__)

# === Function to Create Map ===
def create_map(filtered_df):
    fmap = folium.Map(location=[37.8, -96], zoom_start=4)

    # Custom icons based on product type
    for _, row in filtered_df.iterrows():
        if row.get("Petroleum_Products") == 1:
            icon_url = "/static/icons/red.png"
        elif row.get("Chemical_Products") == 1:
            icon_url = "/static/icons/blue.png"
        elif row.get("Biofuel") == 1:
            icon_url = "/static/icons/green.png"
        else:
            icon_url = "/static/icons/gray.png"

        popup_html = f"""
        <b>{row['Operator_Name']}</b><br>
        Facility: {row['Facility_Name']}<br>
        Address: {row['Physical_Facility_Address']}, {row['State']}<br>
        Liquid: {row.get('Liquid_Type_Detail','N/A')}<br>
        Capacity: {row.get('Capacity_Gallons','N/A')} gallons
        """

        folium.Marker(
            location=[row["Lat"], row["Lng"]],
            popup=popup_html,
            icon=folium.CustomIcon(icon_url, icon_size=(30, 30))
        ).add_to(fmap)

    return fmap._repr_html_()

# === Routes ===
@app.route("/", methods=["GET"])
def home():
    state = request.args.get("state")
    states = sorted(df["State"].dropna().unique())

    if state:
        filtered_df = df[df["State"] == state]
    else:
        filtered_df = df

    # Generate map
    map_html = create_map(filtered_df)

    # Convert filtered data to list of dicts for table
    company_data = filtered_df.to_dict(orient="records")

    return render_template("index.html", 
                           map=map_html, 
                           states=states, 
                           selected=state, 
                           companies=company_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
