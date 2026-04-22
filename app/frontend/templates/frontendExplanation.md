Green Leaf — index.html block guide
====================================

Line ranges refer to app/frontend/templates/index.html in this repository. Use them to jump alongside the source.

The trip form uses class="ser" on the form element; JavaScript selects it with document.querySelector(".ser"). Renaming to "search" would break that hook unless the script is updated too.


## 1. Document shell (L1–L2)

**Purpose:** Declares an HTML5 document and sets the page language for accessibility and typography.

- `<!doctype html>` enables standards mode.
- `<html lang="en">` marks content as English for screen readers and search engines.


## 2. `<head>` (L3–L1083)

### 2a. Meta, title, and document head (L3–L9)

**Purpose:** Encoding, mobile viewport, and the browser tab title.

- `charset="UTF-8"` avoids mojibake for symbols and copy.
- `viewport` meta makes layout scale on phones.
- `<title>` sets the tab label: "Green Leaf | Sustainable Map Explorer".


### 2b. External assets (L10–L19)

**Purpose:** Load icon and UI fonts from Google Fonts without bundling them in the repo.

- Material Symbols Outlined for the account icon (`account_circle`) and similar glyphs.
- Inter as the primary UI font stack fallback to system fonts elsewhere in CSS.


### 2c. Embedded styles wrapper (L20–L21)

**Purpose:** Marks the start of the large inline stylesheet (no external `style.css` link in this template for these rules).


### 2d. CSS — reset and global `body` (L22–L41)

**Purpose:** Normalize spacing and set the default canvas for the app.

- Universal `*` reset (margin/padding/box-sizing).
- `body` font family (Inter + system stack), light green background, text color, page padding, short transition.


### 2e. CSS — header and layout (L42–L75)

**Purpose:** Top title row and decorative separator.

- `.top-bar` flex layout for title vs. supporting content.
- `.title` / `h1` gradient text styling for the brand heading.
- `hr` styled as a soft gradient divider bar.


### 2f. CSS — action row (L76–L113)

**Purpose:** The pill-shaped bar holding profile, menu, and history controls.

- `.action-panel` frosted card look (semi-transparent white, blur, rounded border).
- `.profile-btn`, `.acc-icon` circular account button and icon sizing or colors.
- `.history button` History control styling and hover (includes a clock emoji via `::before`).


### 2g. CSS — dropdown menu (L114–L179)

**Purpose:** "Menu" button and hover-revealed navigation links.

- `.dropdown`, `.dropbtn`, `.dropdown-content` positioning and show-on-hover behavior.
- Link hover states inside the flyout panel.


### 2h. CSS — search and trip form scaffolding (L180–L232)

**Purpose:** Layout for search-related stacks and trip controls that are not the full planner cards yet.

- `.search-input`, `.trip-search-form`, `.trip-input-stack`, labels for primary destination.
- Start-mode radios and history button already overlap with action row visually but these rules support form density inside cards.


### 2i. CSS — main surfaces (comment: "map container", L233–L891)

**Purpose:** Most of the application UI: planner grid, cards, trip configuration, map stage, metrics, route cards, profile summary, history list, prediction UI, and the map web component.

- **Note:** The source comment says `/* map container */` but the rules extend well beyond `.map-container` to cover planner cards, destination rows, route option buttons, profile metrics, `gmp-map` sizing, `.predict-btn`, `.result-box`, `.field`, `.span-2`, etc.
- Defines the green/white card system, grids for two-column planner on desktop, and dense UI for stops, optimize toggle, and submit button.
- `.map-stage` minimum height; `gmp-map` height and rounding for the embedded map element style used with Google Maps.


### 2j. CSS — additional info banner (L892–L911)

**Purpose:** `.eco-note` inline pill under the header area with icon + short tagline styling.


### 2k. CSS — responsive layout (L912–L942)

**Purpose:** `@media (max-width: 700px)` — stack columns, shrink map height, single-column grids, adjust title size and `.span-2` grid spanning.


### 2l. CSS — toast notification (L943–L970)

**Purpose:** `.toast-msg` fixed bottom-center bubble; `.toast-msg.show` for fade/scale in (created/updated from script).


### 2m. CSS — autocomplete dropdown (L971–L1081)

**Purpose:** Styles for custom Places suggestion list under inputs.

- Wrapper, dropdown panel, items, hover/highlight, loading and empty states.
- `@media (max-width: 640px)` tweaks max height and padding for small screens.


### 2n. Close `</style>` and `</head>` (L1082–L1083)

**Purpose:** End of embedded CSS and head section.


## 3. `<body>` — static markup (L1084–L1364)

### 3a. Page header (L1085–L1094)

**Purpose:** Brand row: "Green Leaf" title and `.eco-note` tagline strip.

- Purely presentational structure for the top of the page.


### 3b. Divider (L1094)

