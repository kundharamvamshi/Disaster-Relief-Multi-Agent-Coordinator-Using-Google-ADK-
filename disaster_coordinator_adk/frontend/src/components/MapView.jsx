// src/components/MapView.jsx
import React, { useEffect, useRef } from "react";
import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  useMap,
  CircleMarker
} from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

// Fix default icon paths for Vite + Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: new URL('leaflet/dist/images/marker-icon-2x.png', import.meta.url).href,
  iconUrl: new URL('leaflet/dist/images/marker-icon.png', import.meta.url).href,
  shadowUrl: new URL('leaflet/dist/images/marker-shadow.png', import.meta.url).href,
});

// small helper to invalidate size after mount
function MapSizer() {
  const map = useMap();
  useEffect(() => {
    const id = setTimeout(() => {
      try { map.invalidateSize(true); } catch (e) {}
    }, 200);
    return () => clearTimeout(id);
  }, [map]);
  return null;
}

function riskColor(r) {
  if (r >= 0.85) return "#b91c1c";
  if (r >= 0.6) return "#f59e0b";
  if (r >= 0.35) return "#059669";
  return "#2563eb";
}

// helper to create a small colored div icon (so it's clearly clickable)
function createColoredIcon(color = "#2563eb") {
  const svg = encodeURIComponent(
    `<svg xmlns="http://www.w3.org/2000/svg" width="28" height="36" viewBox="0 0 24 24" fill="${color}" stroke="white" stroke-width="0"><path d="M12 2C8 2 5 5 5 8.8 5 13.5 12 22 12 22s7-8.5 7-13.2C19 5 16 2 12 2z"/></svg>`
  );
  const iconUrl = `data:image/svg+xml;charset=UTF-8,${svg}`;
  return new L.Icon({
    iconUrl,
    iconSize: [28, 36],
    iconAnchor: [14, 36],
    popupAnchor: [0, -36],
    className: ""
  });
}

export default function MapView({ incidents = [], onSelect = () => {} }) {
  // pick first incident with coords or default center
  const first = incidents.find(i => i.payload && i.payload.lat && i.payload.lon);
  const center = first ? [first.payload.lat, first.payload.lon] : [20.5937, 78.9629];

  // markerRefs map to allow programmatic openPopup if needed
  const markerRefs = useRef({});

  // ensure markers are clickable: handle click to both open popup and call onSelect
  function handleMarkerClick(inc, markerRef) {
    // open popup programmatically (works across versions)
    try {
      const m = markerRef && markerRef.current;
      if (m && m.openPopup) m.openPopup();
      else if (m && m._popup && m._popup._open) { /* already open */ }
    } catch (e) {
      // ignore
    }
    // call provided handler
    try { onSelect(inc); } catch (e) { console.error("onSelect error", e); }
  }

  return (
    <div className="w-full h-[520px] rounded shadow overflow-hidden relative">
      <MapContainer
        center={center}
        zoom={5}
        style={{ height: "100%", width: "100%" }}
        scrollWheelZoom={true}
      >
        <MapSizer />
        <TileLayer
          attribution='&copy; OpenStreetMap contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {incidents.map((inc) => {
          const lat = inc?.payload?.lat;
          const lon = inc?.payload?.lon;
          if (!lat || !lon) return null;

          const risk = inc._ui_risk ?? 0.4;
          const color = riskColor(risk);
          // create a unique ref for each marker
          if (!markerRefs.current[inc.id]) markerRefs.current[inc.id] = React.createRef();

          // Use a real Marker (with icon) so clicking works consistently, but also render a circle marker for radius feel
          return (
            <React.Fragment key={inc.id}>
              <Marker
                position={[lat, lon]}
                icon={createColoredIcon(color)}
                ref={markerRefs.current[inc.id]}
                eventHandlers={{
                  click: () => handleMarkerClick(inc, markerRefs.current[inc.id])
                }}
              >
                <Popup>
                  <div className="min-w-[180px]">
                    <div className="font-semibold">{inc.type} — {inc.location}</div>
                    <div className="text-xs">Risk: {(risk).toFixed(2)}</div>
                    <div className="text-xs">Time: {new Date(inc.time).toLocaleString()}</div>
                    <div className="mt-2 text-xs text-slate-600">Click the marker to plan / select</div>
                  </div>
                </Popup>
              </Marker>

              {/* optional: visual circle under the marker */}
              <CircleMarker
                center={[lat, lon]}
                radius={10}
                pathOptions={{ color, fillOpacity: 0.2 }}
                interactive={false}
              />
            </React.Fragment>
          );
        })}
      </MapContainer>
    </div>
  );
}
