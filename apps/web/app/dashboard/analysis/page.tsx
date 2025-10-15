"use client";

import { useState, useEffect } from "react";
import { DailyPerformanceChart } from "../../../components/charts/DailyPerformanceChart";
// We will use a standard fetch call for simplicity in debugging
// import apiClient from '@/lib/apiClient';

type KpiData = {
  ship_date: string;
  total_shipments: number;
  on_time_shipments: number;
  on_time_percentage: number;
};

export default function AnalysisPage() {
  const [kpis, setKpis] = useState<KpiData[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchKpis() {
      setIsLoading(true);
      setError(null);
      try {
        const response = await fetch("http://127.0.0.1:8000/admin/kpis");

        if (!response.ok) {
          // If the server returns an error, try to get the detailed message
          const errorData = await response.json();
          throw new Error(
            errorData.detail || `Request failed with status ${response.status}`
          );
        }

        const data: KpiData[] = await response.json();
        setKpis(data);
      } catch (err: any) {
        console.error("Error fetching KPI data:", err);
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    }
    fetchKpis();
  }, []); // Empty dependency array means this runs once when the page loads

  const totalShipments = kpis.reduce(
    (acc, cur) => acc + cur.total_shipments,
    0
  );

  // --- RENDER LOGIC ---

  if (isLoading) {
    return (
      <div className="text-center p-10">
        <h1 className="text-xl font-semibold text-gray-500">
          Loading Analytics Data...
        </h1>
      </div>
    );
  }

  if (error) {
    return (
      <div
        className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 rounded-r-lg"
        role="alert"
      >
        <p className="font-bold">Could not load Analysis Page</p>
        <p>There was an error communicating with the backend.</p>
        <p className="mt-2 text-sm font-mono bg-red-200 p-2 rounded">
          <strong>Details:</strong> {error}
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold text-gray-800">Performance Analysis</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-sm font-medium text-gray-500">
            Total Shipments (Last 30d)
          </h2>
          <p className="text-3xl font-bold text-gray-800 mt-2">
            {totalShipments}
          </p>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-semibold mb-4 text-gray-700">
          Daily On-Time Performance (%)
        </h2>
        {kpis.length > 0 ? (
          <DailyPerformanceChart data={kpis} />
        ) : (
          <p className="text-gray-500">
            No performance data available to display.
          </p>
        )}
      </div>

      <div className="bg-white p-6 rounded-lg shadow-md">
        {/* CHANGE: Added 'text-gray-800' to make this header visible */}
        <h2 className="text-xl font-semibold mb-4 text-gray-800">
          Daily On-Time Delivery Data
        </h2>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Total Shipments
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  On-Time
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  On-Time %
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {kpis.length > 0 ? (
                kpis.map((day) => (
                  <tr key={day.ship_date}>
                    {/* CHANGE: Added 'text-gray-900' to ensure table data is visible */}
                    <td className="px-6 py-4 text-gray-900">
                      {new Date(day.ship_date).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 text-gray-900">{day.total_shipments}</td>
                    <td className="px-6 py-4 text-gray-900">{day.on_time_shipments}</td>
                    <td className="px-6 py-4 text-gray-900">{day.on_time_percentage}%</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={4} className="text-center py-4 text-gray-500">
                    No data to display.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}