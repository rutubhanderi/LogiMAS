'use client';

import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { useEffect } from 'react';

// --- THIS IS THE CRUCIAL PART FOR FIXING THE ICONS ---

// 1. Import the image files directly. Webpack will handle these imports
//    and provide the correct public URLs.
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

// 2. Delete the old icon options that Leaflet's CSS might be using.
// @ts-ignore
delete L.Icon.Default.prototype._getIconUrl;

// 3. Re-configure Leaflet's default icon with the imported image paths.
L.Icon.Default.mergeOptions({
  iconUrl: markerIcon.src,
  iconRetinaUrl: markerIcon2x.src,
  shadowUrl: markerShadow.src,
});

// --- END OF ICON FIX ---


// A helper component to smoothly pan the map when the position changes
function ChangeView({ center }: { center: [number, number] }) {
  const map = useMap();
  useEffect(() => {
    map.flyTo(center, map.getZoom());
  }, [center, map]);
  return null;
}

interface LiveTrackingMapProps {
  lat: number;
  lon: number;
  vehicleType: string;
  lastUpdate: string;
}

export function LiveTrackingMap({ lat, lon, vehicleType, lastUpdate }: LiveTrackingMapProps) {
  const position: [number, number] = [lat, lon];

  return (
    <MapContainer center={position} zoom={14} scrollWheelZoom={false} style={{ height: '400px', width: '100%' }}>
      <ChangeView center={position} />
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <Marker position={position}>
        <Popup>
          <b>{vehicleType}</b><br />
          Last update: {new Date(lastUpdate).toLocaleTimeString()}
        </Popup>
      </Marker>
    </MapContainer>
  );
}