import { supabase } from "../../../lib/supabaseClient";

export const dynamic = 'force-dynamic';
export const revalidate = 60; // Re-fetch data at most once per minute

type KpiData = {
  ship_date: string;
  total_shipments: number;
  on_time_shipments: number;
  on_time_percentage: number;
};

async function getKpis(): Promise<KpiData[]> {
  const { data, error } = await supabase
    .from('daily_on_time_rate')
    .select('*')
    .order('ship_date', { ascending: false })
    .limit(30);
  
  if (error) {
    console.error("Failed to fetch KPI data:", error);
    return [];
  }
  return data;
}

export default async function DashboardPage() {
  const kpis = await getKpis();
  const overallRate = kpis.length > 0
    ? (kpis.reduce((acc, cur) => acc + cur.on_time_shipments, 0) / kpis.reduce((acc, cur) => acc + cur.total_shipments, 0) * 100).toFixed(2)
    : "0.00";

  return (
    <div className="min-h-screen bg-gray-100 p-4 sm:p-6 lg:p-8">
      <div className="container mx-auto max-w-7xl">
        <h1 className="text-3xl font-bold text-gray-800 mb-6">Admin Dashboard</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-sm font-medium text-gray-500">Overall On-Time Rate (Last 30 Days)</h2>
            <p className="text-3xl font-bold text-green-600 mt-2">{overallRate}%</p>
          </div>
          {/* Other KPI cards can go here */}
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Daily On-Time Delivery Performance</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total Shipments</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">On-Time</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">On-Time %</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {kpis.map((day) => (
                  <tr key={day.ship_date}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{new Date(day.ship_date).toLocaleDateString()}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{day.total_shipments}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{day.on_time_shipments}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-gray-900">{day.on_time_percentage}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}