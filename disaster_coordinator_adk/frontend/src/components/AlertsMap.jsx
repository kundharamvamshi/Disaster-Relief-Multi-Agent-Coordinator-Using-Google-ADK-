import React from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
// optionally fix icon path warning
import L from "leaflet";
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png')
});

export default function AlertsMap({alerts}) {
  const center = alerts && alerts.length ? [17.3850, 78.4867] : [20.5937, 78.9629]; // fallback
  return (
    <MapContainer center={center} zoom={5} style={{height: "300px", width: "100%"}}>
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      {alerts.map((a) => {
        // NOTE: this requires geocoding (see part D) to convert location name -> lat/lon
        // for now place markers approximately via a small static map table or skip
        const latlon = a._latlon || null;
        if (!latlon) return null;
        return (
          <Marker key={a.id} position={latlon}>
            <Popup>
              <div><strong>{a.type}</strong><div>{a.location}</div><div>{a.time}</div></div>
            </Popup>
          </Marker>
        )
      })}
    </MapContainer>
  );
}
