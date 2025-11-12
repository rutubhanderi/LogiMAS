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
   // { name: 'Analysis', href: '/admin/analysis', icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg> },
    { name: 'Users', href: '/admin/users', icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" /></svg> },
    { name: 'Warehouses', href: '/admin/warehouses', icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" /></svg> },
    { name: 'Vehicles', href: '/admin/vehicles', icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg> },
];

const initialVehicleState = {
  vehicle_type: 'truck', plate_number: '', capacity_kg: 1000, fuel_type: 'diesel',
  driver_id: null, current_location: '', status: 'active'
};

const VehicleModal = ({ isOpen, onClose, onSubmit, vehicle, drivers }) => {
    // ... (This sub-component is unchanged)
    const [formData, setFormData] = useState(initialVehicleState);
    const isEditMode = vehicle && vehicle.vehicle_id;
    useEffect(() => { if (isOpen) { const initialData = isEditMode ? { ...vehicle, driver_id: vehicle.driver?.customer_id || null } : { ...initialVehicleState }; setFormData(initialData); } }, [vehicle, isOpen]);
    if (!isOpen) return null;
    const handleChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value });
    const handleSubmit = (e) => { e.preventDefault(); const payload = { ...formData, capacity_kg: parseFloat(formData.capacity_kg), driver_id: formData.driver_id === "" ? null : formData.driver_id }; onSubmit(payload); };
    return (
        <div className="fixed inset-0 bg-black bg-opacity-60 flex justify-center items-center z-50">
            <div className="bg-gray-800 p-8 rounded-xl shadow-lg w-full max-w-lg text-white">
                <h2 className="text-2xl font-bold mb-6">{isEditMode ? 'Edit Vehicle' : 'Add New Vehicle'}</h2>
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div><label className="block text-sm font-medium text-gray-400 mb-1">Plate Number</label><input name="plate_number" value={formData.plate_number} onChange={handleChange} required className="w-full p-2 bg-gray-700 rounded"/></div>
                    <div><label className="block text-sm font-medium text-gray-400 mb-1">Assign Driver</label><select name="driver_id" value={formData.driver_id || ''} onChange={handleChange} className="w-full p-2 bg-gray-700 rounded"><option value="">-- Unassigned --</option>{drivers.map(driver => (<option key={driver.customer_id} value={driver.customer_id}>{driver.name}</option>))}</select></div>
                    <div><label className="block text-sm font-medium text-gray-400 mb-1">Current Location</label><input name="current_location" value={formData.current_location} onChange={handleChange} className="w-full p-2 bg-gray-700 rounded"/></div>
                    <div><label className="block text-sm font-medium text-gray-400 mb-1">Capacity (kg)</label><input name="capacity_kg" type="number" value={formData.capacity_kg} onChange={handleChange} required className="w-full p-2 bg-gray-700 rounded"/></div>
                    <div><label className="block text-sm font-medium text-gray-400 mb-1">Vehicle Type</label><select name="vehicle_type" value={formData.vehicle_type} onChange={handleChange} className="w-full p-2 bg-gray-700 rounded"><option value="truck">Truck</option><option value="van">Van</option><option value="bike">Bike</option></select></div>
                    <div><label className="block text-sm font-medium text-gray-400 mb-1">Fuel Type</label><select name="fuel_type" value={formData.fuel_type} onChange={handleChange} className="w-full p-2 bg-gray-700 rounded"><option value="diesel">Diesel</option><option value="petrol">Petrol</option><option value="EV">EV</option><option value="CNG">CNG</option></select></div>
                    <div><label className="block text-sm font-medium text-gray-400 mb-1">Status</label><select name="status" value={formData.status} onChange={handleChange} className="w-full p-2 bg-gray-700 rounded"><option value="active">Active</option><option value="maintenance">Maintenance</option><option value="inactive">Inactive</option></select></div>
                    <div className="flex justify-end gap-4 pt-4"><button type="button" onClick={onClose} className="px-4 py-2 bg-gray-600 rounded-lg">Cancel</button><button type="submit" className="px-4 py-2 bg-indigo-600 text-white rounded-lg">{isEditMode ? 'Save Changes' : 'Add Vehicle'}</button></div>
                </form>
            </div>
        </div>
    );
};

