'use client';

import { useEffect, useState } from 'react';
import { supabase } from '../../lib/supabaseClient';

// Define the structure of our telemetry data
type Telemetry = {
  lat: number;
  lon: number;
  speed_kmph: number;
  ts: string;
};

export function RealtimeTelemetry({ vehicleId }: { vehicleId: string }) {
  const [latest, setLatest] = useState<Telemetry | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!vehicleId) return;

    // 1. Fetch the most recent telemetry point on initial load
    const fetchInitialTelemetry = async () => {
      const { data, error } = await supabase
        .from('vehicle_telemetry')
        .select('lat, lon, speed_kmph, ts')
        .eq('vehicle_id', vehicleId)
        .order('ts', { ascending: false })
        .limit(1)
        .single();
      
      if (error && error.code !== 'PGRST116') { // PGRST116 = no rows found
        setError(error.message);
      } else if (data) {
        setLatest(data);
      }
    };

    fetchInitialTelemetry();

    // 2. Set up the real-time subscription
    const channel = supabase
      .channel(`telemetry:${vehicleId}`)
      .on(
        'postgres_changes',
        {
          event: 'INSERT',
          schema: 'public',
          table: 'vehicle_telemetry',
          filter: `vehicle_id=eq.${vehicleId}`,
        },
        (payload) => {
          console.log('New telemetry received!', payload.new);
          setLatest(payload.new as Telemetry);
        }
      )
      .subscribe((status, err) => {
        if (status === 'SUBSCRIBED') {
          console.log(`Subscribed to telemetry for vehicle ${vehicleId}`);
        }
        if (err) {
          console.error('Subscription error:', err);
          setError('Could not subscribe to real-time updates.');
        }
      });

    // 3. Clean up the subscription when the component unmounts
    return () => {
      supabase.removeChannel(channel);
    };

  }, [vehicleId]); // Re-run effect if vehicleId changes

  if (error) {
    return <div className="p-4 bg-red-100 text-red-700 rounded-md">Error: {error}</div>;
  }

  return (
    <div className="mt-8">
      <h3 className="text-lg font-semibold border-t pt-6">Live Telemetry</h3>
      {!latest ? (
        <p className="mt-2 text-gray-500">Awaiting first telemetry signal...</p>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 mt-4 text-gray-700">
          <div>
            <p className="text-sm font-medium text-gray-500">Latitude</p>
            <p className="font-mono">{latest.lat.toFixed(4)}</p>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500">Longitude</p>
            <p className="font-mono">{latest.lon.toFixed(4)}</p>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500">Speed</p>
            <p>{latest.speed_kmph} km/h</p>
          </div>
          <div className="col-span-2 sm:col-span-3">
            <p className="text-sm font-medium text-gray-500">Last Update</p>
            <p className="text-xs">{new Date(latest.ts).toLocaleString()}</p>
          </div>
        </div>
      )}
    </div>
  );
}