'use client';

import { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import { supabase } from '../../lib/supabaseClient';

const LiveTrackingMap = dynamic(
  () => import('../maps/LiveTrackingMap').then((mod) => mod.LiveTrackingMap),
  { 
    ssr: false,     
    loading: () => <div style={{ height: '400px', background: '#f3f4f6' }} className="rounded-md animate-pulse" />
  }
);

type Telemetry = { lat: number; lon: number; speed_kmph: number; ts: string; };
interface RealtimeTelemetryProps { vehicleId: string; vehicleType: string; }

export function RealtimeTelemetry({ vehicleId, vehicleType }: RealtimeTelemetryProps) {
  const [latest, setLatest] = useState<Telemetry | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!vehicleId) return;

    const fetchInitialTelemetry = async () => {
      const { data, error } = await supabase
        .from('vehicle_telemetry')
        .select('lat, lon, speed_kmph, ts')
        .eq('vehicle_id', vehicleId)
        .order('ts', { ascending: false }) // <-- CORRECT SYNTAX FOR supabase-js
        .limit(1)
        .single();
      
      if (error && error.code !== 'PGRST116') {
        setError(`Failed to fetch initial telemetry: ${error.message}`);
      } else if (data) {
        setLatest(data);
      }
    };

    fetchInitialTelemetry();

    const channel = supabase
      .channel(`telemetry:${vehicleId}`)
      .on('postgres_changes', {
          event: 'INSERT', schema: 'public', table: 'vehicle_telemetry',
          filter: `vehicle_id=eq.${vehicleId}`,
        },
        (payload) => { setLatest(payload.new as Telemetry); }
      )
      .subscribe((status, err) => {
        if (status === 'SUBSCRIBED') { console.log(`Subscribed to telemetry for vehicle ${vehicleId}`); }
        if (err) { setError('Could not subscribe to real-time updates.'); }
      });

    return () => { supabase.removeChannel(channel); };
  }, [vehicleId]);

  if (error) {
    return <div className="p-4 bg-red-100 text-red-700 rounded-md">Error: {error}</div>;
  }

  return (
    <div className="mt-8 border-t border-slate-200 pt-6">
      <h3 className="text-lg font-semibold text-slate-800 mb-4">Live Vehicle Location</h3>
      
      <div className="rounded-lg overflow-hidden border shadow-sm">
        {!latest ? (
          <div style={{ height: '400px', background: '#f3f4f6' }} className="rounded-md animate-pulse flex items-center justify-center">
            <p className="text-slate-500">Awaiting first telemetry signal...</p>
          </div>
        ) : (
          <LiveTrackingMap 
            lat={latest.lat} 
            lon={latest.lon}
            vehicleType={vehicleType}
            lastUpdate={latest.ts}
          />
        )}
      </div>
      
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 mt-4 text-slate-700">
        <div>
          <p className="text-sm font-medium text-slate-500">Speed</p>
          <p className="font-semibold text-base">{latest ? `${latest.speed_kmph} km/h` : 'N/A'}</p>
        </div>
        <div>
          <p className="text-sm font-medium text-slate-500">Last Update</p>
          <p className="text-sm">{latest ? new Date(latest.ts).toLocaleString() : 'N/A'}</p>
        </div>
      </div>
    </div>
  );
}