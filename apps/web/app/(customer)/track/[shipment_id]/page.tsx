'use client';

import { useEffect, useState } from 'react';
import { supabase } from '../../../../lib/supabaseClient';
import { RealtimeTelemetry } from '../../../../components/ui/RealtimeTelemetry';

// Define the expected shape of the data for this page
type ShipmentPageData = {
  shipment_id: string;
  status: string;
  current_eta: string;
  expected_arrival: string;
  orders: {
    order_id: string;
    items: { sku: string; name: string; price: number }[];
  } | null;
  vehicles: {
    vehicle_id: string;
    vehicle_type: string;
  } | null;
};

export default function TrackShipmentPage({ params }: { params: { shipment_id: string } }) {
  const { shipment_id } = params;
  const [shipment, setShipment] = useState<ShipmentPageData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!shipment_id) {
      setIsLoading(false);
      setError("No shipment ID provided.");
      return;
    }

    const fetchShipmentData = async () => {
      const { data, error } = await supabase
        .from('shipments')
        .select(`
          shipment_id,
          status,
          current_eta,
          expected_arrival,
          orders ( order_id, items ),
          vehicles ( vehicle_id, vehicle_type )
        `)
        .eq('shipment_id', shipment_id)
        .single();

      if (error) {
        console.error("Error fetching shipment:", error.message);
        setError(`Failed to fetch shipment data: ${error.message}`);
      } else if (data) {
        setShipment(data as ShipmentPageData);
      }
      
      setIsLoading(false);
    };

    fetchShipmentData();
  }, [shipment_id]); // Re-fetch if the shipment ID in the URL changes

  // --- Render Logic ---
  if (isLoading) {
    return <div className="p-8 text-center text-gray-500">Loading shipment details...</div>;
  }

  if (error) {
    return <div className="p-8 text-center text-red-600">Error: {error}</div>;
  }

  if (!shipment) {
    return <div className="p-8 text-center text-orange-600">Shipment not found.</div>;
  }

  return (
    <div className="min-h-screen bg-gray-100 p-4 sm:p-6 lg:p-8">
      <div className="container mx-auto max-w-4xl">
        <div className="mb-6">
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-800">Shipment Tracking</h1>
          <p className="text-sm text-gray-500 mt-1 font-mono">ID: {shipment.shipment_id}</p>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-lg">
          <h2 className="text-xl sm:text-2xl font-semibold mb-6">
            Status: <span className="font-bold text-indigo-600 capitalize">{shipment.status}</span>
          </h2>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 text-gray-700 border-t pt-6">
            <div>
              <p className="text-sm font-medium text-gray-500">Current ETA</p>
              <p className="text-lg font-semibold">{new Date(shipment.current_eta).toLocaleString()}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">Vehicle Type</p>
              <p className="text-lg">{shipment.vehicles?.vehicle_type || 'N/A'}</p>
            </div>
             <div>
              <p className="text-sm font-medium text-gray-500">Order ID</p>
              <p className="text-lg font-mono">{shipment.orders?.order_id || 'N/A'}</p>
            </div>
          </div>

          {/* Render the Realtime Telemetry Component, passing the necessary props */}
          {shipment.vehicles?.vehicle_id ? (
            <RealtimeTelemetry 
              vehicleId={shipment.vehicles.vehicle_id}
              vehicleType={shipment.vehicles.vehicle_type}
            />
          ) : (
            <div className="mt-8 border-t pt-6">
              <h3 className="text-lg font-semibold">Live Vehicle Location</h3>
              <p className="mt-2 text-gray-500">No vehicle is currently assigned to this shipment.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}