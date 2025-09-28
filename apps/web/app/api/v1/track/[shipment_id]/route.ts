import { NextResponse } from 'next/server';
import { supabase } from '../../../../../lib/supabaseClient';

// This function handles GET requests to /api/v1/track/[shipment_id]
export async function GET(
  request: Request,
  { params }: { params: { shipment_id: string } }
) {
  const { shipment_id } = params;

  if (!shipment_id) {
    return NextResponse.json({ error: 'Shipment ID is required' }, { status: 400 });
  }

  try {
    // Fetch shipment details from the 'shipments' table
    // .select(`...`) allows us to fetch related data from other tables
    // In this case, we're getting order details and vehicle type
    const { data: shipment, error } = await supabase
      .from('shipments')
      .select(`
        shipment_id,
        status,
        current_eta,
        expected_arrival,
        orders (
          order_id,
          destination,
          items
        ),
        vehicles (
          vehicle_type
        )
      `)
      .eq('shipment_id', shipment_id)
      .single(); // .single() expects one result and returns an object, not an array

    if (error) {
      console.error('Supabase error:', error);
      // If no shipment is found, .single() returns an error
      if (error.code === 'PGRST116') {
        return NextResponse.json({ error: 'Shipment not found' }, { status: 404 });
      }
      return NextResponse.json({ error: error.message }, { status: 500 });
    }

    if (!shipment) {
      return NextResponse.json({ error: 'Shipment not found' }, { status: 404 });
    }

    return NextResponse.json(shipment);

  } catch (err) {
    console.error('Catch block error:', err);
    return NextResponse.json({ error: 'An internal error occurred' }, { status: 500 });
  }
}