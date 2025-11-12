'use client';

import { useState, useEffect } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import Link from 'next/link';

const deliveryMenuItems = [
    { name: 'Dashboard', href: '/delivery/dashboard', icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" /></svg> },
    { name: 'Chat', href: '/delivery/chat', icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" /></svg> },
    { name: 'Tracking', href: '/delivery/tracking', icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" /></svg> },
    { name: 'Report Incident', href: '/delivery/report-incident', icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg> },
    { name: 'My Deliveries', href: '/delivery/deliveries', icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" /></svg> },
];

export default function MyDeliveries() {
  const [deliveries, setDeliveries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [updatingId, setUpdatingId] = useState(null); // Tracks which delivery is being updated

  useEffect(() => {
    // ... (This data fetching logic is unchanged)
    const fetchDeliveries = async () => {
      setLoading(true); setError('');
      try {
        const token = localStorage.getItem('logimas_token');
        if (!token) throw new Error('Authentication token not found.');
        const response = await fetch('http://localhost:8000/api/v1/shipments/my-deliveries', { headers: { 'Authorization': `Bearer ${token}` } });
        if (!response.ok) throw new Error('Failed to fetch deliveries.');
        const data = await response.json();
        setDeliveries(data);
      } catch (err) { setError(err.message); } finally { setLoading(false); }
    };
    fetchDeliveries();
  }, []);

  // --- NEW: Function to handle marking a delivery as complete ---
  const handleMarkAsDelivered = async (shipmentId) => {
    setUpdatingId(shipmentId);
    setError('');
    try {
        const token = localStorage.getItem('logimas_token');
        if (!token) throw new Error('Authentication token not found.');

        const response = await fetch(`http://localhost:8000/api/v1/shipments/${shipmentId}/status`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ status: 'delivered' }),
        });

        if (!response.ok) {
            const errorResult = await response.json();
            throw new Error(errorResult.detail || 'Failed to update status.');
        }

        // Update the UI instantly for a better user experience
        setDeliveries(prevDeliveries => 
            prevDeliveries.map(d => 
                d.shipment_id === shipmentId ? { ...d, status: 'delivered' } : d
            )
        );
        alert('Delivery marked as complete!');

    } catch (err) {
        setError(err.message);
    } finally {
        setUpdatingId(null);
    }
  };

  const renderContent = () => {
    if (loading) return <p className="text-center text-gray-400">Loading your deliveries...</p>;
    if (error) return <p className="text-center text-red-400">{error}</p>;
    if (deliveries.length === 0) return <p className="text-center text-gray-500">You have no assigned deliveries.</p>;

    return (
      <div className="space-y-4">
        {deliveries.map((delivery) => (
          <div key={delivery.shipment_id} className="bg-gray-800 rounded-xl shadow-md p-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-lg font-semibold text-white font-mono">{delivery.shipment_id.substring(0, 8)}...</h3>
                <p className="text-sm text-gray-400">To: {delivery.order.customer.name}</p>
              </div>
              <span className={`px-3 py-1 rounded-full text-xs font-medium capitalize ${
                  delivery.status === 'delivered' ? 'bg-green-900/50 text-green-300' :
                  delivery.status === 'in-transit' ? 'bg-blue-900/50 text-blue-300' :
                  'bg-gray-700 text-gray-400'
              }`}>
                {delivery.status.replace('-', ' ')}
              </span>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <p className="text-sm text-gray-400">Delivery Address</p>
                <p className="font-medium text-white">{delivery.order.destination.address}, {delivery.order.destination.city}</p>
              </div>
              <div>
                <p className="text-sm text-gray-400">ETA</p>
                <p className="font-medium text-white">
                  {delivery.current_eta ? new Date(delivery.current_eta).toLocaleString() : 'Not available'}
                </p>
              </div>
            </div>
            <div className="flex gap-3">
              <Link href={`/delivery/tracking?id=${delivery.shipment_id}`} className="px-4 py-2 bg-green-900/30 hover:bg-green-900/50 text-green-400 font-medium rounded-lg text-sm">Track</Link>
              
              {/* --- MODIFIED: The button is now functional --- */}
              {delivery.status !== 'delivered' && (
                <button 
                    onClick={() => handleMarkAsDelivered(delivery.shipment_id)}
                    disabled={updatingId === delivery.shipment_id}
                    className="px-4 py-2 bg-blue-900/30 hover:bg-blue-900/50 text-blue-400 font-medium rounded-lg text-sm disabled:bg-gray-600 disabled:cursor-not-allowed"
                >
                    {updatingId === delivery.shipment_id ? 'Updating...' : 'Mark as Delivered'}
                </button>
              )}

              <Link href={`/delivery/report-incident?shipmentId=${delivery.shipment_id}`} className="px-4 py-2 bg-red-900/30 hover:bg-red-900/50 text-red-400 font-medium rounded-lg text-sm">Report Issue</Link>
            </div>
          </div>
        ))}
      </div>
    );
  };

  return (
    <DashboardLayout role="delivery_guy" menuItems={deliveryMenuItems}>
      <div>
        <h1 className="text-3xl font-bold text-white mb-6">My Deliveries</h1>
        {renderContent()}
      </div>
    </DashboardLayout>
  );
}