export default function Vehicles() {
  const [allVehicles, setAllVehicles] = useState([]); // Master list from API
  const [filteredVehicles, setFilteredVehicles] = useState([]); // List to display
  const [drivers, setDrivers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingVehicle, setEditingVehicle] = useState(null);

  // --- NEW: State for search and filters ---
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [driverFilter, setDriverFilter] = useState('all');

  const fetchData = async () => {
    // ... (fetchData is unchanged)
    setLoading(true); setError('');
    const token = localStorage.getItem('logimas_token');
    if (!token) { setError("Authentication required."); setLoading(false); return; }
    try {
        const [vehiclesRes, driversRes] = await Promise.all([
            fetch('http://localhost:8000/api/v1/vehicles/', { headers: { 'Authorization': `Bearer ${token}` } }),
            fetch('http://localhost:8000/api/v1/admin/delivery-personnel', { headers: { 'Authorization': `Bearer ${token}` } })
        ]);
        if (!vehiclesRes.ok) throw new Error("Failed to fetch vehicles.");
        if (!driversRes.ok) throw new Error("Failed to fetch drivers.");
        const vehiclesData = await vehiclesRes.json();
        const driversData = await driversRes.json();
        setAllVehicles(vehiclesData);
        setDrivers(driversData);
    } catch (err) { setError(err.message); } finally { setLoading(false); }
  };
  
  useEffect(() => { fetchData(); }, []);

  // --- NEW: Combined filtering logic ---
  useEffect(() => {
    let results = [...allVehicles];

    // 1. Filter by status
    if (statusFilter !== 'all') {
      results = results.filter(v => v.status === statusFilter);
    }

    // 2. Filter by driver
    if (driverFilter !== 'all') {
      if (driverFilter === 'unassigned') {
        results = results.filter(v => !v.driver);
      } else {
        results = results.filter(v => v.driver?.customer_id === driverFilter);
      }
    }

    // 3. Filter by search term
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      results = results.filter(v =>
        v.plate_number.toLowerCase().includes(term) ||
        (v.driver?.name || '').toLowerCase().includes(term) ||
        (v.current_location || '').toLowerCase().includes(term)
      );
    }

    setFilteredVehicles(results);
  }, [searchTerm, statusFilter, driverFilter, allVehicles]);

  // --- (Modal control and API handlers are unchanged) ---
  const handleModalClose = () => { setIsModalOpen(false); setEditingVehicle(null); };
  const openAddModal = () => { setEditingVehicle(null); setIsModalOpen(true); };
  const openEditModal = (vehicle) => { setEditingVehicle(vehicle); setIsModalOpen(true); };
  const handleFormSubmit = async (formData) => { /* ... */ };
  const handleDelete = async (vehicleId) => {
    if (!window.confirm("Are you sure?")) return;
    const token = localStorage.getItem('logimas_token');
    if (!token) { setError("Authentication required."); return; }
    try {
        const response = await fetch(`http://localhost:8000/api/v1/vehicles/${vehicleId}`, { method: 'DELETE', headers: { 'Authorization': `Bearer ${token}` } });
        if (response.status !== 204) { throw new Error('Failed to delete vehicle.'); }
        alert("Vehicle deleted!");
        setAllVehicles(allVehicles.filter(v => v.vehicle_id !== vehicleId));
    } catch (err) { setError(err.message); }
  };

  const statusCounts = allVehicles.reduce((acc, v) => {
    acc[v.status] = (acc[v.status] || 0) + 1;
    return acc;
  }, {});

  return (
    <DashboardLayout role="admin" menuItems={adminMenuItems}>
      <div>
        <div className="flex justify-between items-center mb-6"><h1 className="text-3xl font-bold">Vehicle Management</h1><button onClick={openAddModal} className="px-4 py-2 bg-indigo-600 text-white font-medium rounded-lg">+ Add Vehicle</button></div>
        
        {/* --- NEW: Filter Controls Section --- */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <input type="text" placeholder="Search by Plate, Driver, Location..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="md:col-span-1 w-full p-2 bg-gray-800 border border-gray-700 rounded-lg"/>
            <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} className="w-full p-2 bg-gray-800 border border-gray-700 rounded-lg">
                <option value="all">All Statuses</option>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="maintenance">Maintenance</option>
                <option value="in-transit">In-Transit</option>
            </select>
            <select value={driverFilter} onChange={(e) => setDriverFilter(e.target.value)} className="w-full p-2 bg-gray-800 border border-gray-700 rounded-lg">
                <option value="all">All Drivers</option>
                <option value="unassigned">Unassigned</option>
                {drivers.map(driver => (<option key={driver.customer_id} value={driver.customer_id}>{driver.name}</option>))}
            </select>
        </div>

        {error && <p className="text-center text-red-500 font-semibold py-4">{error}</p>}
        {loading ? <p className="text-center">Loading...</p> : (
          <>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                <div className="bg-gray-800 p-6 rounded-xl"><p className="text-sm text-gray-400">Total Vehicles</p><p className="text-2xl font-bold mt-1">{allVehicles.length}</p></div>
                <div className="bg-gray-800 p-6 rounded-xl"><p className="text-sm text-gray-400">Active</p><p className="text-2xl font-bold text-green-400 mt-1">{statusCounts.active || 0}</p></div>
                <div className="bg-gray-800 p-6 rounded-xl"><p className="text-sm text-gray-400">In Maintenance</p><p className="text-2xl font-bold text-yellow-400 mt-1">{statusCounts.maintenance || 0}</p></div>
                <div className="bg-gray-800 p-6 rounded-xl"><p className="text-sm text-gray-400">On Delivery</p><p className="text-2xl font-bold text-blue-400 mt-1">{statusCounts['in-transit'] || 0}</p></div>
            </div>
            <div className="bg-gray-800 rounded-xl shadow-md overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-700">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs uppercase text-gray-300">Plate</th>
                    <th className="px-6 py-3 text-left text-xs uppercase text-gray-300">Type</th>
                    <th className="px-6 py-3 text-left text-xs uppercase text-gray-300">Driver</th>
                    <th className="px-6 py-3 text-left text-xs uppercase text-gray-300">Location</th>
                    <th className="px-6 py-3 text-left text-xs uppercase text-gray-300">Status</th>
                    <th className="px-6 py-3 text-left text-xs uppercase text-gray-300">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-700">
                  {filteredVehicles.length > 0 ? filteredVehicles.map((v) => (
                    <tr key={v.vehicle_id} className="hover:bg-gray-700">
                      <td className="px-6 py-4 whitespace-nowrap font-medium">{v.plate_number}</td>
                      <td className="px-6 py-4 whitespace-nowrap capitalize">{v.vehicle_type}</td>
                      <td className="px-6 py-4 whitespace-nowrap">{v.driver ? v.driver.name : <span className="text-gray-500">Unassigned</span>}</td>
                      <td className="px-6 py-4 whitespace-nowrap">{v.current_location}</td>
                      <td className="px-6 py-4 whitespace-nowrap"><span className={`px-2 py-1 text-xs font-semibold rounded-full capitalize ${v.status === 'active' ? 'bg-green-900 text-green-300' : v.status === 'maintenance' ? 'bg-yellow-900 text-yellow-300' : v.status === 'in-transit' ? 'bg-blue-900 text-blue-300' : 'bg-gray-700 text-gray-300'}`}>{v.status}</span></td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm"><button onClick={() => openEditModal(v)} className="text-indigo-400 hover:text-indigo-300 mr-4">Edit</button><button onClick={() => handleDelete(v.vehicle_id)} className="text-red-400 hover:text-red-300">Delete</button></td>
                    </tr>
                  )) : (
                    <tr><td colSpan="6" className="text-center py-8 text-gray-500">No vehicles match your filters.</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </>
        )}
      </div>
      <VehicleModal isOpen={isModalOpen} onClose={handleModalClose} onSubmit={handleFormSubmit} vehicle={editingVehicle} drivers={drivers} />
    </DashboardLayout>
  );
}