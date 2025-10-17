import { useEffect, useMemo, useState } from "react";
import { MapContainer, TileLayer, CircleMarker, Tooltip, Popup } from "react-leaflet";

const MAP_CENTER = [53.5461, -113.4938];
const MAP_LAYERS = {
  streets: {
    label: "Street Map",
    attribution:
      "&copy; <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a> contributors",
    url: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
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
const API_BASE = "http://127.0.0.1:8000";
const GEOJSON_ENDPOINTS = {
  miovision: `${API_BASE}/geojson/mv_points_snapped`,
  estimation: `${API_BASE}/geojson/estimation_points_snapped`
};

const CSV_HEADERS = ["id", "year", "direction", "lat", "lon"];

const getLatLon = (feature) => {
  const props = feature?.properties ?? {};
  const coords = Array.isArray(feature?.geometry?.coordinates)
    ? feature.geometry.coordinates
    : [];

  const lat = typeof props.lat === "number" ? props.lat : coords[1];
  const lon = typeof props.lon === "number" ? props.lon : coords[0];

  return {
    lat: typeof lat === "number" ? lat : null,
    lon: typeof lon === "number" ? lon : null
  };
};

const formatCoordinate = (value) => {
  if (typeof value !== "number") {
    return "N/A";
  }
  return value.toFixed(5);
};

export default function MapView() {
  const [activeLayer, setActiveLayer] = useState("streets");
  const [startYear, setStartYear] = useState(DEFAULT_START_YEAR);
  const [endYear, setEndYear] = useState(DEFAULT_END_YEAR);
  const [direction, setDirection] = useState("All");
  const [studies, setStudies] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [hasFiltered, setHasFiltered] = useState(false);
  const [selectedStudy, setSelectedStudy] = useState(null);

  const [miovisionEnabled, setMiovisionEnabled] = useState(true);
  const [estimationEnabled, setEstimationEnabled] = useState(true);
  const [miovisionFeatures, setMiovisionFeatures] = useState([]);
  const [estimationFeatures, setEstimationFeatures] = useState([]);
  const [layerErrors, setLayerErrors] = useState({ miovision: null, estimation: null });

  useEffect(() => {
    const fetchMiovision = async () => {
      try {
        const response = await fetch(GEOJSON_ENDPOINTS.miovision);
        if (!response.ok) {
          throw new Error(`Failed with status ${response.status}`);
        }
        const data = await response.json();
        const features = Array.isArray(data?.features) ? data.features : [];
        setMiovisionFeatures(features);
        setLayerErrors((prev) => ({ ...prev, miovision: null }));
      } catch (fetchError) {
        setLayerErrors((prev) => ({
          ...prev,
          miovision: "Unable to load Miovision points."
        }));
      }
    };

    if (miovisionEnabled && miovisionFeatures.length === 0) {
      fetchMiovision();
    }
  }, [miovisionEnabled, miovisionFeatures.length]);

  useEffect(() => {
    const fetchEstimation = async () => {
      try {
        const response = await fetch(GEOJSON_ENDPOINTS.estimation);
        if (!response.ok) {
          throw new Error(`Failed with status ${response.status}`);
        }
        const data = await response.json();
        const features = Array.isArray(data?.features) ? data.features : [];
        setEstimationFeatures(features);
        setLayerErrors((prev) => ({ ...prev, estimation: null }));
      } catch (fetchError) {
        setLayerErrors((prev) => ({
          ...prev,
          estimation: "Unable to load estimation points."
        }));
      }
    };

    if (estimationEnabled && estimationFeatures.length === 0) {
      fetchEstimation();
    }
  }, [estimationEnabled, estimationFeatures.length]);

  const handleFilter = async () => {
    setLoading(true);
    setError(null);
    setHasFiltered(true);
    setSelectedStudy(null);
    setStudies([]);

    try {
      const params = new URLSearchParams({
        start_year: startYear.toString(),
        end_year: endYear.toString()
      });

      if (direction && direction !== "All") {
        params.append("direction", direction);
      }

      const response = await fetch(`${API_BASE}/query/studies?${params.toString()}`);

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
      setLoading(false);
    }
  };

  const handleReset = () => {
    setStartYear(DEFAULT_START_YEAR);
    setEndYear(DEFAULT_END_YEAR);
    setDirection("All");
    setStudies([]);
    setError(null);
    setHasFiltered(false);
    setSelectedStudy(null);
  };

  const handleExport = () => {
    if (!studies.length) {
      return;
    }

    const rows = studies.map((feature) => {
      const props = feature?.properties ?? {};
      const { lat, lon } = getLatLon(feature);
      return [
        props.id ?? "",
        props.year ?? "",
        props.direction ?? "",
        lat ?? "",
        lon ?? ""
      ].join(",");
    });

    const csvContent = [CSV_HEADERS.join(","), ...rows].join("\n");
    const blob = new Blob([`${csvContent}\n`], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", "traffic_studies.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handleSelectStudy = (feature) => {
    setSelectedStudy(feature);
  };

  const closeSidebar = () => {
    setSelectedStudy(null);
  };

  const selectedDetails = useMemo(() => {
    if (!selectedStudy) {
      return null;
    }

    const props = selectedStudy.properties ?? {};
    const { lat, lon } = getLatLon(selectedStudy);

    return {
      id: props.id ?? "Unknown",
      year: props.year ?? "N/A",
      direction: props.direction ?? "N/A",
      lat,
      lon
    };
  }, [selectedStudy]);

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
            <div className="layer-toggle-group">
              <label className="layer-toggle-option">
                <input
                  type="checkbox"
                  checked={miovisionEnabled}
                  onChange={(event) => setMiovisionEnabled(event.target.checked)}
                />
                Miovision Points
              </label>
              <label className="layer-toggle-option">
                <input
                  type="checkbox"
                  checked={estimationEnabled}
                  onChange={(event) => setEstimationEnabled(event.target.checked)}
                />
                Estimation Points
              </label>
              {layerErrors.miovision ? (
                <p className="layer-error">{layerErrors.miovision}</p>
              ) : null}
              {layerErrors.estimation ? (
                <p className="layer-error">{layerErrors.estimation}</p>
              ) : null}
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
            {loading ? <p className="loading-message">Loading studies...</p> : null}
            <div className="filter-actions">
              <button type="button" className="filter-button" onClick={handleFilter} disabled={loading}>
                Filter
              </button>
              <button type="button" className="reset-button" onClick={handleReset} disabled={loading}>
                Reset Filters
              </button>
            </div>
            <button
              type="button"
              className="export-button"
              onClick={handleExport}
              disabled={!studies.length || loading}
            >
              Export Results
            </button>
            {error ? <p className="filter-error">{error}</p> : null}
            {!error && hasFiltered && studies.length === 0 && !loading ? (
              <p className="filter-empty">No studies match the current filters.</p>
            ) : null}
          </div>
        </div>

        <div className="map-content">
          <MapContainer
            center={MAP_CENTER}
            zoom={12}
            scrollWheelZoom
            className="map-placeholder"
            style={{ height: "100%", width: "100%" }}
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

              const { lat: latProp, lon: lonProp } = getLatLon(feature);

              return (
                <CircleMarker
                  key={properties?.id ?? `${lat}-${lon}`}
                  center={[lat, lon]}
                  radius={8}
                  eventHandlers={{
                    click: () => handleSelectStudy(feature)
                  }}
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
                  <Popup>
                    <div>
                      <strong>Study:</strong> {properties?.id ?? "Unknown ID"}
                      <br />
                      <strong>Year:</strong> {properties?.year ?? "N/A"}
                      <br />
                      <strong>Direction:</strong> {properties?.direction ?? "Unknown"}
                      <br />
                      <strong>Lat:</strong> {formatCoordinate(latProp ?? lat)}
                      <br />
                      <strong>Lon:</strong> {formatCoordinate(lonProp ?? lon)}
                    </div>
                  </Popup>
                </CircleMarker>
              );
            })}

            {miovisionEnabled
              ? miovisionFeatures.map((feature, index) => {
                  const coordinates = feature?.geometry?.coordinates;
                  if (!Array.isArray(coordinates) || coordinates.length < 2) {
                    return null;
                  }

                  const [lon, lat] = coordinates;

                  if (typeof lat !== "number" || typeof lon !== "number") {
                    return null;
                  }

                  const id = feature?.properties?.id ?? `MV-${index + 1}`;

                  return (
                    <CircleMarker
                      key={`mv-${id}`}
                      center={[lat, lon]}
                      radius={6}
                      pathOptions={{ color: "#16a34a", fillColor: "#22c55e", fillOpacity: 0.75 }}
                    >
                      <Tooltip>Miovision: {id}</Tooltip>
                      <Popup>
                        <div>
                          <strong>Miovision Point</strong>
                          <br />
                          ID: {id}
                        </div>
                      </Popup>
                    </CircleMarker>
                  );
                })
              : null}

            {estimationEnabled
              ? estimationFeatures.map((feature, index) => {
                  const coordinates = feature?.geometry?.coordinates;
                  if (!Array.isArray(coordinates) || coordinates.length < 2) {
                    return null;
                  }

                  const [lon, lat] = coordinates;

                  if (typeof lat !== "number" || typeof lon !== "number") {
                    return null;
                  }

                  const id = feature?.properties?.id ?? `EST-${index + 1}`;

                  return (
                    <CircleMarker
                      key={`est-${id}`}
                      center={[lat, lon]}
                      radius={6}
                      pathOptions={{ color: "#dc2626", fillColor: "#f87171", fillOpacity: 0.75 }}
                    >
                      <Tooltip>Estimation: {id}</Tooltip>
                      <Popup>
                        <div>
                          <strong>Estimation Point</strong>
                          <br />
                          ID: {id}
                        </div>
                      </Popup>
                    </CircleMarker>
                  );
                })
              : null}
          </MapContainer>

          <aside className={`map-sidebar${selectedDetails ? " open" : ""}`}>
            <div className="map-sidebar__header">
              <h3 className="map-sidebar__title">Study Details</h3>
              <button
                type="button"
                className="map-sidebar__close"
                onClick={closeSidebar}
                aria-label="Close study details"
              >
                &times;
              </button>
            </div>
            {selectedDetails ? (
              <div className="map-sidebar__body">
                <div className="map-sidebar__item">
                  <span className="map-sidebar__label">Study ID</span>
                  <strong className="map-sidebar__value">{selectedDetails.id}</strong>
                </div>
                <div className="map-sidebar__item">
                  <span className="map-sidebar__label">Year</span>
                  <span className="map-sidebar__value">{selectedDetails.year}</span>
                </div>
                <div className="map-sidebar__item">
                  <span className="map-sidebar__label">Direction</span>
                  <span className="map-sidebar__value">{selectedDetails.direction}</span>
                </div>
                <div className="map-sidebar__item">
                  <span className="map-sidebar__label">Latitude</span>
                  <span className="map-sidebar__value">{formatCoordinate(selectedDetails.lat)}</span>
                </div>
                <div className="map-sidebar__item">
                  <span className="map-sidebar__label">Longitude</span>
                  <span className="map-sidebar__value">{formatCoordinate(selectedDetails.lon)}</span>
                </div>
                <button type="button" className="report-button">
                  Generate Report
                </button>
              </div>
            ) : (
              <p className="map-sidebar__empty">Select a study marker to view its details.</p>
            )}
          </aside>
        </div>
      </div>
      <footer className="map-footer">
        Demo data only — real study data integration pending (© 2025 City of Edmonton / GeoTrans Lab UAlberta)
      </footer>
    </section>
  );
}
