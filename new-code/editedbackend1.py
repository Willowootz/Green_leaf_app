from pathlib import Path

import json

import pandas as pd
import requests
import toml
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from sklearn.ensemble import RandomForestRegressor


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "vehicles.json"
SECRETS_PATH = BASE_DIR / "secrets.toml"
FRONTEND_DIR = BASE_DIR / "new-code"

app = Flask(__name__)
CORS(app)


def _format_duration(total_seconds):
    hours, remainder = divmod(int(total_seconds), 3600)
    minutes, _ = divmod(remainder, 60)
    if hours and minutes:
        return f"{hours} hr {minutes} min"
    if hours:
        return f"{hours} hr"
    return f"{minutes} min"


def _load_google_api_key() -> str:
    secrets = toml.load(SECRETS_PATH)
    return secrets["google_maps"]["api_key"]


GOOGLE_API_KEY = _load_google_api_key()


def _load_training_data() -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Training data not found: {DATA_PATH}")

    frame = pd.read_json(DATA_PATH)
    required_columns = ["Make", "Model", "EngineSize", "FuelType", "CO2"]
    missing_columns = [column for column in required_columns if column not in frame.columns]
    if missing_columns:
        raise ValueError(
            f"vehicles.json is missing required columns: {', '.join(missing_columns)}"
        )

    return frame[required_columns].dropna()


def _build_model() -> tuple[RandomForestRegressor, list[str], pd.DataFrame]:
    frame = _load_training_data()
    encoded = pd.get_dummies(frame, columns=["Make", "FuelType", "Model"])
    features = encoded.drop("CO2", axis=1)
    target = encoded["CO2"]

    trained_model = RandomForestRegressor(n_estimators=100, random_state=42)
    trained_model.fit(features, target)
    return trained_model, list(features.columns), frame


model, training_columns, training_frame = _build_model()


def _clean_string(value: object, field_name: str) -> str:
    if value is None:
        raise ValueError(f"Missing required field: {field_name}")

    text = str(value).strip()
    if not text:
        raise ValueError(f"Missing required field: {field_name}")

    return text.upper()


def _build_prediction_data(payload: dict) -> tuple[pd.DataFrame, dict]:
    def value_of(lower_key: str, upper_key: str):
        return payload.get(lower_key) if payload.get(lower_key) is not None else payload.get(upper_key)

    car_info = {
        "Make": _clean_string(value_of("make", "Make"), "make"),
        "Model": _clean_string(value_of("model", "Model"), "model"),
        "EngineSize": float(value_of("engine_size", "EngineSize")),
        "FuelType": _clean_string(value_of("fuel_type", "FuelType"), "fuel_type"),
    }

    prediction_frame = pd.DataFrame([car_info])
    prediction_frame = pd.get_dummies(prediction_frame)
    prediction_frame = prediction_frame.reindex(columns=training_columns, fill_value=0)

    return prediction_frame, car_info


def _predict_co2_per_km(payload: dict) -> tuple[float, dict]:
    prediction_frame, car_info = _build_prediction_data(payload)
    return float(model.predict(prediction_frame)[0]), car_info


def _normalize_location(value: object, label: str) -> dict:
    if not isinstance(value, dict):
        raise ValueError(f"Missing required field: {label}")

    lat = value.get("lat")
    lng = value.get("lng")
    if lat is None or lng is None:
        raise ValueError(f"Missing required field: {label}")

    return {"lat": float(lat), "lng": float(lng)}


def _normalize_stops(stops: object) -> list[dict]:
    normalized = []
    if not isinstance(stops, list):
        return normalized

    for stop in stops:
        if not isinstance(stop, dict):
            continue
        lat = stop.get("lat")
        lng = stop.get("lng")
        if lat is None or lng is None:
            continue
        normalized.append(
            {
                "lat": float(lat),
                "lng": float(lng),
                "name": stop.get("name") or stop.get("label") or "Stop",
            }
        )
    return normalized


@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html.html")


@app.route("/get-api-key")
def get_api_key():
    return jsonify({"api_key": GOOGLE_API_KEY})


@app.route("/get-cars")
def get_cars():
    with open(DATA_PATH, encoding="utf-8") as file_handle:
        data = json.load(file_handle)
    return jsonify(data)


@app.route("/search-location", methods=["POST"])
def search_location():
    data = request.get_json(silent=True) or {}
    query = str(data.get("query", "")).strip()

    if not query:
        return jsonify({"error": "No query provided"}), 400

    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": query, "key": GOOGLE_API_KEY}

    try:
        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()
        results = response.json()
    except requests.RequestException as error:
        return jsonify({"error": "API request failed", "details": str(error)}), 500

    if results.get("status") == "OK":
        location = results["results"][0]["geometry"]["location"]
        return jsonify(
            {
                "lat": location["lat"],
                "lng": location["lng"],
                "address": results["results"][0]["formatted_address"],
            }
        )

    return jsonify({"error": "Location not found"}), 404