**Purpose:** Visual `hr` between header and controls.


### 3c. Action bar (L1096–L1124)

**Purpose:** Primary navigation chrome.

- Profile form with `#profileBtn` (toggles vehicle profile panel in script).
- `.dropdown` with `#menuDiscover`, `#menuFarm`, `#menuEvents`, `#menuProfile` (stubs or scroll actions in script).
- `#historyBtn` opens the history section.


### 3d. Main trip planner (L1126–L1269)

**Purpose:** Two-column `<section class="planner-grid">` with the vehicle profile card and the location/trip card.

- **`#profileMenu` (hidden by default):** `#Make`, `#Model`, `#EngineSize`, `#FuelType` selects inside `#carSelector`; `#saveProfileBtn`, `#profileStatus`, `#activeVehicleBadge`.
- **Location card:** Explains geolocation / IP / fallback; `#locateBtn`, `#locationBadge`.
- **Form `class="ser trip-search-form"`:** Trip configuration — `#searchInput` + `#searchInput-autocomplete`; start mode radios `#startModeCurrent` / `#startModeCustom`; `#startLocationInput` + autocomplete; `#extraDestinations` dynamic rows; `#addDestinationBtn`, `#optimizeOrderToggle`, `#destinationLimitNote`; submit `#searchBtn` ("Get Route").
- **`#uiStatus`:** Inline status/error/success messages from script (`role="alert"`).


### 3e. Map view (L1271–L1274)

**Purpose:** Wrapper `.map-container` with `#map` div where Google Maps attaches.


### 3f. Trip results (L1276–L1288)

**Purpose:** Read-only summary strip after routing.

- `#distanceText`, `#durationText`, `#co2Text` updated when a route is selected.


### 3g. Route options shell (L1290–L1296)

**Purpose:** Empty `#routesList` section; script injects heading, grid, and `.route-option` cards after `/get-greenest-route` responds.


### 3h. Profile summary (L1298–L1335)

**Purpose:** Hidden by default; `#profileSummarySection` shows totals and recent trips.

- Header copy, `#profileTripCountBadge`, metrics (`#profileTotalEmissions`, `#profileTripCount`, `#profileLatestTrip`), `#profileRecentTrips` list container.


### 3i. History panel (L1337–L1358)

**Purpose:** Hidden panel listing the same trip log with `#historyTripCountBadge`, `#historyCloseBtn`, `#historyTripList`.


### 3j. Datalists (L1360–L1363)

**Purpose:** Empty `<datalist id="makeOptions">` (and model/fuel). The live car UI uses `<select>` populated from `/get-cars`; these datalists are placeholders unless wired elsewhere.


### 3k. Script tag opening (L1365)

**Purpose:** Marks start of inline application logic before the large `<script>` block.


## 4. `<script>` — application logic (L1366–L3104)

### 4a. Constants and global state (L1367–L1391)

**Purpose:** Defaults and mutable runtime state for map, markers, routes, API key, destination cap, and `localStorage` key `TRIP_HISTORY_STORAGE_KEY`.

- `DEFAULT_LOCATION` (St. Louis area), `IP_LOOKUP_URL` for coarse IP geolocation, `MAX_DESTINATIONS` (5).


### 4b. Small utilities (L1393–L1414)

**Purpose:** Shared helpers before DOM wiring.

- `fuelTypeMap` / `getFuelLabel` translate dataset fuel codes to readable labels.
- `escapeHtml` for safe string insertion into template literals.


### 4c. DOM references (L1416–L1470)

**Purpose:** Cache `document.getElementById` / `querySelector` handles for elements used throughout the app.

- Includes form `.ser`, route list, profile/history sections, inputs, toggles, and `autocompleteInstances` Map.


### 4d. Google Places autocomplete and nearby helpers (L1472–L1875)

**Purpose:** File section header covers autocomplete plus immediate UX helpers used with maps and forms.

- **`initializeAutocomplete` / `initializeMainAutocompletes`:** Attach `PlacesAutocomplete` to `#searchInput`, `#startLocationInput`, and dynamically added destination inputs.
- **`showToast`:** Creates/updates `.toast-msg` for lightweight feedback.
- **`setProfileMenuState`:** Toggles `#profileMenu` visibility and ARIA on `#profileBtn`.
- **`setUiStatus` / `clearUiStatus`:** Show or hide `#uiStatus` with success/error/info styling.
- **`geocodeLocationQuery`:** POST `/search-location` JSON `{ query }` when the user did not pick a Places suggestion.
- **`PlacesAutocomplete` class:** Debounced `AutocompleteService.getPlacePredictions`, keyboard navigation, `PlacesService.getDetails` for lat/lng, dropdown rendering with escaped HTML, `autocomplete-select` event on pick.


### 4e. Trip history and storage (L1877–L2019)

**Purpose:** Browser `localStorage` persistence and HTML builders for lists.

