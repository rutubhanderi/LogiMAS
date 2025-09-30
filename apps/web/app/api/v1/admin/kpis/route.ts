import { NextResponse } from 'next/server';
import { supabase } from '../../../../../lib/supabaseClient';

export const dynamic = 'force-dynamic'; // Ensure fresh data on every request

export async function GET() {
  try {
    // Query the materialized view directly
    const { data, error } = await supabase
      .from('daily_on_time_rate')
      .select('*')
      .order('ship_date', { ascending: false })
      .limit(30); // Get the last 30 days of data

    if (error) {
      console.error('Error fetching KPIs:', error);
      throw new Error(error.message);
    }

    return NextResponse.json(data);

  } catch (err: any) {
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}