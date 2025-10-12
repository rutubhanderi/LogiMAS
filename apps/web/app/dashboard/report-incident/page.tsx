'use client';

import { useState, FormEvent } from 'react';
// Assuming you have an apiClient set up in this path
import apiClient from '../../../lib/apiClient'; 

export default function ReportIncidentPage() {
  const [routeDescription, setRouteDescription] = useState('');
  const [details, setDetails] = useState('');
  const [shipmentId, setShipmentId] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!routeDescription.trim() || !details.trim()) {
      setError("Route Description and Details are required.");
      return;
    }

    setIsLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const payload = {
        route_description: routeDescription,
        details: details,
        shipment_id: shipmentId.trim() || undefined,
      };

      const response = await apiClient.post('/incidents', payload);

      setSuccess(response.data.message);
      // Clear the form on success
      setRouteDescription('');
      setDetails('');
      setShipmentId('');
    } catch (err: any) {
      setError(err.response?.data?.detail || "An unexpected error occurred.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-4xl font-bold text-slate-900">Report an Incident</h1>
        <p className="text-lg text-slate-600 mt-1">
          Submit a report for traffic, weather, or other incidents affecting a route.
        </p>
      </div>

      <div className="bg-white p-8 rounded-xl shadow-lg max-w-2xl">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="route" className="block text-base font-semibold text-slate-800">
              Route Description
            </label>
            <input
              id="route"
              type="text"
              value={routeDescription}
              onChange={(e) => setRouteDescription(e.target.value)}
              placeholder="e.g., I-5 Northbound near Exit 112"
              className="mt-2 w-full p-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-slate-800"
              required
            />
          </div>

          <div>
            <label htmlFor="shipment_id" className="block text-base font-semibold text-slate-800">
              Associated Shipment ID (Optional)
            </label>
            <input
              id="shipment_id"
              type="text"
              value={shipmentId}
              onChange={(e) => setShipmentId(e.target.value)}
              placeholder="Paste Shipment ID if applicable..."
              className="mt-2 w-full p-3 border border-slate-300 rounded-lg font-mono focus:outline-none focus:ring-2 focus:ring-blue-500 text-slate-800"
            />
          </div>
          
          <div>
            <label htmlFor="details" className="block text-base font-semibold text-slate-800">
              Incident Details
            </label>
            <textarea
              id="details"
              value={details}
              onChange={(e) => setDetails(e.target.value)}
              placeholder="Describe what is happening..."
              rows={5}
              className="mt-2 w-full p-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-slate-800"
              required
            />
          </div>

          <button
            type="submit"
            className="w-full px-6 py-4 bg-blue-600 text-white font-bold text-lg rounded-lg hover:bg-blue-700 transition-colors disabled:bg-slate-400"
            disabled={isLoading}
          >
            {isLoading ? 'Submitting...' : 'Submit Report'}
          </button>
        </form>

        {success && <div className="mt-4 text-center p-3 bg-green-100 text-green-800 rounded-lg">{success}</div>}
        {error && <div className="mt-4 text-center p-3 bg-red-100 text-red-800 rounded-lg">{error}</div>}
      </div>
    </div>
  );
}