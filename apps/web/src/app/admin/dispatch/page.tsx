'use client';

import { useState, useEffect } from 'react';
import DashboardLayout from '@/components/DashboardLayout';

const adminMenuItems = [
    { name: 'Dashboard', href: '/admin/dashboard', icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" /></svg> },
    { name: 'Dispatch Orders', href: '/admin/dispatch', icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" /></svg> },
    {
    name: "Chat",
    href: "/admin/chat",
    icon: (
      <svg
        className="w-5 h-5"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
        />
      </svg>
    ),
  },
    { name: 'Tracking', href: '/admin/tracking', icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" /></svg> },
    { name: 'Knowledge Base', href: '/admin/knowledge-base', icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" /></svg> },
    //{ name: 'Analysis', href: '/admin/analysis', icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg> },
    { name: 'Users', href: '/admin/users', icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" /></svg> },
    { name: 'Warehouses', href: '/admin/warehouses', icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" /></svg> },
    { name: 'Vehicles', href: '/admin/vehicles', icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg> },
];

export default function DispatchOrders() {
  const [allOrders, setAllOrders] = useState([]); // Store all fetched orders
  const [filteredOrders, setFilteredOrders] = useState([]); // Store orders to be displayed
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [dispatchingId, setDispatchingId] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  // Fetch pending orders when the component mounts
  useEffect(() => {
    const fetchPendingOrders = async () => {
      setLoading(true);
      setError('');
      try {
        const token = localStorage.getItem('logimas_token');
        if (!token) throw new Error('Authentication token not found. Please log in.');
        
        const response = await fetch('http://localhost:8000/api/v1/orders/?status=pending', {
          headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.status === 401) throw new Error('Your session has expired. Please log in again.');
        if (!response.ok) throw new Error('Failed to fetch pending orders.');

        const data = await response.json();
        setAllOrders(data);
        setFilteredOrders(data); // Initially, show all orders
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchPendingOrders();
  }, []);

  // Handle filtering when search term changes
  useEffect(() => {
    const results = allOrders.filter(order =>
      order.order_id.toLowerCase().includes(searchTerm.toLowerCase())
    );
    setFilteredOrders(results);
  }, [searchTerm, allOrders]);

  const handleDispatch = async (orderId) => {
    // ... (This function is unchanged)
    setDispatchingId(orderId); setError('');
    try {
      const token = localStorage.getItem('logimas_token');
      if (!token) throw new Error('Authentication token not found.');
      const response = await fetch('http://localhost:8000/api/v1/shipments/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ order_id: orderId }),
      });
      if (!response.ok) { const errorResult = await response.json(); throw new Error(errorResult.detail || 'Failed to create shipment.'); }
      const shipmentResult = await response.json();
      alert(`Shipment created successfully! Shipment ID: ${shipmentResult.shipment_id}`);
      setAllOrders(prev => prev.filter(order => order.order_id !== orderId));
    } catch (err) { setError(err.message); } finally { setDispatchingId(null); }
  };

  // --- NEW: Dynamic KPI card calculations ---
  const totalPendingValue = allOrders.reduce((sum, order) => sum + order.order_total, 0);
  const oldestOrderDate = allOrders.length > 0
    ? new Date(Math.min(...allOrders.map(order => new Date(order.order_date)))).toLocaleDateString()
    : 'N/A';

  const renderContent = () => {
    if (loading) return <p className="text-center">Loading pending orders...</p>;
    if (error) return <p className="text-center text-red-500 font-semibold">{error}</p>;
    if (allOrders.length === 0) return <p className="text-center text-gray-500">No pending orders to dispatch.</p>;

    return (
      <div className="space-y-4">
        {filteredOrders.length > 0 ? (
          filteredOrders.map(order => (
            <div key={order.order_id} className="bg-gray-800 p-4 rounded-lg shadow flex justify-between items-center">
              <div>
                <p className="font-bold text-lg">{order.destination.city}, {order.destination.postal_code}</p>
                <p className="text-sm text-gray-400 font-mono">{order.order_id}</p>
                <p className="text-sm">Total: <span className="font-semibold text-green-400">${order.order_total.toFixed(2)}</span></p>
              </div>
              <button
                onClick={() => handleDispatch(order.order_id)}
                disabled={dispatchingId === order.order_id}
                className="px-4 py-2 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:bg-blue-400 disabled:cursor-not-allowed"
              >
                {dispatchingId === order.order_id ? 'Dispatching...' : 'Dispatch'}
              </button>
            </div>
          ))
        ) : (
          <p className="text-center text-gray-500">No orders found with that ID.</p>
        )}
      </div>
    );
  };

  return (
    <DashboardLayout role="admin" menuItems={adminMenuItems}>
      <div>
        <h1 className="text-3xl font-bold text-white mb-6">Dispatch Pending Orders</h1>

        {/* --- NEW: KPI Cards --- */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            <div className="bg-gray-800 p-6 rounded-xl shadow-md">
                <p className="text-sm text-gray-400">Pending Orders</p>
                <p className="text-2xl font-bold text-white mt-1">{allOrders.length}</p>
            </div>
            <div className="bg-gray-800 p-6 rounded-xl shadow-md">
                <p className="text-sm text-gray-400">Total Pending Value</p>
                <p className="text-2xl font-bold text-green-400 mt-1">${totalPendingValue.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</p>
            </div>
            <div className="bg-gray-800 p-6 rounded-xl shadow-md">
                <p className="text-sm text-gray-400">Oldest Pending Order</p>
                <p className="text-2xl font-bold text-yellow-400 mt-1">{oldestOrderDate}</p>
            </div>
        </div>

        {/* --- NEW: Search Bar --- */}
        <div className="mb-6">
            <input
                type="text"
                placeholder="Filter by Order ID..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full p-3 bg-gray-800 border-2 border-gray-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
            />
        </div>
        
        {renderContent()}
      </div>
    </DashboardLayout>
  );
}