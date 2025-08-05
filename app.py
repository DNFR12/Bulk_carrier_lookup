from flask import Flask, render_template, jsonify
import pandas as pd

app = Flask(__name__)

# === Load Data ===
df = pd.read_csv("bulk_carriers.csv")

# Keep only necessary columns
columns_to_keep = [
    "Operator_Name", "Facility_Name", "Physical_Facility_Address", "State",
    "Truck", "Chemical_Products", "Petroleum_Products", "Liquified_Gasses_Products",
    "NGL", "Biofuel", "Vegetable_Oil", "Waste", "Liquid_Type_Detail", "Capacity_Gallons", "Lat", "Lng"
]
df = df[columns_to_keep]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/data")
def get_data():
    return jsonify(df.to_dict(orient="records"))

if __name__ == "__main__":
    app.run(debug=True)
