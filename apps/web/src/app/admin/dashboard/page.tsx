'use client';

import { useEffect, useState } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import { supabase } from '@/lib/supabase/client'; // Assuming you have this configured

const adminMenuItems = [
    { name: 'Dashboard', href: '/admin/dashboard', icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" /></svg> },
    { name: 'Dispatch Orders', href: '/admin/dispatch', icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" /></svg> },
    { name: 'Chat', href: '/admin/chat', icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" /></svg> },
    { name: 'Tracking', href: '/admin/tracking', icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" /></svg> },
    { name: 'Knowledge Base', href: '/admin/knowledge-base', icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" /></svg> },
    //{ name: 'Analysis', href: '/admin/analysis', icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg> },
    { name: 'Users', href: '/admin/users', icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" /></svg> },
    { name: 'Warehouses', href: '/admin/warehouses', icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" /></svg> },
    { name: 'Vehicles', href: '/admin/vehicles', icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg> },
];

export default function AdminDashboard() {
  const [stats, setStats] = useState<any>({});
  const [loading, setLoading] = useState(true);
  const [realtimeEnabled, setRealtimeEnabled] = useState(false);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const token = localStorage.getItem('logimas_token');
        if (!token) throw new Error("Authentication token not found.");

        const [
          { count: totalOrders },
          { count: activeDeliveries },
          { count: totalUsers },
          analyticsRes,
        ] = await Promise.all([
          supabase.from('orders').select('*', { count: 'exact', head: true }),
          supabase.from('shipments').select('*', { count: 'exact', head: true }).in('status', ['in-transit', 'processing']),
          supabase.from('customers').select('*', { count: 'exact', head: true }),
          fetch("http://localhost:8000/api/v1/analytics/summary", { headers: { 'Authorization': `Bearer ${token}` } }),
        ]);

        if (!analyticsRes.ok) throw new Error("Failed to fetch analytics data.");
        const analyticsData = await analyticsRes.json();
        
        setStats({
          totalOrders,
          activeDeliveries,
          totalUsers,
          revenue: analyticsData.total_revenue || 0,
          statusDistribution: analyticsData.delivery_status_distribution || {},
          // --- THE FIX ---
          // The backend sends `popular_routes` as an array directly.
          // We no longer need to look for a nested `routes` property.
          popularRoutes: analyticsData.popular_routes || [],
        });
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();

    // ... (realtime subscription is unchanged)
    const subscription = supabase.channel('dashboard-updates').on('postgres_changes', { event: '*', schema: 'public' }, () => { fetchDashboardData(); }).subscribe();
    setRealtimeEnabled(true);
    return () => { subscription.unsubscribe(); };
  }, []);

  // --- (The rest of the component is unchanged) ---
  const StatCard = ({ title, value, icon, trend, color }) => {
    const colors = { blue: 'from-blue-500 to-blue-600', green: 'from-green-500 to-green-600', purple: 'from-purple-500 to-purple-600', orange: 'from-orange-500 to-orange-600' };
    return (
      <div className={`bg-gradient-to-br ${colors[color]} p-6 rounded-xl shadow-md text-white`}>
        <div className="flex justify-between items-start">
          <div><p className="text-sm opacity-90">{title}</p><p className="text-3xl font-bold mt-2">{value}</p></div>
          <div className="bg-white/20 p-2 rounded-lg">{icon}</div>
        </div>
        {trend && <p className="text-sm mt-2 opacity-75">{trend}</p>}
      </div>
    );
  };
  
  const StatusBar = ({ label, count, total, color }) => {
      const pct = total > 0 ? Math.round((count / total) * 100) : 0;
      return (
          <div>
              <div className="flex justify-between text-sm mb-1"><span className="text-gray-400 capitalize">{label.replace('_', ' ')}</span><span className="font-medium text-white">{pct}%</span></div>
              <div className="w-full bg-gray-700 rounded-full h-3"><div className={`${color} h-3 rounded-full`} style={{ width: `${pct}%` }}></div></div>
          </div>
      );
  }

  const totalStatuses = Object.values(stats.statusDistribution || {}).reduce((a: number, b: number) => a + b, 0);

  return (
    <DashboardLayout role="admin" menuItems={adminMenuItems}>
      <div>
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-white">Admin Dashboard</h1>
          <div className="text-sm text-gray-400">{realtimeEnabled ? 'Live updates enabled' : 'Connecting...'}</div>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">{[...Array(4)].map((_, i) => (<div key={i} className="bg-gray-700 p-6 rounded-xl h-32 animate-pulse" />))}</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <StatCard title="Total Orders" value={stats.totalOrders?.toLocaleString() || '0'} icon={<svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" /></svg>} color="blue" trend="↑ Increase from last period"/>
            <StatCard title="Active Deliveries" value={stats.activeDeliveries?.toLocaleString() || '0'} icon={<svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" /></svg>} color="green" trend="→ No change from last period"/>
            <StatCard title="Total Users" value={stats.totalUsers?.toLocaleString() || '0'} icon={<svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" /></svg>} color="purple" trend="↑ Increase from last period"/>
            <StatCard title="Revenue (30d)" value={`$${(stats.revenue || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`} icon={<svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>} color="orange" trend="↑ Increase from last period"/>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-gray-800 p-6 rounded-xl shadow-md">
            <h3 className="text-lg font-semibold text-white mb-4">Delivery Status Distribution (7d)</h3>
            {loading ? <p className="text-gray-400">Loading statuses…</p> : (
              <div className="space-y-4">
                {Object.keys(stats.statusDistribution || {}).length === 0 ? <p className="text-sm text-gray-500">No shipment data available.</p> : (
                  <>
                    <StatusBar label="Pending" count={stats.statusDistribution.pending || 0} total={totalStatuses} color="bg-yellow-500" />
                    <StatusBar label="In Transit" count={stats.statusDistribution['in-transit'] || 0} total={totalStatuses} color="bg-blue-500" />
                    <StatusBar label="Delivered" count={stats.statusDistribution.delivered || 0} total={totalStatuses} color="bg-green-500" />
                  </>
                )}
              </div>
            )}
          </div>
          
          <div className="bg-gray-800 p-6 rounded-xl shadow-md">
            <h3 className="text-lg font-semibold text-white mb-4">Popular Routes (30d)</h3>
            <div className="space-y-3">
              {loading ? <p className="text-gray-400">Loading routes…</p> : !stats.popularRoutes || stats.popularRoutes.length === 0 ? (
                <p className="text-sm text-gray-500">No popular routes data available.</p>
              ) : (
                stats.popularRoutes.map((route, i) => (
                  <div key={i} className="flex items-center justify-between p-3 bg-gray-700 rounded-lg">
                    <div><p className="font-medium text-white">{route.route}</p><p className="text-sm text-gray-400">{route.shipments ?? 0} shipments</p></div>
                    <svg className="w-5 h-5 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" /></svg>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}