'use client';

import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Leaflet's default icons can break in Next.js. This is a standard workaround.
import iconUrl from 'leaflet/dist/images/marker-icon.png';
import iconRetinaUrl from 'leaflet/dist/images/marker-icon-2x.png';
import shadowUrl from 'leaflet/dist/images/marker-shadow.png';

const DefaultIcon = L.icon({
    iconUrl,
    iconRetinaUrl,
    shadowUrl,
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
});

L.Marker.prototype.options.icon = DefaultIcon;


interface LiveTrackingMapProps {
  lat: number;
  lon: number;
  vehicleType: string;
  lastUpdate: string;
}

export function LiveTrackingMap({ lat, lon, vehicleType, lastUpdate }: LiveTrackingMapProps) {
  // Use a key based on lat/lon to force the map to re-center when props change
  const mapKey = `${lat}-${lon}`;

  return (
    <MapContainer key={mapKey} center={[lat, lon]} zoom={13} scrollWheelZoom={false} style={{ height: '400px', width: '100%' }}>
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <Marker position={[lat, lon]}>
        <Popup>
          <b>{vehicleType}</b><br />
          Last update: {new Date(lastUpdate).toLocaleTimeString()}
        </Popup>
      </Marker>
    </MapContainer>
  );
}