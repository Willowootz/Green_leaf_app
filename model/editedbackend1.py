from pathlib import Path

import json

import pandas as pd
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from sklearn.ensemble import RandomForestRegressor


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "vehicles.json"
FRONTEND_DIR = BASE_DIR / "frontend"

app = Flask(__name__)
CORS(app)


def _load_training_data() -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Training data not found: {DATA_PATH}")

    frame = pd.read_json(DATA_PATH)
    required_columns = ["Make", "Model", "EngineSize", "FuelType", "CO2"]
    missing_columns = [column for column in required_columns if column not in frame.columns]
    if missing_columns:
        raise ValueError(f"vehicles.json is missing required columns: {', '.join(missing_columns)}")

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
    car_info = {
        "Make": _clean_string(payload.get("make"), "make"),
        "Model": _clean_string(payload.get("model"), "model"),
        "EngineSize": float(payload.get("engine_size")),
        "FuelType": _clean_string(payload.get("fuel_type"), "fuel_type"),
    }

    prediction_frame = pd.DataFrame([car_info])
    prediction_frame = pd.get_dummies(prediction_frame)
    prediction_frame = prediction_frame.reindex(columns=training_columns, fill_value=0)

    return prediction_frame, car_info


@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html.html")


@app.route("/vehicle-options")
def vehicle_options():
    return jsonify(
        {
            "makes": sorted(training_frame["Make"].dropna().unique().tolist()),
            "models": sorted(training_frame["Model"].dropna().unique().tolist()),
            "fuel_types": sorted(training_frame["FuelType"].dropna().unique().tolist()),
        }
    )


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


if __name__ == "__main__":
    app.run(debug=True)