import { useState } from "react";
import { MapContainer, TileLayer } from "react-leaflet";

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

export default function MapView() {
  const [activeLayer, setActiveLayer] = useState("streets");

  return (
    <section className="map-page">
      <div className="map-wrapper">
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

        <MapContainer
          center={MAP_CENTER}
          zoom={12}
          scrollWheelZoom
          className="map-placeholder"
          style={{
            height: "calc(100vh - 128px)", // Reserve room for the fixed navbar and footer.
            width: "100%"
          }}
        >
          <TileLayer
            attribution={MAP_LAYERS[activeLayer].attribution}
            url={MAP_LAYERS[activeLayer].url}
          />
        </MapContainer>
      </div>
    </section>
  );
}
