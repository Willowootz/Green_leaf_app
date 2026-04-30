# Green Leaf App

Green Leaf is a Flask-based route planning app that estimates vehicle CO2 emissions and compares route options so users can choose a lower-emission trip before driving.

## What It Does

- Lets users choose a vehicle profile from a local emissions dataset
- Accepts an origin, a destination, and optional additional stops
- Uses Google Places Autocomplete for location search inputs
- Looks up distances, durations, and route alternatives through Google Maps APIs
- Calculates estimated emissions for each route and highlights the greenest one
- Saves route history and vehicle choices in the browser

## How It Works

1. The frontend loads the main trip planner UI from [app/frontend/templates/index.html](app/frontend/templates/index.html).
2. The backend serves the page and API endpoints from [app/backend/app.py](app/backend/app.py).
3. Vehicle data is loaded from [data/raw/vehicles.json](data/raw/vehicles.json) and used to train a Random Forest emissions model at startup.
4. The frontend requests Google Maps support through the backend and loads Google Maps JavaScript with Places enabled.
5. Users search for places, add stops, and submit the trip.
6. The backend geocodes locations, calculates route alternatives, and estimates emissions for each route.
7. The frontend displays the route comparison and the lowest-emission option.

## Project Structure

```text
Green_leaf_app/
├─ app/
│  ├─ backend/
│  │  ├─ app.py
│  │  └─ services/
│  │     └─ carbonemissionspredictions.py
│  └─ frontend/
│     ├─ templates/
│     │  └─ index.html
│     └─ static/
│        └─ css/
│           └─ style.css
├─ data/
│  └─ raw/
│     └─ vehicles.json
├─ notebooks/
│  └─ CarbonEmissionsPredictions.ipynb
├─ requirements.txt
├─ secrets.toml
└─ README.md
```

## Main Files

- [app/backend/app.py](app/backend/app.py) - Flask app entry point and API routes
- [app/frontend/templates/index.html](app/frontend/templates/index.html) - Main web UI
- [app/frontend/static/css/style.css](app/frontend/static/css/style.css) - App styling
- [data/raw/vehicles.json](data/raw/vehicles.json) - Vehicle emissions dataset
- Dataset source: [CO2 Emission by Vehicles (Kaggle)](https://www.kaggle.com/datasets/debajyotipodder/co2-emission-by-vehicles)
- [secrets.toml](secrets.toml) - Google Maps API key configuration
- [app/backend/services/carbonemissionspredictions.py](app/backend/services/carbonemissionspredictions.py) - Emissions modeling script
- [notebooks/CarbonEmissionsPredictions.ipynb](notebooks/CarbonEmissionsPredictions.ipynb) - Notebook version of the emissions work

## Features

- Vehicle profile selection
- Google Places Autocomplete for all location inputs
- Distance and duration lookup
- Greenest-route comparison
- Multi-stop trip planning
- Optional stop-order optimization
- Browser-saved trip history

## Tech Stack

- Python
- Flask
- pandas
- scikit-learn
- requests
- flask-cors
- Google Maps APIs

## Requirements

- Python 3.10 or newer
- A Google Cloud project with billing enabled
- A Google Maps API key with access to:
  - Geocoding API
  - Distance Matrix API
  - Directions API
  - Places API
  - Maps JavaScript API

## Setup

1. Clone the repository.
2. Create and activate a virtual environment.
3. Install dependencies.
4. Add your Google Maps API key to `secrets.toml`.

### Create a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Install dependencies

```powershell
pip install -r requirements.txt
```

### Configure secrets

Create or edit `secrets.toml`:

```toml
[google_maps]
api_key = "YOUR_GOOGLE_MAPS_API_KEY"
```

## Run the App

From the repository root:

```powershell
python app/backend/app.py
```

Then open:

- http://127.0.0.1:5000/

## Backend Endpoints

- `GET /` - Serves the main web app
- `GET /get-api-key` - Returns the Google Maps API key
- `GET /get-cars` - Returns the vehicle dataset
- `POST /search-location` - Geocodes a place or address
- `POST /get-distance` - Returns distance and duration between two coordinates
- `POST /predict` - Predicts CO2 emissions for a vehicle and distance
- `POST /get-greenest-route` - Returns route alternatives and identifies the lowest-emission route

## Notes

- The app currently runs in Flask debug mode.
- The Google Maps API key is required for the app to work.
- The emissions model is trained from the local dataset at startup.
- The notebook and service script are supporting assets for experimentation and model development.
