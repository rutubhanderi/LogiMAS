import { supabase } from '../../../../lib/supabaseClient';
import { notFound } from "next/navigation";

// This line is crucial for pages with dynamic data
export const dynamic = 'force-dynamic';

// Define a more precise type for our data
type ShipmentPageData = {
  shipment_id: string;
  status: string;
  current_eta: string;
  expected_arrival: string;
  orders: {
    order_id: string;
    destination: { lat: number; lon: number; address: string };
    items: { sku: string; name: string; price: number }[];
  } | null;
  vehicles: {
    vehicle_type: string;
  } | null;
};

// Helper function to fetch data directly on the server
async function getShipmentData(shipment_id: string): Promise<ShipmentPageData | null> {
  const { data, error } = await supabase
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
    .single();

  if (error || !data) {
    console.error("Error fetching shipment:", error?.message);
    return null;
  }
  
  return data as ShipmentPageData;
}

// The main page component is now an async Server Component
export default async function TrackShipmentPage({ params }: { params: { shipment_id: string } }) {
  const { shipment_id } = params;
  const shipment = await getShipmentData(shipment_id);

  // If no data, show a 404 page
  if (!shipment) {
    notFound();
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
              <p className="text-sm font-medium text-gray-500">Original Expected Arrival</p>
              <p className="text-lg">{new Date(shipment.expected_arrival).toLocaleString()}</p>
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

          <div className="mt-8">
            <h3 className="text-lg font-semibold border-t pt-6">Items in Shipment</h3>
            {shipment.orders && shipment.orders.items.length > 0 ? (
               <ul className="mt-4 space-y-2">
                 {shipment.orders.items.map((item, index) => (
                   <li key={index} className="flex justify-between p-3 bg-gray-50 rounded-md">
                     <span>{item.name}</span>
                     <span className="text-gray-500 font-mono text-sm">SKU: {item.sku}</span>
                   </li>
                 ))}
               </ul>
            ) : (
               <p className="mt-2 text-gray-500">No items found.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}