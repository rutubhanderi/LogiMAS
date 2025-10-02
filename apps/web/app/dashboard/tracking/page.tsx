"use client";

import { useState, FormEvent } from "react";
import { RealtimeTelemetry } from "../../../components/ui/RealtimeTelemetry";

// Define the shape of the data we expect to receive from our FastAPI backend.
// Note that related tables (`orders`, `vehicles`) are correctly typed as arrays.
type ShipmentDetails = {
  shipment_id: string;
  status: string;
  current_eta: string;
  expected_arrival: string;
  orders: {
    order_id: string;
    items: { sku: string; name: string; price: number }[];
  }[]; // Array of orders
  vehicles: {
    vehicle_id: string;
    vehicle_type: string;
  }[]; // Array of vehicles
};

export default function TrackingDashboardPage() {
  const [shipmentIdInput, setShipmentIdInput] = useState("");
  const [shipmentDetails, setShipmentDetails] =
    useState<ShipmentDetails | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // This function is triggered when the user clicks the "Track" button.
  const handleSearch = async (e: FormEvent) => {
    e.preventDefault();
    if (!shipmentIdInput.trim()) {
      setError("Please enter a Shipment ID.");
      return;
    }

    // Reset the state for the new search
    setIsLoading(true);
    setError(null);
    setShipmentDetails(null);

    try {
      // **CRITICAL:** This now calls your single, authoritative FastAPI backend.
      const response = await fetch(
        `http://127.0.0.1:8000/shipments/${shipmentIdInput.trim()}`
      );

      if (!response.ok) {
        // If the backend returns an error (like 404), parse the error message.
        const errorData = await response.json();
        throw new Error(
          errorData.detail || `An error occurred: ${response.statusText}`
        );
      }

      const data: ShipmentDetails = await response.json();
      setShipmentDetails(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  // Helper variables to safely access the first item in the related data arrays.
  const vehicle = shipmentDetails?.vehicles?.[0];
  const order = shipmentDetails?.orders?.[0];

  return (
    <div className="h-full flex flex-col space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-800">Shipment Lookup</h1>
        <p className="text-gray-500 mt-1">
          Enter a shipment ID to view its live status and location.
        </p>
      </div>

      {/* Search Bar Section */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <form
          onSubmit={handleSearch}
          className="flex flex-col sm:flex-row gap-4"
        >
          <input
            type="text"
            value={shipmentIdInput}
            onChange={(e) => setShipmentIdInput(e.target.value)}
            placeholder="Paste Shipment ID here..."
            className="flex-grow p-3 border border-gray-300 rounded-md font-mono focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          />
          <button
            type="submit"
            className="px-6 py-3 bg-blue-600 text-white font-semibold rounded-md hover:bg-blue-700 transition-colors disabled:bg-gray-400"
            disabled={isLoading}
          >
            {isLoading ? "Searching..." : "Track Shipment"}
          </button>
        </form>
      </div>

      {/* Results Area - Renders conditionally */}
      <div className="flex-grow">
        {isLoading && (
          <div className="text-center p-8 text-gray-500">
            Loading shipment data...
          </div>
        )}

        {error && (
          <div
            className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 rounded-r-lg animate-fade-in"
            role="alert"
          >
            <p className="font-bold">Error</p>
            <p>{error}</p>
          </div>
        )}

        {shipmentDetails && (
          <div className="bg-white p-6 rounded-xl shadow-lg animate-fade-in">
            <h2 className="text-2xl font-semibold mb-6">Tracking Details</h2>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-gray-700 border-t pt-6 mb-6">
              <div>
                <p className="text-sm font-medium text-gray-500">Status</p>
                <p
                  className={`text-lg font-bold capitalize ${
                    shipmentDetails.status === "shipped"
                      ? "text-blue-600"
                      : shipmentDetails.status === "delivered"
                      ? "text-green-600"
                      : "text-yellow-600"
                  }`}
                >
                  {shipmentDetails.status}
                </p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-500">Current ETA</p>
                <p className="text-lg font-semibold">
                  {new Date(shipmentDetails.current_eta).toLocaleString()}
                </p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-500">Order ID</p>
                <p className="text-lg font-mono">{order?.order_id || "N/A"}</p>
              </div>
            </div>

            {/* The Live Map and Telemetry Component */}
            {vehicle?.vehicle_id ? (
              <RealtimeTelemetry
                vehicleId={vehicle.vehicle_id}
                vehicleType={vehicle.vehicle_type}
              />
            ) : (
              <div className="mt-8 border-t pt-6">
                <h3 className="text-lg font-semibold">Live Vehicle Location</h3>
                <p className="mt-2 text-gray-500">
                  No vehicle is currently assigned to this shipment.
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
