from flask import Flask, request, jsonify, render_template
import requests
import toml
from flask_cors import CORS
import json

app = Flask(__name__, static_folder="frontend")
CORS(app)


def format_duration(total_seconds):
    hours, remainder = divmod(int(total_seconds), 3600)
    minutes, _ = divmod(remainder, 60)
    if hours and minutes:
        return f"{hours} hr {minutes} min"
    if hours:
        return f"{hours} hr"
    return f"{minutes} min"

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


# New endpoint: Get the greenest route (lowest CO2 emissions)
@app.route("/get-greenest-route", methods=["POST"])
def get_greenest_route():
    data = request.get_json()

    origin = data.get("origin")  # {lat, lng}
    destination = data.get("destination")  # {lat, lng}
    stops = data.get("stops") or []
    optimize_order = bool(data.get("optimize_order", False))
    car_emissions = data.get("car_emissions")  # grams CO2 per km

    normalized_stops = []
    if isinstance(stops, list):
        for stop in stops:
            if not isinstance(stop, dict):
                continue
            lat = stop.get("lat")
            lng = stop.get("lng")
            if lat is None or lng is None:
                continue
            normalized_stops.append(
                {
                    "lat": lat,
                    "lng": lng,
                    "name": stop.get("name") or stop.get("label") or "Stop",
                }
            )

    if normalized_stops:
        destination = {
            "lat": normalized_stops[-1]["lat"],
            "lng": normalized_stops[-1]["lng"],
        }

    if not origin or not destination or car_emissions is None:
        return jsonify({"error": "Missing origin, destination, or car_emissions"}), 400

    origin_str = f"{origin['lat']},{origin['lng']}"
    destination_str = f"{destination['lat']},{destination['lng']}"

    waypoint_stops = normalized_stops[:-1] if normalized_stops else []
    waypoint_values = [f"{stop['lat']},{stop['lng']}" for stop in waypoint_stops]
    if waypoint_values and optimize_order:
        waypoint_values.insert(0, "optimize:true")

    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": origin_str,
        "destination": destination_str,
        "alternatives": "true",
        "key": GOOGLE_API_KEY,
    }
    if waypoint_values:
        params["waypoints"] = "|".join(waypoint_values)

    response = requests.get(url, params=params)
    result = response.json()

    if result.get("status") != "OK":
        return jsonify({"error": "Failed to get routes", "details": result.get("error_message")}), 500

    routes = result.get("routes", [])
    if not routes:
        return jsonify({"error": "No routes found"}), 404

    # Gather all routes with emissions
    route_infos = []
    for idx, route in enumerate(routes):
        total_distance_m = sum(leg["distance"]["value"] for leg in route["legs"])
        total_duration_s = sum(leg["duration"]["value"] for leg in route["legs"])
        total_distance_km = total_distance_m / 1000.0
        emissions = total_distance_km * car_emissions  # grams CO2
        route_infos.append({
            "index": idx,
            "distance_km": total_distance_km,
            "duration": format_duration(total_duration_s),
            "co2_emissions_g": emissions,
            "polyline": route["overview_polyline"]["points"],
            "waypoint_order": route.get("waypoint_order", []),
            "legs_summary": [
                {
                    "distance_text": leg["distance"]["text"],
                    "duration_text": leg["duration"]["text"],
                }
                for leg in route["legs"]
            ],
        })

    # Find the greenest route (lowest emissions)
    greenest = min(route_infos, key=lambda r: r["co2_emissions_g"])
    for r in route_infos:
        if r is not greenest:
            r["extra_emissions_g"] = r["co2_emissions_g"] - greenest["co2_emissions_g"]
        else:
            r["extra_emissions_g"] = 0

    return jsonify({
        "greenest": greenest,
        "routes": route_infos,
        "savings_g": [r["extra_emissions_g"] for r in route_infos],
        "stops": normalized_stops,
        "optimize_order": optimize_order,
    })

if __name__ == "__main__":
    app.run(debug=True)