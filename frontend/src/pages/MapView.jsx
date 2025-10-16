import { useState } from "react";
import { MapContainer, TileLayer, CircleMarker, Tooltip } from "react-leaflet";

const MAP_CENTER = [53.5461, -113.4938];
const MAP_LAYERS = {
  streets: {
    label: "Street Map",
    attribution:
      "&copy; <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a> contributors",
    url: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
  },
  transit: {
    label: "Stamen Toner",
    attribution:
      "Map tiles by <a href='http://stamen.com'>Stamen Design</a>, CC BY 3.0 — Map data © <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a>",
    url: "https://stamen-tiles.a.ssl.fastly.net/toner/{z}/{x}/{y}.png"
  },
  imagery: {
    label: "Satellite Imagery",
    attribution:
      "Tiles © Esri — Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community",
    url: "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
  }
};

const DIRECTION_OPTIONS = ["All", "Northbound", "Southbound", "Eastbound", "Westbound"];
const DEFAULT_START_YEAR = 2020;
const DEFAULT_END_YEAR = 2024;

export default function MapView() {
  const [activeLayer, setActiveLayer] = useState("streets");
  const [startYear, setStartYear] = useState(DEFAULT_START_YEAR);
  const [endYear, setEndYear] = useState(DEFAULT_END_YEAR);
  const [direction, setDirection] = useState("All");
  const [studies, setStudies] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFilter = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams({
        start_year: startYear.toString(),
        end_year: endYear.toString()
      });

      if (direction && direction !== "All") {
        params.append("direction", direction);
      }

      const response = await fetch(`http://127.0.0.1:8000/query/studies?${params.toString()}`);

      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`);
      }

      const data = await response.json();
      const features = Array.isArray(data?.features) ? data.features : [];
      setStudies(features);
    } catch (fetchError) {
      const message = fetchError instanceof Error ? fetchError.message : "Failed to load studies.";
      setError(message);
      setStudies([]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section className="map-page">
      <div className="map-wrapper">
        <div className="map-controls">
          <div className="map-layer-card">
            <h3>Map Layers</h3>
            <div className="map-layer-options">
              {Object.entries(MAP_LAYERS).map(([key, layer]) => (
                <label key={key} className="map-layer-option">
                  <input
                    type="radio"
                    name="map-layer"
                    value={key}
                    checked={activeLayer === key}
                    onChange={() => setActiveLayer(key)}
                  />
                  {layer.label}
                </label>
              ))}
            </div>
          </div>

          <div className="map-filter-card">
            <h3>Filter Studies</h3>
            <div className="filter-grid">
              <label className="filter-field">
                <span>Start Year</span>
                <input
                  type="number"
                  value={startYear}
                  onChange={(event) => setStartYear(Number(event.target.value) || DEFAULT_START_YEAR)}
                  className="filter-input"
                />
              </label>
              <label className="filter-field">
                <span>End Year</span>
                <input
                  type="number"
                  value={endYear}
                  onChange={(event) => setEndYear(Number(event.target.value) || DEFAULT_END_YEAR)}
                  className="filter-input"
                />
              </label>
              <label className="filter-field">
                <span>Direction</span>
                <select
                  value={direction}
                  onChange={(event) => setDirection(event.target.value)}
                  className="filter-input"
                >
                  {DIRECTION_OPTIONS.map((option) => (
                    <option key={option} value={option}>
                      {option}
                    </option>
                  ))}
                </select>
              </label>
            </div>
            <button type="button" className="filter-button" onClick={handleFilter} disabled={isLoading}>
              {isLoading ? "Filtering..." : "Filter"}
            </button>
            {error ? <p className="filter-error">{error}</p> : null}
            {!error && studies.length === 0 && !isLoading ? (
              <p className="filter-empty">No studies match the current filters.</p>
            ) : null}
          </div>
        </div>

        <MapContainer
          center={MAP_CENTER}
          zoom={12}
          scrollWheelZoom
          className="map-placeholder"
          style={{
            height: "calc(100vh - 128px)",
            width: "100%"
          }}
        >
          <TileLayer
            attribution={MAP_LAYERS[activeLayer].attribution}
            url={MAP_LAYERS[activeLayer].url}
          />
          {studies.map((feature) => {
            const coordinates = feature?.geometry?.coordinates;
            const properties = feature?.properties;
            if (!Array.isArray(coordinates) || coordinates.length < 2) {
              return null;
            }

            const [lon, lat] = coordinates;

            if (typeof lat !== "number" || typeof lon !== "number") {
              return null;
            }

            return (
              <CircleMarker
                key={properties?.id ?? `${lat}-${lon}`}
                center={[lat, lon]}
                radius={8}
                pathOptions={{ color: "#1d4ed8", fillColor: "#1d4ed8", fillOpacity: 0.7 }}
              >
                <Tooltip>
                  <div>
                    <strong>{properties?.id ?? "Unknown ID"}</strong>
                    <br />
                    Year: {properties?.year ?? "N/A"}
                    <br />
                    Direction: {properties?.direction ?? "Unknown"}
                  </div>
                </Tooltip>
              </CircleMarker>
            );
          })}
        </MapContainer>
      </div>
    </section>
  );
}