@app.route("/get-distance", methods=["POST"])
def get_distance():
    data = request.get_json(silent=True) or {}
    origin = data.get("origin")
    destination = data.get("destination")

    try:
        origin_location = _normalize_location(origin, "origin")
        destination_location = _normalize_location(destination, "destination")
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    origin_str = f"{origin_location['lat']},{origin_location['lng']}"
    destination_str = f"{destination_location['lat']},{destination_location['lng']}"

    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        "origins": origin_str,
        "destinations": destination_str,
        "key": GOOGLE_API_KEY,
    }

    try:
        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()
        result = response.json()
    except requests.RequestException as error:
        return jsonify({"error": "Failed to calculate distance", "details": str(error)}), 500

    try:
        element = result["rows"][0]["elements"][0]
        distance_meters = element["distance"]["value"]
        duration_text = element["duration"]["text"]
        distance_text = element["distance"]["text"]
        distance_miles = distance_meters * 0.000621371

        return jsonify(
            {
                "distance": distance_text,
                "duration": duration_text,
                "distance_value_miles": distance_miles,
            }
        )
    except Exception:
        return jsonify({"error": "Failed to calculate distance"}), 500


@app.route("/predict", methods=["POST"])
def predict():
    payload = request.get_json(silent=True) or {}

    try:
        distance = float(payload.get("distance"))
        if distance <= 0:
            raise ValueError("distance must be greater than zero")

        prediction_frame, car_info = _build_prediction_data(payload)
    except (TypeError, ValueError) as error:
        return jsonify({"error": str(error)}), 400

    co2_per_km = float(model.predict(prediction_frame)[0])
    total_emissions_g = co2_per_km * distance

    return jsonify(
        {
            "make": car_info["Make"],
            "model": car_info["Model"],
            "engine_size": car_info["EngineSize"],
            "fuel_type": car_info["FuelType"],
            "distance_km": round(distance, 3),
            "co2_per_km_g": round(co2_per_km, 3),
            "total_emissions_g": round(total_emissions_g, 3),
            "total_emissions_kg": round(total_emissions_g / 1000, 3),
            "emissions": round(total_emissions_g / 1000, 3),
        }
    )


@app.route("/get-greenest-route", methods=["POST"])
def get_greenest_route():
    data = request.get_json(silent=True) or {}

    try:
        origin = _normalize_location(data.get("origin"), "origin")
        destination = _normalize_location(data.get("destination"), "destination")
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    stops = _normalize_stops(data.get("stops") or [])
    optimize_order = bool(data.get("optimize_order", False))

    if stops:
        destination = {"lat": stops[-1]["lat"], "lng": stops[-1]["lng"]}

    car_emissions = data.get("car_emissions")
    selected_vehicle = data.get("car") if isinstance(data.get("car"), dict) else data

    try:
        if car_emissions is None:
            car_emissions, selected_vehicle = _predict_co2_per_km(selected_vehicle)
        else:
            car_emissions = float(car_emissions)
    except (TypeError, ValueError) as error:
        return jsonify({"error": f"Invalid vehicle profile: {error}"}), 400

    origin_str = f"{origin['lat']},{origin['lng']}"
    destination_str = f"{destination['lat']},{destination['lng']}"

    waypoint_stops = stops[:-1] if stops else []
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

    try:
        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()
        result = response.json()
    except requests.RequestException as error:
        return jsonify({"error": "Failed to get routes", "details": str(error)}), 500

    if result.get("status") != "OK":
        return jsonify(
            {"error": "Failed to get routes", "details": result.get("error_message")}
        ), 500

    routes = result.get("routes", [])
    if not routes:
        return jsonify({"error": "No routes found"}), 404

    route_infos = []
    for index, route in enumerate(routes):
        total_distance_m = sum(leg["distance"]["value"] for leg in route["legs"])
        total_duration_s = sum(leg["duration"]["value"] for leg in route["legs"])
        total_distance_km = total_distance_m / 1000.0
        emissions_g = total_distance_km * car_emissions
        route_infos.append(
            {
                "index": index,
                "distance_km": round(total_distance_km, 3),
                "duration": _format_duration(total_duration_s),
                "co2_emissions_g": round(emissions_g, 3),
                "polyline": route["overview_polyline"]["points"],
                "waypoint_order": route.get("waypoint_order", []),
                "legs_summary": [
                    {
                        "distance_text": leg["distance"]["text"],
                        "duration_text": leg["duration"]["text"],
                    }
                    for leg in route["legs"]
                ],
            }
        )

    greenest = min(route_infos, key=lambda route_info: route_info["co2_emissions_g"])
    for route_info in route_infos:
        if route_info is not greenest:
            route_info["extra_emissions_g"] = round(
                route_info["co2_emissions_g"] - greenest["co2_emissions_g"], 3
            )
        else:
            route_info["extra_emissions_g"] = 0

    return jsonify(
        {
            "greenest": greenest,
            "routes": route_infos,
            "savings_g": [route["extra_emissions_g"] for route in route_infos],
            "stops": stops,
            "optimize_order": optimize_order,
            "car_emissions_g_per_km": round(car_emissions, 3),
            "car": selected_vehicle,
        }
    )


if __name__ == "__main__":
    app.run(debug=True)