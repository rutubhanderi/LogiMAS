"use client"; // This must become a client component to fetch data

import { useState, useEffect } from "react";

type KpiData = {
  ship_date: string;
  total_shipments: number;
  on_time_shipments: number;
  on_time_percentage: number;
};

export default function AnalysisPage() {
  const [kpis, setKpis] = useState<KpiData[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchKpis = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/admin/kpis");
        const data = await response.json();
        setKpis(data);
      } catch (error) {
        console.error("Failed to fetch KPIs", error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchKpis();
  }, []);

  if (isLoading) return <div>Loading KPI data...</div>;

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-800 mb-6">
        Performance Analysis
      </h1>
      {/* ... (The JSX for displaying the table is the same as before) ... */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4">
          Daily On-Time Delivery Performance
        </h2>
        <table className="min-w-full">
          {/* ... table head ... */}
          <tbody>
            {kpis.map((day) => (
              <tr key={day.ship_date}>
                {/* ... table cells ... */}
                <td className="px-6 py-4">
                  {new Date(day.ship_date).toLocaleDateString()}
                </td>
                <td className="px-6 py-4">{day.total_shipments}</td>
                <td className="px-6 py-4">{day.on_time_shipments}</td>
                <td className="px-6 py-4">{day.on_time_percentage}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
