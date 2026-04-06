from flask import Flask, request, jsonify, render_template
import requests
import toml
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

# Load Google Maps API key from secrets.toml
secrets = toml.load("secrets.toml")
GOOGLE_API_KEY = secrets["google_maps"]["api_key"]

@app.route("/")
def home():
    return render_template("index.html") # Frontend loads here

@app.route("/get-api-key")
def get_api_key():
    return jsonify({"api_key": GOOGLE_API_KEY}) # Return API key to frontend

@app.route("/search-location", methods=["POST"])
def search_location():
    data = request.get_json()
    query = data.get("query")

    if not query:
        return jsonify({"error": "No query provided"}), 400

    # Call Google Geocoding API to get coordinates
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": query,
        "key": GOOGLE_API_KEY
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        results = response.json()
    except requests.RequestException as e:
        return jsonify({"error": "API request failed", "details": str(e)}), 500

    if results['status'] == 'OK':
        location = results['results'][0]['geometry']['location']
        return jsonify({
            "lat": location['lat'],
            "lng": location['lng'],
            "address": results['results'][0]['formatted_address']
        })
    else:
        return jsonify({"error": "Location not found"}), 404
    
@app.route("/get-distance", methods=["POST"])
def get_distance():
    data = request.get_json()

    origin = data.get("origin") # {lat, lng}
    destination = data.get("destination") # {lat, lng}

    if not origin or not destination:
        return jsonify({"error": "Missing origin or destination"}), 400
    
    origin_str = f"{origin['lat']},{origin['lng']}"
    destination_str = f"{destination['lat']},{destination['lng']}"
    
    url = f"https://maps.googleapis.com/maps/api/distancematrix/json"

    params = {
        "origins": origin_str,
        "destinations": destination_str,
        "key": GOOGLE_API_KEY,
    }

    response = requests.get(url, params=params)
    result = response.json()

    try:
        element = result["rows"][0]["elements"][0]
        distance_meters = element["distance"]["value"] # Distance in meters
        duration_text = element["duration"]["text"] # Duration as text (e.g., "12 mins")
        distance_text = element["distance"]["text"] # Distance as text (e.g., "5.2 miles")

        distance_miles = distance_meters * 0.000621371 # Convert meters to miles

        return jsonify({
            "distance": distance_text, # "5.2 miles"
            "duration": duration_text,  # "12 mins"
            "distance_value_miles": distance_miles # 5.2 (Number)
        })
    
    except Exception as e:
        return jsonify({"error": "Failed to calculate distance"})
    
@app.route("/get-cars")
def get_cars():
    with open("data/vehicles.json") as f:
        data = json.load(f)
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)