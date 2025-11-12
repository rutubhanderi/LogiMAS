'use client';

import { useState, useEffect } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import Link from 'next/link';

// The menu items for the driver's sidebar
const deliveryMenuItems = [
    { name: 'Dashboard', href: '/delivery/dashboard', icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" /></svg> },
    { name: 'Chat', href: '/delivery/chat', icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" /></svg> },
    { name: 'Tracking', href: '/delivery/tracking', icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" /></svg> },
    { name: 'Report Incident', href: '/delivery/report-incident', icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg> },
    //{ name: 'My Deliveries', href: '/delivery/deliveries', icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" /></svg> },
];

export default function DeliveryDashboard() {
  const [allDeliveries, setAllDeliveries] = useState([]); // Master list from API
  const [filteredDeliveries, setFilteredDeliveries] = useState([]); // List to display
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [updatingId, setUpdatingId] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');

  // Fetch all assigned deliveries for the logged-in driver
  useEffect(() => {
    const fetchDeliveries = async () => {
      setLoading(true);
      setError('');
      try {
        const token = localStorage.getItem('logimas_token');
        if (!token) throw new Error('Authentication token not found. Please log in.');

        const response = await fetch('http://localhost:8000/api/v1/shipments/my-deliveries', {
          headers: { 'Authorization': `Bearer ${token}` },
        });

        if (response.status === 401) throw new Error('Your session has expired. Please log in again.');
        if (!response.ok) throw new Error('Failed to fetch deliveries.');
        
        const data = await response.json();
        setAllDeliveries(data);
        setFilteredDeliveries(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchDeliveries();
  }, []);

  // Filter deliveries based on the search term
   useEffect(() => {
    let results = [...allDeliveries];

    // 1. Apply status filter first
    if (statusFilter !== 'all') {
      if (statusFilter === 'pending') {
        // "Pending" is a logical group of all non-delivered statuses
        results = results.filter(delivery => delivery.status !== 'delivered');
      } else {
        results = results.filter(delivery => delivery.status === statusFilter);
      }
    }

    // 2. Apply search term filter on the result of the status filter
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      results = results.filter(delivery =>
          delivery.shipment_id.toLowerCase().includes(term) ||
          delivery.order.customer.name.toLowerCase().includes(term) ||
          delivery.order.destination.address.toLowerCase().includes(term) ||
          delivery.order.destination.city.toLowerCase().includes(term)
      );
    }
    
    setFilteredDeliveries(results);
  }, [searchTerm, statusFilter, allDeliveries]);

  // Handle the API call to mark a shipment as "delivered"
  const handleMarkAsDelivered = async (shipmentId) => {
    setUpdatingId(shipmentId);
    setError('');
    try {
        const token = localStorage.getItem('logimas_token');
        if (!token) throw new Error('Authentication token not found.');

        const response = await fetch(`http://localhost:8000/api/v1/shipments/${shipmentId}/status`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify({ status: 'delivered' }),
        });

        if (!response.ok) {
            const errorResult = await response.json();
            throw new Error(errorResult.detail || 'Failed to update status.');
        }

        // Optimistically update the UI for instant feedback
        const updateList = (list) => list.map(d => d.shipment_id === shipmentId ? { ...d, status: 'delivered' } : d);
        setAllDeliveries(updateList);
        setFilteredDeliveries(updateList);
        alert('Delivery marked as complete!');
    } catch (err) {
        setError(err.message);
    } finally {
        setUpdatingId(null);
    }
  };

  // Calculate KPI values from the master list of deliveries
  const totalCount = allDeliveries.length;
  const deliveredCount = allDeliveries.filter(d => d.status === 'delivered').length;
  const inTransitCount = allDeliveries.filter(d => d.status === 'in-transit').length;
  const pendingCount = totalCount - deliveredCount;

  return (
    <DashboardLayout role="delivery_guy" menuItems={deliveryMenuItems}>
      <div>
        <h1 className="text-3xl font-bold text-white mb-6">Delivery Dashboard</h1>
        
        {loading ? <p className="text-center text-gray-400">Loading dashboard...</p> : error ? <p className="text-center text-red-400 p-4 bg-red-900/20 rounded-lg">{error}</p> : (
          <>
            <div className="bg-gradient-to-r from-green-500 to-teal-600 rounded-xl shadow-lg p-8 mb-8 text-white">
              <h2 className="text-2xl font-bold mb-2">Ready for your next delivery?</h2>
              <p className="text-green-100">You have <span className="font-bold">{pendingCount}</span> active deliveries to complete.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <div className="bg-gray-800 p-6 rounded-xl"><p className="text-sm text-gray-400">Total Assigned</p><p className="text-2xl font-bold mt-1">{totalCount}</p></div>
              <div className="bg-gray-800 p-6 rounded-xl"><p className="text-sm text-gray-400">Pending</p><p className="text-2xl font-bold text-yellow-400 mt-1">{pendingCount}</p></div>
              <div className="bg-gray-800 p-6 rounded-xl"><p className="text-sm text-gray-400">In Transit</p><p className="text-2xl font-bold text-blue-400 mt-1">{inTransitCount}</p></div>
              <div className="bg-gray-800 p-6 rounded-xl"><p className="text-sm text-gray-400">Delivered</p><p className="text-2xl font-bold text-green-400 mt-1">{deliveredCount}</p></div>
            </div>
            
            <div className="bg-gray-800 rounded-xl shadow-md p-6">
              <div className="flex flex-col md:flex-row justify-between items-center mb-4 gap-4">
                  <h2 className="text-xl font-semibold text-white">My Deliveries</h2>
                  <input
                      type="text"
                      placeholder="Search by ID, customer, or address..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="w-full md:w-1/3 p-2 bg-gray-900 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-indigo-500"
                  />
              </div>
          <div className="flex space-x-2 mb-6 border-b border-gray-700 pb-4">
                <button onClick={() => setStatusFilter('all')} className={`px-4 py-2 text-sm rounded-lg ${statusFilter === 'all' ? 'bg-indigo-600 text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'}`}>All ({allDeliveries.length})</button>
                <button onClick={() => setStatusFilter('pending')} className={`px-4 py-2 text-sm rounded-lg ${statusFilter === 'pending' ? 'bg-indigo-600 text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'}`}>Pending ({pendingCount})</button>
                <button onClick={() => setStatusFilter('in-transit')} className={`px-4 py-2 text-sm rounded-lg ${statusFilter === 'in-transit' ? 'bg-indigo-600 text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'}`}>In Transit ({inTransitCount})</button>
                <button onClick={() => setStatusFilter('delivered')} className={`px-4 py-2 text-sm rounded-lg ${statusFilter === 'delivered' ? 'bg-indigo-600 text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'}`}>Delivered ({deliveredCount})</button>
              </div>
              {filteredDeliveries.length === 0 ? (
                <p className="text-center text-gray-500 py-8">
                  {allDeliveries.length > 0 ? "No deliveries match your search." : "You have no assigned deliveries."}
                </p>
              ) : (
                <div className="space-y-6">
                  {filteredDeliveries.map((delivery) => {
                    const totalItems = delivery.order.items.reduce((sum, item) => sum + item.qty, 0);
                    return (
                      <div key={delivery.shipment_id} className="bg-gray-900 rounded-lg shadow p-5 border border-gray-700">
                        <header className="flex justify-between items-start mb-4">
                          <div>
                            <p className="text-xs text-gray-400">Shipment ID</p>
                            <h3 className="font-semibold text-white font-mono">{delivery.shipment_id}</h3>
                          </div>
                          <span className={`px-3 py-1 rounded-full text-xs font-bold capitalize ${
                              delivery.status === 'delivered' ? 'bg-green-500/20 text-green-400' :
                              delivery.status === 'in-transit' ? 'bg-blue-500/20 text-blue-400' :
                              'bg-gray-500/20 text-gray-300'
                          }`}>{delivery.status.replace('-', ' ')}</span>
                        </header>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 border-t border-b border-gray-700 py-4">
                          <div>
                            <p className="text-xs text-gray-400 mb-1">Recipient</p>
                            <p className="font-medium text-white">{delivery.order.customer.name}</p>
                            {delivery.order.customer.phone && <p className="text-sm text-gray-500">{delivery.order.customer.phone}</p>}
                          </div>
                          <div>
                            <p className="text-xs text-gray-400 mb-1">Destination</p>
                            <p className="font-medium text-white">{delivery.order.destination.address}, {delivery.order.destination.city}</p>
                          </div>
                          <div>
                            <p className="text-xs text-gray-400 mb-1">Package</p>
                            <p className="font-medium text-white">{totalItems} Item{totalItems > 1 ? 's' : ''}</p>
                          </div>
                        </div>

                        <footer className="flex flex-col md:flex-row justify-between items-center pt-4">
                          <div>
                            <p className="text-xs text-gray-400">Estimated Time of Arrival</p>
                            <p className="font-medium text-white">{delivery.current_eta ? new Date(delivery.current_eta).toLocaleString() : 'Not available'}</p>
                          </div>
                          <div className="flex gap-3 mt-4 md:mt-0">
                            <Link href={`/delivery/tracking?id=${delivery.shipment_id}`} className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white font-medium rounded-lg text-sm">Track</Link>
                            {delivery.status !== 'delivered' && (
                              <button onClick={() => handleMarkAsDelivered(delivery.shipment_id)} disabled={updatingId === delivery.shipment_id} className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white font-medium rounded-lg text-sm disabled:bg-green-800">
                                {updatingId === delivery.shipment_id ? 'Updating...' : 'Mark Delivered'}
                              </button>
                            )}
                            <Link href={`/delivery/report-incident?shipmentId=${delivery.shipment_id}`} className="px-4 py-2 bg-red-900/40 hover:bg-red-900/60 text-red-400 font-medium rounded-lg text-sm">Report</Link>
                          </div>
                        </footer>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </DashboardLayout>
  );
}