"use client";

import { useState, FormEvent } from "react";
import { RealtimeTelemetry } from "../../../components/ui/RealtimeTelemetry";

// The type definition is still useful
type ShipmentDetails = {
  shipment_id: string;
  status: string;
  current_eta: string;
  orders: { order_id: string; items: any[] }[]; // Corrected type
  vehicles: { vehicle_id: string; vehicle_type: string }[]; // Corrected type
};

export default function TrackingDashboardPage() {
  const [shipmentIdInput, setShipmentIdInput] = useState("");
  const [shipmentDetails, setShipmentDetails] =
    useState<ShipmentDetails | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (e: FormEvent) => {
    e.preventDefault();
    if (!shipmentIdInput.trim()) return;

    setIsLoading(true);
    setError(null);
    setShipmentDetails(null);

    try {
      // Call our FastAPI backend instead of Supabase directly
      const response = await fetch(
        `http://127.0.0.1:8000/shipments/${shipmentIdInput.trim()}`
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Shipment not found.`);
      }

      const data: ShipmentDetails = await response.json();
      setShipmentDetails(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const vehicle = shipmentDetails?.vehicles?.[0];

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-800 mb-6">Shipment Lookup</h1>
      <div className="bg-white p-6 rounded-lg shadow-md mb-8">
        <form onSubmit={handleSearch} className="flex gap-2">
          <input
            type="text"
            value={shipmentIdInput}
            onChange={(e) => setShipmentIdInput(e.target.value)}
            placeholder="Enter Shipment ID..."
            className="flex-grow p-3 border rounded-md font-mono"
            disabled={isLoading}
          />
          <button
            type="submit"
            className="px-6 py-3 bg-blue-600 text-white font-semibold rounded-md"
            disabled={isLoading}
          >
            {isLoading ? "Searching..." : "Track"}
          </button>
        </form>
      </div>
      {error && (
        <div className="bg-red-100 text-red-700 p-3 rounded-md">
          Error: {error}
        </div>
      )}
      {shipmentDetails && (
        <div className="bg-white p-6 rounded-xl shadow-lg">
          <h2 className="text-2xl font-semibold mb-6">
            Details for Shipment:{" "}
            <span className="font-mono text-gray-600 text-xl">
              {shipmentDetails.shipment_id}
            </span>
          </h2>
          {vehicle?.vehicle_id && (
            <RealtimeTelemetry
              vehicleId={vehicle.vehicle_id}
              vehicleType={vehicle.vehicle_type}
            />
          )}
        </div>
      )}
    </div>
  );
}
