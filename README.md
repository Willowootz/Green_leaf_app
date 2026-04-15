# Green Leaf App

Green Leaf is a Flask-based route planning app that helps drivers compare route options by estimated CO2 emissions.
It combines Google Maps routing data with a vehicle emissions dataset so users can choose the lowest-emission route before driving.

## Features

- Vehicle profile selector (make, model, engine size, fuel type) from a local dataset
- Destination search and optional multi-stop trip planning (up to 5 destinations)
- Optional stop-order optimization for multi-stop routes
- Multiple route comparison from Google Directions API alternatives
- Automatic identification of the greenest route (lowest estimated CO2)
- Route cards showing emissions, distance, duration, and potential savings
- Trip history panel with sorting and cumulative CO2 totals
- Browser local storage for saved vehicle profile and trip history

## Tech Stack

- Backend: Python, Flask, flask-cors
- Frontend: HTML, CSS, Vanilla JavaScript
- External APIs: Google Maps Geocoding API, Distance Matrix API, Directions API, Places API, Maps JavaScript API
- Data source: `data/vehicles.json`

## Project Structure

```text
Green_leaf_app/
├─ app.py
├─ requirements.txt
├─ secrets.toml
├─ data/
│  └─ vehicles.json
├─ frontend/
│  └─ style.css
├─ templates/
│  └─ index.html
├─ model/
│  └─ carbonemissionspredictions.py
├─ notebooks/
│  └─ CarbonEmissionsPredictions.ipynb
├─ GPS/
├─ emissions/
└─ README.md
```

## Prerequisites

- Python 3.10+
- A Google Cloud project with billing enabled
- A Google Maps API key with access to:
  - Geocoding API
  - Distance Matrix API
  - Directions API
  - Places API
  - Maps JavaScript API

## Setup

1. Clone the repository and open the project folder.
2. Create and activate a virtual environment.
3. Install dependencies.
4. Add your Google Maps API key to `secrets.toml`.

### 1) Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2) Install dependencies

```powershell
pip install -r requirements.txt
```

### 3) Configure secrets

Create or edit `secrets.toml`:

```toml
[google_maps]
api_key = "YOUR_GOOGLE_MAPS_API_KEY"
```

## Run the App

```powershell
python app.py
```

Then open:

- http://127.0.0.1:5000/

## How It Works

1. The frontend loads and requests `/get-api-key`.
2. Google Maps JavaScript + Places libraries are loaded dynamically.
3. User sets a vehicle profile from `vehicles.json`.
4. User selects one or more destinations.
5. Frontend sends origin/stops/car emissions data to `/get-greenest-route`.
6. Backend fetches alternative routes from Google Directions API.
7. Backend computes estimated emissions per route:

$$\text{CO2 emissions (g)} = \text{distance (km)} \times \text{vehicle CO2 factor (g/km)}$$

8. Frontend highlights the greenest route and shows comparisons.

## Backend Endpoints

- `GET /`
  - Returns the main web UI (`templates/index.html`).

- `GET /get-api-key`
  - Returns Google Maps API key from `secrets.toml`.

- `POST /search-location`
  - Body: `{ "query": "address or place" }`
  - Returns geocoded latitude/longitude and formatted address.

- `POST /get-distance`
  - Body: `{ "origin": {"lat": ..., "lng": ...}, "destination": {"lat": ..., "lng": ...} }`
  - Returns distance and duration using Google Distance Matrix.

- `GET /get-cars`
  - Returns vehicle records from `data/vehicles.json`.

- `POST /get-greenest-route`
  - Body includes:
    - `origin`: coordinates
    - `stops`: array of stop coordinates
    - `optimize_order`: boolean
    - `car_emissions`: grams CO2 per km
  - Returns:
    - `greenest`: lowest-emission route object
    - `routes`: all route options with metrics
    - `savings_g`: extra emissions vs greenest route

## Notes on Model Assets

The repository includes:

- `model/carbonemissionspredictions.py`
- `notebooks/CarbonEmissionsPredictions.ipynb`

These files are related to experimentation/training logic for emissions prediction. The running web app currently uses the vehicle emissions values from `data/vehicles.json` for route calculations.

## Current Limitations

- API key is served to frontend by design (required for Maps JavaScript API)
- Depends on Google APIs and internet connectivity
- No automated tests included yet
- `app.py` runs with Flask debug mode enabled by default

## Future Improvements

- Move runtime config to environment variables for deployment
- Add backend input validation and stronger error handling
- Add unit/integration tests for API routes
- Add production WSGI server setup (e.g., gunicorn/waitress)
- Add Docker support and deployment docs

## License

No license file is currently included in this repository.
If you plan to publish/distribute this project, add a `LICENSE` file (for example MIT, Apache-2.0, etc.).
