Green Leaf backend — app.py block guide
=========================================

Line ranges refer to app/backend/app.py in this repository. Use them to read alongside the source.

The source contains a misplaced section comment at L146 (`# ===== API ROUTES =====` indented inside `_normalize_stops` spacing). All Flask routes actually begin at L147 with `@app.route("/")`.


## 1. Imports (L1–L11)

**Purpose:** Load standard library and third-party modules used across the file.

- `Path` for repo-relative paths; `json` for reading vehicle JSON in `/get-cars`.
- `pandas` for training data and one-hot alignment for predictions.
- `requests` for Google REST APIs (Geocoding, Distance Matrix, Directions).
- `toml` for loading `secrets.toml`.
- Flask (`Flask`, `jsonify`, `render_template`, `request`) and `CORS` for the web app and JSON APIs.
- `RandomForestRegressor` for CO2 (g per km) estimation from vehicle attributes.


## 2. Configuration and paths (L13–L25)

**Purpose:** Resolve project layout and construct the Flask application.

- `PROJECT_ROOT` is two parents above `app.py` (repository root).
- `DATA_PATH` points to `data/raw/vehicles.json` (training + car list).
- `SECRETS_PATH` points to `secrets.toml` (Google API key).
- `TEMPLATES_DIR` and `STATIC_DIR` wire the monolithic `index.html` and static assets.
- `app = Flask(...)` sets `template_folder` and `static_folder`; `CORS(app)` allows cross-origin access to APIs (useful for local dev or split frontends).


## 3. Utility functions (L28–L44)

**Purpose:** Small helpers used by routing and emissions logic.

- **`_format_duration(total_seconds)` (L29–L36):** Converts seconds (from Google leg durations) into a short human string (`"X hr Y min"`, hours only, or minutes only).
- **`_load_google_api_key()` (L39–L41):** Reads `secrets["google_maps"]["api_key"]` from `SECRETS_PATH`.
- **`GOOGLE_API_KEY` (L44):** Module-level key loaded at import time; used by all Google HTTP calls and exposed to the browser via `/get-api-key` (fine for demos; production apps usually proxy Maps without exposing keys).


## 4. Model training (L47–L74)

**Purpose:** Train a regression model once when the module loads.

- **`_load_training_data()` (L48–L60):** Ensures `vehicles.json` exists; loads JSON; requires columns `Make`, `Model`, `EngineSize`, `FuelType`, `CO2`; drops rows with nulls.
- **`_build_model()` (L63–L71):** One-hot encodes categorical columns with `pd.get_dummies`, fits `RandomForestRegressor` (100 trees, `random_state=42`) to predict `CO2` from numeric + dummy features.
- **Module globals (L74):** `model`, `training_columns` (feature column order after dummies), and `training_frame` (raw cleaned frame). `training_columns` is critical so prediction rows match the same dummy layout via `reindex(..., fill_value=0)`.


## 5. Data normalization and prediction helpers (L77–L143)

**Purpose:** Validate JSON payloads and align inputs with the trained model and route APIs.

- **`_clean_string` (L78–L86):** Requires non-empty string fields; returns uppercased text for consistent dummy categories.
- **`_build_prediction_data` (L89–L104):** Accepts either snake_case or PascalCase keys (`make`/`Make`, etc.); builds one-row `DataFrame`, `get_dummies`, then **`reindex` to `training_columns`** so missing categories become zero columns.
- **`_predict_co2_per_km` (L107–L109):** Returns predicted CO2 per km (float) and the normalized `car_info` dict.
- **`_normalize_location` (L112–L121):** Ensures `value` is a dict with numeric `lat` and `lng`.
- **`_normalize_stops` (L124–L143):** Accepts a list of stop dicts; skips invalid entries; returns list of `{lat, lng, name}` with fallback name `"Stop"` (uses `name` or `label`).


## 6. API routes (L147–L377)

**Purpose:** HTTP interface for the frontend and other clients.

---

### 6a. `GET /` (L147–L149)

**Purpose:** Serve the main SPA template.

- Returns `render_template("index.html")` from `TEMPLATES_DIR`.

---

### 6b. `GET /get-api-key` (L152–L154)

**Purpose:** Provide the Google Maps JavaScript API key to the client loader.

