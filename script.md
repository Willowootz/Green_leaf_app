# Green Leaf Presentation Script (About 3 Minutes)

## Opening (20-30 seconds)
Hi everyone. Today I’m presenting **Green Leaf**, a web app that helps users choose lower-emission driving routes.  
The app combines a Flask backend, a browser-based frontend, Google Maps services, and a machine learning model that estimates vehicle CO2 output.

---

## System Overview (30-40 seconds)
Green Leaf has two main parts:

1. **Frontend** in `app/frontend/templates/index.html`  
   - Collects vehicle profile and trip inputs
   - Shows the map, route cards, and emissions summary
2. **Backend** in `app/backend/app.py`  
   - Serves API routes
   - Calls Google APIs
   - Predicts CO2 emissions and picks the greenest route

---

## Frontend Flow (45-55 seconds)
On the frontend, users first choose their vehicle details: make, model, engine size, and fuel type.  
Those dropdowns are populated by calling the backend endpoint `/get-cars`.

Then users enter trip info: start location, destination, and optional extra stops.  
When they click **Get Route**, the main submit handler sends a request to `/get-greenest-route`.

### Frontend code callouts
```html
<!-- app/frontend/templates/index.html -->
<form class="ser trip-search-form" autocomplete="off">
  ...
  <button type="submit" id="searchBtn">Get Route</button>
</form>
```

```javascript
// app/frontend/templates/index.html
async function findGreenestRoute(event) {
  ...
  const response = await fetch("/get-greenest-route", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}
```

Use this line while presenting:  
**“This function is where the frontend packages user input and asks the backend to compute greener route options.”**

---

## Backend Flow (65-75 seconds)
In the backend, the app loads a vehicle dataset and trains a **Random Forest Regressor** at startup.  
That model predicts a car’s CO2 emissions per kilometer based on make, model, engine size, and fuel type.

For trip requests, the backend:
- Validates origin, destination, and stops
- Calls Google Directions with `alternatives=true`
- Computes total distance and duration for each returned route
- Estimates route emissions with:

**emissions = distance_km × car_emissions_g_per_km**

Then it picks the route with the minimum emissions and returns all options plus the extra emissions for non-greenest routes.

### Backend code callouts
```python
# app/backend/app.py
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)
```

```python
# app/backend/app.py
response = requests.get(
    "https://maps.googleapis.com/maps/api/directions/json",
    params=params,
    timeout=20,
)
```

```python
# app/backend/app.py
co2_emissions_g = distance_km * car_emissions
greenest = min(route_infos, key=lambda route: route["co2_emissions_g"])
```

Use this line while presenting:  
**“The backend compares all alternative routes and uses predicted or provided vehicle emissions to identify the lowest-CO2 option.”**

---

## Results in the UI (25-35 seconds)
After the backend responds, the frontend:
- Draws each route polyline on Google Maps
- Highlights the greenest route
- Displays distance, duration, and CO2 totals
- Saves selected-trip history in local storage for profile and history panels

### UI update code callout
```javascript
// app/frontend/templates/index.html
selectRoute(routeId, { saveToHistory: true });
```

Use this line while presenting:  
**“After route selection, the app updates the map and metrics immediately, then stores the trip for future review.”**

---

## Closing (15-20 seconds)
So Green Leaf turns route planning into a sustainability decision tool:  
it combines live map routing, vehicle-based emissions prediction, and clear visual feedback so users can choose a greener trip with confidence.
