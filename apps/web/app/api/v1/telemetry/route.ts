import { NextResponse } from 'next/server';
import { supabase } from '../../../../lib/supabaseClient';

// Define the expected structure of a single telemetry event
interface TelemetryEvent {
  vehicle_id: string;
  ts: string; // ISO 8601 timestamp string
  lat: number;
  lon: number;
  speed_kmph: number;
  fuel_pct: number;
  cargo_temp?: number; // Optional
}

// This function handles POST requests to /api/v1/telemetry
export async function POST(request: Request) {
  try {
    // The body can be a single event or an array of events
    const payload: TelemetryEvent | TelemetryEvent[] = await request.json();

    // Ensure the payload is an array for consistent processing
    const events = Array.isArray(payload) ? payload : [payload];

    if (events.length === 0) {
      return NextResponse.json({ message: 'No events to process' }, { status: 200 });
    }
    
    // Use the Supabase client to insert the data into the vehicle_telemetry table
    // The client is smart enough to handle inserting multiple rows at once.
    const { error } = await supabase
      .from('vehicle_telemetry')
      .insert(events);

    if (error) {
      console.error('Supabase telemetry insert error:', error);
      return NextResponse.json({ error: error.message }, { status: 500 });
    }

    return NextResponse.json({ message: `Successfully ingested ${events.length} event(s)` }, { status: 201 });

  } catch (err: any) {
    console.error('Telemetry ingestion error:', err);
    return NextResponse.json({ error: 'Invalid request body or internal error' }, { status: 400 });
  }
}