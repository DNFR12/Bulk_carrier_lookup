from flask import Flask, render_template, request
import pandas as pd
import folium
from folium import Popup

csv_path = "Liquid_Bulk_Carriers_With_Coords.csv"
df = pd.read_csv(csv_path)

# Ensure valid Lat/Lng
df["Lat"] = pd.to_numeric(df["Lat"], errors="coerce")
df["Lng"] = pd.to_numeric(df["Lng"], errors="coerce")
df = df.dropna(subset=["Lat", "Lng"])

app = Flask(__name__)

def create_map(filtered_df):
    fmap = folium.Map(location=[37.8, -96], zoom_start=4)

    # Use a small Google-style blue pin
    small_icon_url = "https://maps.gstatic.com/mapfiles/ms2/micons/blue-dot.png"

    for _, row in filtered_df.iterrows():
        popup_html = f"""
        <div style="width:320px; white-space: normal; line-height:1.2; font-size:13px;">
            <b style="font-size:14px;">{row['Operator_Name']}</b><br>
            Facility: {row['Facility_Name']}<br>
            Address: {row['Physical_Facility_Address']}, {row['State']}<br>
            Liquid: {row.get('Liquid_Type_Detail','N/A')}<br>
            Capacity: {row.get('Capacity_Gallons','N/A')} gallons
        </div>
        """

        popup = Popup(popup_html, max_width=350, min_width=300)

        folium.Marker(
            location=[row["Lat"], row["Lng"]],
            popup=popup,
            icon=folium.CustomIcon(small_icon_url, icon_size=(18, 18))
        ).add_to(fmap)

    return fmap._repr_html_()

@app.route("/", methods=["GET"])
def home():
    state = request.args.get("state")
    states = sorted(df["State"].dropna().unique())
    filtered_df = df[df["State"] == state] if state else df

    map_html = create_map(filtered_df)
    company_names = filtered_df["Operator_Name"].dropna().unique().tolist()

    return render_template("index.html",
                           map=map_html,
                           states=states,
                           selected=state,
                           company_names=company_names)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