- JSON: `{"api_key": "<key>"}` using module `GOOGLE_API_KEY`.

---

### 6c. `GET /get-cars` (L157–L161)

**Purpose:** Expose the raw vehicle dataset for cascading dropdowns.

- Opens `DATA_PATH` as UTF-8 JSON and returns `jsonify(data)` (same structure as on disk).

---

### 6d. `POST /search-location` (L164–L192)

**Purpose:** Geocode a free-text address when the user does not pick a Places result.

- Body JSON: `{"query": "<string>"}`; empty query → 400.
- Calls `https://maps.googleapis.com/maps/api/geocode/json` with `address` and `key`.
- On `status == "OK"`: returns `lat`, `lng`, `formatted_address` from the first result.
- On network failure: 500 with `details`; on no results: 404 `"Location not found"`.

---

### 6e. `POST /get-distance` (L195–L239)

**Purpose:** One origin–destination pair via Google Distance Matrix API.

- Body: `{"origin": {"lat", "lng"}, "destination": {"lat", "lng"}}`; validation uses `_normalize_location` (400 on error).
- GET `https://maps.googleapis.com/maps/api/distancematrix/json` with `origins`/`destinations` as `"lat,lng"` strings.
- Success JSON: `distance` and `duration` human text from Google, plus `distance_value_miles` derived from meters.
- Malformed Google response or missing elements → 500 generic error.

---

### 6f. `POST /predict` (L242–L270)

**Purpose:** Predict CO2 for a given distance using the saved vehicle profile fields.

- Body: vehicle keys (via `_build_prediction_data` rules) and **`distance`** as float **kilometers**; must be `> 0` or 400.
- Uses `model.predict` on the aligned frame (same as `_predict_co2_per_km` logic inlined: `co2_per_km` then `total_emissions_g = co2_per_km * distance`).
- Response echoes normalized make/model/engine/fuel, rounded `distance_km`, `co2_per_km_g`, `total_emissions_g`, `total_emissions_kg`, and `emissions` (kg alias).

---

### 6g. `POST /get-greenest-route` (L273–L377)

**Purpose:** Request alternative driving routes, estimate CO2 per route using vehicle g/km, and identify the lowest-emissions option.

- Normalizes `origin` and `destination` from JSON; reads optional `stops` list and `optimize_order` boolean.
- If `stops` is non-empty, **`destination` is overwritten** by the last stop’s coordinates (final leg ends at last waypoint).
- Vehicle emissions: either `car_emissions` float (g/km) supplied by client, or a **`car` dict** (or the whole JSON body if `car` is missing) normalized and passed to `_predict_co2_per_km(selected_vehicle)` when `car_emissions` is None.
- Builds Directions request: `origin`/`destination` as `"lat,lng"`, `alternatives=true`, optional `waypoints` pipe-joined. Intermediate stops are `stops[:-1]`; if optimizing, inserts `optimize:true` at the front of the waypoint list per Google’s waypoint optimization convention.
- GET `https://maps.googleapis.com/maps/api/directions/json`.
- Non-OK status or empty `routes` → 500/404 with error payload.
- For each route: sums all legs’ distance (m) and duration (s); `distance_km`, `_format_duration`, `co2_emissions_g = distance_km * car_emissions`, stores `overview_polyline.points`, `waypoint_order`, and short `legs_summary`.
- **`greenest`:** route info dict with minimum `co2_emissions_g`; other routes get **`extra_emissions_g`** (delta vs greenest, zero for greenest).
- Response also includes `savings_g` list, normalized `stops`, `optimize_order`, `car_emissions_g_per_km`, and resolved `car` profile dict.


## 7. Application entry point (L380–L382)

**Purpose:** Run the development server when executing this file directly.

- `app.run(debug=True)` enables Flask debug mode (auto-reload and debugger — not for untrusted production).


---

External services and files referenced
----------------------------------------

- **Google Maps Platform (HTTP):** Geocoding API, Distance Matrix API, Directions API (`maps.googleapis.com/maps/api/...`).
- **Local files:** `secrets.toml` (API key), `data/raw/vehicles.json` (vehicles and CO2 training labels).
- **Frontend:** Templates and static paths under `app/frontend/` as configured on the `Flask` instance.
