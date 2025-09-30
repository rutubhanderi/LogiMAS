'use client';

import { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import { supabase } from '../../lib/supabaseClient';


const LiveTrackingMap = dynamic(
  () => import('../maps/LiveTrackingMap').then((mod) => mod.LiveTrackingMap),
  { 
    ssr: false,     
    loading: () => (
      <div style={{ height: '400px', background: '#f3f4f6', display: 'flex', alignItems: 'center', justifyContent: 'center' }} className="rounded-md">
        <p className="text-gray-500">Loading map...</p>
      </div>
    )
  }
);

type Telemetry = {
  lat: number;
  lon: number;
  speed_kmph: number;
  ts: string;
};


interface RealtimeTelemetryProps {
  vehicleId: string;
  vehicleType: string;
}

export function RealtimeTelemetry({ vehicleId, vehicleType }: RealtimeTelemetryProps) {
  const [latest, setLatest] = useState<Telemetry | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!vehicleId) return;

    // 1. Fetch the most recent telemetry point on initial component load
    const fetchInitialTelemetry = async () => {
      const { data, error } = await supabase
        .from('vehicle_telemetry')
        .select('lat, lon, speed_kmph, ts')
        .eq('vehicle_id', vehicleId)
        .order('ts', { ascending: false })
        .limit(1)
        .single();
      
      if (error && error.code !== 'PGRST116') { // PGRST116 means no rows were found, which is not an error
        setError(`Failed to fetch initial telemetry: ${error.message}`);
      } else if (data) {
        setLatest(data);
      }
    };

    fetchInitialTelemetry();

    // 2. Set up the real-time subscription to listen for new 'INSERT' events
    const channel = supabase
      .channel(`telemetry:${vehicleId}`)
      .on(
        'postgres_changes',
        {
          event: 'INSERT',
          schema: 'public',
          table: 'vehicle_telemetry',
          filter: `vehicle_id=eq.${vehicleId}`, // Only listen for changes for this specific vehicle
        },
        (payload) => {
          console.log('New telemetry received via real-time!', payload.new);
          setLatest(payload.new as Telemetry);
        }
      )
      .subscribe((status, err) => {
        if (status === 'SUBSCRIBED') {
          console.log(`Successfully subscribed to telemetry updates for vehicle ${vehicleId}`);
        }
        if (err) {
          console.error('Real-time subscription error:', err);
          setError('Could not subscribe to real-time updates.');
        }
      });

    // 3. Clean up by removing the channel subscription when the component unmounts
    return () => {
      supabase.removeChannel(channel);
    };

  }, [vehicleId]); // Re-run this effect if the vehicleId prop ever changes

  if (error) {
    return <div className="p-4 bg-red-100 text-red-700 rounded-md">Error: {error}</div>;
  }

  return (
    <div className="mt-8 border-t pt-6">
      <h3 className="text-lg font-semibold mb-4">Live Vehicle Location</h3>
      
      {/* Conditionally render the map or a placeholder */}
      {!latest ? (
        <div style={{ height: '400px', background: '#f3f4f6', display: 'flex', alignItems: 'center', justifyContent: 'center' }} className="rounded-md">
          <p className="text-gray-500">Awaiting first telemetry signal...</p>
        </div>
      ) : (
        <div className="rounded-lg overflow-hidden border shadow-sm">
          <LiveTrackingMap 
            lat={latest.lat} 
            lon={latest.lon}
            vehicleType={vehicleType}
            lastUpdate={latest.ts}
          />
        </div>
      )}
      
      {/* Display supplementary telemetry data below the map */}
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 mt-4 text-gray-700">
        <div>
          <p className="text-sm font-medium text-gray-500">Speed</p>
          <p className="font-semibold">{latest ? `${latest.speed_kmph} km/h` : 'N/A'}</p>
        </div>
        <div>
          <p className="text-sm font-medium text-gray-500">Last Update</p>
          <p className="text-xs">{latest ? new Date(latest.ts).toLocaleString() : 'N/A'}</p>
        </div>
      </div>
    </div>
  );
}