from flask import Flask, render_template, request
import pandas as pd
import folium

# === Load Data ===
csv_path = "Liquid_Bulk_Carriers_With_Coords.csv"
df = pd.read_csv(csv_path)

# Ensure valid Lat/Lng
df["Lat"] = pd.to_numeric(df["Lat"], errors="coerce")
df["Lng"] = pd.to_numeric(df["Lng"], errors="coerce")
df = df.dropna(subset=["Lat", "Lng"])

app = Flask(__name__)

# === Function to Create Map ===
def create_map(filtered_df):
    fmap = folium.Map(location=[37.8, -96], zoom_start=4)

    for _, row in filtered_df.iterrows():
        # Choose color based on product type
        if row.get("Petroleum_Products") == 1:
            color, icon = "red", "tint"
        elif row.get("Chemical_Products") == 1:
            color, icon = "blue", "flask"
        elif row.get("Biofuel") == 1:
            color, icon = "green", "leaf"
        else:
            color, icon = "gray", "info-sign"

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
            icon=folium.Icon(color=color, icon=icon, prefix='fa')
        ).add_to(fmap)

    return fmap._repr_html_()

# === Routes ===
@app.route("/", methods=["GET"])
def home():
    state = request.args.get("state")
    states = sorted(df["State"].dropna().unique())

    filtered_df = df[df["State"] == state] if state else df

    map_html = create_map(filtered_df)
    company_data = filtered_df.to_dict(orient="records")

    return render_template("index.html", 
                           map=map_html, 
                           states=states, 
                           selected=state, 
                           companies=company_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
