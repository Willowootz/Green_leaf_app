# Green Leaf

Green Leaf is a Flask-based navigation app that helps users choose lower-emission routes.
It compares available driving routes, highlights the most eco-friendly option, and tracks each user's estimated CO2 output over time based on their selected vehicle profile.

## Why Green Leaf

Most navigation apps optimize for speed. Green Leaf adds environmental impact into route decision-making by:

- estimating CO2 emissions for each route option
- highlighting the greenest route
- showing how much extra CO2 alternative routes produce
- tracking recent trips and total emissions in a built-in history panel

## Core Features

- Vehicle profile selection (Make, Model, Engine Size, Fuel Type)
- Local profile persistence in browser storage
- Multi-stop trip planning (up to 5 stops)
- Optional stop-order optimization using Google Directions waypoints
- Alternative route comparison with emissions metrics
- Route visualization on Google Maps with polyline highlighting
- Trip history panel with:
  - total CO2 output
  - trip count
  - sortable entries (newest, oldest, highest CO2, lowest CO2)
  - clear-all history action

## How Emissions Are Calculated

For each returned route:

- total distance is computed from route legs (km)
- selected vehicle emission factor is used (grams CO2 per km)
- route emissions are estimated as:

$$
	ext{CO2}_{route} = \text{distance}_{km} \times \text{carEmissions}_{g/km}
$$

The route with the minimum estimated CO2 is marked as the greenest route.

## Tech Stack

- Backend: Flask
- Frontend: HTML, CSS, Vanilla JavaScript
- Mapping and routing:
  - Google Maps JavaScript API
  - Google Places Autocomplete
  - Google Geocoding API
  - Google Directions API
  - Google Distance Matrix API

## Project Structure

```text
Green_leaf_app/
├─ app.py
├─ requirements.txt
├─ secrets.toml
├─ data/
│  └─ vehicles.json
├─ templates/
│  └─ index.html
├─ frontend/
│  └─ style.css
├─ model/
│  └─ carbonemissionspredictions.py
└─ notebooks/
	 └─ CarbonEmissionsPredictions.ipynb
```

## Prerequisites

- Python 3.10+
- A Google Maps API key with the following APIs enabled:
  - Maps JavaScript API
  - Places API
  - Geocoding API
  - Directions API
  - Distance Matrix API

## Setup

1. Clone the repository.
2. Create and activate a virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create or update `secrets.toml` in the project root:

```toml
[google_maps]
api_key = "YOUR_GOOGLE_MAPS_API_KEY"
```

5. Run the app:

```bash
python app.py
```

6. Open your browser at:

```text
http://127.0.0.1:5000
```

## Usage

1. Open the profile icon and save your vehicle profile.
2. In Trip Planner:
   - add one or more destinations (up to 5)
   - drag to reorder stops or use move controls
   - optionally enable Optimize order
3. Click Get Route.
4. Review route alternatives and choose the preferred route.
5. Open History to review cumulative CO2 output and recent trips.

## API Endpoints

- `GET /` : serves the main app page
- `GET /get-api-key` : returns Google Maps API key to frontend
- `POST /search-location` : geocodes a location string
- `POST /get-distance` : returns point-to-point distance and duration
- `GET /get-cars` : returns vehicle dataset from `data/vehicles.json`
- `POST /get-greenest-route` : returns route alternatives and emissions data

### Example `POST /get-greenest-route` Request

```json
{
  "origin": { "lat": 38.627, "lng": -90.1994 },
  "stops": [
    { "lat": 38.648, "lng": -90.31, "name": "Stop A" },
    { "lat": 38.7, "lng": -90.28, "name": "Stop B" }
  ],
  "optimize_order": true,
  "car_emissions": 190
}
```

## Data and Privacy Notes

- Vehicle profile and trip history are stored locally in the browser (`localStorage`).
- No user authentication or cloud profile sync is implemented.
- API key is loaded from local `secrets.toml`.

## Troubleshooting

- App fails to start:
  - verify dependencies are installed with `pip install -r requirements.txt`
  - verify `secrets.toml` exists and contains a valid key
- Map is blank or routes fail:
  - verify required Google APIs are enabled
  - verify billing and API key restrictions in Google Cloud
- Could not fetch route/location:
  - check internet access and API quota limits

## Roadmap Ideas

- Display optimized stop order directly in the planner UI
- Add per-stop leg-by-leg emissions in route cards
- Add user accounts and cross-device history sync
- Add export for trip history (CSV/JSON)

## License

Add your preferred license (for example, MIT) in this repository.