- `buildTripEntries`, `getTripHistory`, `setTripHistory`, `formatTripDate`, `saveTripToHistory`.
- `renderProfileSummary` and `renderHistoryPanel` refresh `#profileSummarySection` / `#historyPanel` contents.
- `openProfileSection`, `openHistoryPanel`, `closeHistoryPanel` + scroll into view.


### 4f. Vehicle profile management (L2021–L2257)

**Purpose:** Car dataset from backend and cascading `<select>` behavior.

- `populateSelect`, `loadCars` GET `/get-cars`, `populateModels` / `populateEngineSizes` / `populateFuelTypes`.
- `getSelectedCar`, `hasValidCar`, `updateActiveVehicleBadge`.
- `saveProfile` / `loadProfile` read/write `localStorage` key `userCarProfile`; integrates with `setUiStatus` and toast.


### 4g. Location resolution (L2259–L2348)

**Purpose:** Decide where the map starts: browser geolocation, then ipapi.co, then `DEFAULT_LOCATION`.

- `resolveLocationFromGeolocation`, `resolveLocationFromIp`, `resolveInitialLocation` set `pendingInitialLocation`, `userLocation`, and `#locationBadge` text; optionally `centerMap` when map is ready.


### 4h. Destination management (L2350–L2532)

**Purpose:** Multi-stop UI and resolving typed addresses to coordinates.

- `centerMap`, `updateStartModeVisibility`, `getDestinationInputs`, `refreshDestinationControls`, `moveDestinationValue`, `createDestinationItem` (adds row, wires move up/down/remove, new autocomplete).
- `getDestinationQueries`, `getAutocompleteSelectedPlace`, `geocodeLocation` (prefer autocomplete selection else backend geocode).
- `getDestinationInputsWithElements` for ordered resolution in `findGreenestRoute`.


### 4i. Route visualization (L2534–L2740)

**Purpose:** Draw and highlight paths and markers on the Google Map.

- Marker helpers: `clearDestinationMarkers`, `updateDestinationMarkers`, `updateDestinationMarker`.
- Polylines and selection UI: `clearRoutePolylines`, `setRouteHighlight`, `setActiveRouteCard`, `selectRoute` (updates `#distanceText` / `#durationText` / `#co2Text`), `saveSelectedRouteToHistory`, `renderRouteCards`, `drawRoutes` (decoded polylines via Geometry library).


### 4j. Route calculation (L2742–L2879)

**Purpose:** Main submit handler `findGreenestRoute`.

- Validates destinations, vehicle profile, optional custom start geocoding.
- POST `/get-greenest-route` with `origin`, final `destination`, `stops`, `optimize_order`, and `car`.
- On success: `drawRoutes`, `renderRouteCards`, `selectRoute` for greenest, updates status and toast; on failure sets error status.


### 4k. Google Maps API loading (L2881–L2964)

**Purpose:** Securely obtain key and load Maps + libraries.

- `fetchGoogleMapsApiKey` GET `/get-api-key`.
- `loadGoogleMapsAPI` injects script with `libraries=geometry,places` and `callback=initMapCallback`.
- `initMapWithLocation` constructs `google.maps.Map`, user marker, sets `mapReady` and badge from `pendingInitialLocationLabel`.
- `refreshLocation` clears cached location and re-runs detection.


### 4l. Event listeners and startup (L2966–L3101)

**Purpose:** Wire cascading car selects and all UI events after load.

- `attachCarDropdownHandlers` for Make/Model/Engine/Fuel change chain.
- `window.addEventListener("load", async () => { ... })` sequence: `loadCars`, profile load, `resolveInitialLocation`, `loadGoogleMapsAPI`, profile toggle, menu toasts / `openProfileSection`, history open/close, locate refresh, destination add, start mode, save profile, form submit → `findGreenestRoute`, search input clears status, `initializeMainAutocompletes`, welcome toast; catch sets fatal-ish `#uiStatus`.
- **`window.handleSearch = findGreenestRoute` (L3103):** Global alias for external or inline triggers.


### 4m. Close `</script>` (L3104)

**Purpose:** End of inline script.


## 5. Trailing HTML comment (L3106–L3109)

**Purpose:** Developer note about API key handling and map behavior; not executed by the browser.


## 6. Close `</body></html>` (L3110–L3111)

**Purpose:** End of document.


---
Backend endpoints referenced from this page
-------------------------------------------
- GET `/get-cars` — vehicle list for selects.
- GET `/get-api-key` — Google Maps JavaScript API key for client loader.
- POST `/search-location` — geocode a free-text query when Places selection is not used.
- POST `/get-greenest-route` — compute route alternatives, emissions, polylines.

Third-party: `https://ipapi.co/json/...` for approximate location; Google Maps / Places / Geometry libraries loaded from `maps.googleapis.com`.
