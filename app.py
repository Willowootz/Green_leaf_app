from flask import Flask, request, jsonify, render_template
import requests
import toml
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Google Maps API Key
secrets = toml.load("secrets.toml")
GOOGLE_API_KEY = secrets["google_maps"]["api_key"]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/search-location", methods=["POST"])
def search_location():
    data = request.get_json()
    query = data.get("query")

    if not query:
        return jsonify({"error": "No query provided"}), 400

    # Call Google Geocoding API to get coordinates
    geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={query}&key={GOOGLE_API_KEY}"
    try:
        response = requests.get(geocode_url)
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

if __name__ == "__main__":
    app.run(debug=True)