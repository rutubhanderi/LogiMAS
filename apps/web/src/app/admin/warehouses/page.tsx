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

const initialWarehouseState = {
  name: '', region: '', capacity_sq_ft: 1000, utilization_pct: 0, status: 'active'
};

const WarehouseModal = ({ isOpen, onClose, onSubmit, warehouse }) => {
  const [formData, setFormData] = useState(initialWarehouseState);
  const isEditMode = warehouse && warehouse.warehouse_id;

  useEffect(() => {
    if (isOpen) {
        setFormData(isEditMode ? { ...warehouse } : { ...initialWarehouseState });
    }
  }, [warehouse, isOpen]);

  if (!isOpen) return null;

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const processedData = {
        ...formData,
        capacity_sq_ft: parseInt(formData.capacity_sq_ft, 10),
        utilization_pct: parseInt(formData.utilization_pct, 10),
    };
    onSubmit(processedData);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-60 flex justify-center items-center z-50">
      <div className="bg-gray-800 p-8 rounded-xl shadow-lg w-full max-w-lg text-white">
        <h2 className="text-2xl font-bold mb-6">{isEditMode ? 'Edit Warehouse' : 'Add New Warehouse'}</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-1">Name</label>
            <input name="name" value={formData.name} onChange={handleChange} placeholder="e.g., Mumbai Central Hub" required className="w-full p-2 border rounded bg-gray-700 border-gray-600"/>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-1">Region / City</label>
            <input name="region" value={formData.region} onChange={handleChange} placeholder="e.g., Mumbai" required className="w-full p-2 border rounded bg-gray-700 border-gray-600"/>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-1">Capacity (sq ft)</label>
            <input name="capacity_sq_ft" type="number" value={formData.capacity_sq_ft} onChange={handleChange} required className="w-full p-2 border rounded bg-gray-700 border-gray-600"/>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-1">Utilization (%)</label>
            <input name="utilization_pct" type="number" value={formData.utilization_pct} onChange={handleChange} required className="w-full p-2 border rounded bg-gray-700 border-gray-600"/>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-1">Status</label>
            <select name="status" value={formData.status} onChange={handleChange} className="w-full p-2 border rounded bg-gray-700 border-gray-600">
              <option value="active">Active</option>
              <option value="maintenance">Maintenance</option>
              <option value="inactive">Inactive</option>
            </select>
          </div>
          <div className="flex justify-end gap-4 pt-4">
            <button type="button" onClick={onClose} className="px-4 py-2 bg-gray-600 rounded-lg hover:bg-gray-500">Cancel</button>
            <button type="submit" className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">{isEditMode ? 'Save Changes' : 'Add Warehouse'}</button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default function Warehouses() {
    // ... (All existing state and functions are unchanged)
  const [warehouses, setWarehouses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingWarehouse, setEditingWarehouse] = useState(null);

  const fetchWarehouses = async () => {
    setLoading(true); setError('');
    try {
      const token = localStorage.getItem('logimas_token');
      if (!token) throw new Error("Authentication token not found.");
      const response = await fetch('http://localhost:8000/api/v1/warehouses/', { headers: { 'Authorization': `Bearer ${token}` } });
      if (!response.ok) throw new Error("Failed to fetch data.");
      const data = await response.json();
      setWarehouses(data);
    } catch (err) { setError(err.message); } finally { setLoading(false); }
  };

  useEffect(() => {
    fetchWarehouses();
  }, []);

  const handleModalClose = () => {
    setIsModalOpen(false);
    setEditingWarehouse(null);
  };

  const openAddModal = () => {
    setEditingWarehouse(null);
    setIsModalOpen(true);
  };

  const openEditModal = (warehouse) => {
    setEditingWarehouse(warehouse);
    setIsModalOpen(true);
  };

  const handleFormSubmit = async (formData) => {
    const token = localStorage.getItem('logimas_token');
    if (!token) { setError("Authentication required."); return; }

    const { lat, lon, ...payload } = formData; // Exclude lat/lon from the payload

    const isEditMode = editingWarehouse && editingWarehouse.warehouse_id;
    const url = isEditMode
      ? `http://localhost:8000/api/v1/warehouses/${editingWarehouse.warehouse_id}`
      : 'http://localhost:8000/api/v1/warehouses/';
    const method = isEditMode ? 'PATCH' : 'POST';

    try {
      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || 'Failed to save warehouse.');
      }
      
      alert(`Warehouse successfully ${isEditMode ? 'updated' : 'added'}!`);
      handleModalClose();
      fetchWarehouses();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDelete = async (warehouseId) => {
    if (!window.confirm("Are you sure you want to delete this warehouse?")) return;
    
    const token = localStorage.getItem('logimas_token');
    if (!token) { setError("Authentication required."); return; }

    try {
      const response = await fetch(`http://localhost:8000/api/v1/warehouses/${warehouseId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` },
      });

      if (response.status !== 204) {
        const errData = await response.json();
        throw new Error(errData.detail || 'Failed to delete warehouse.');
      }
      
      alert("Warehouse deleted successfully!");
      setWarehouses(warehouses.filter(wh => wh.warehouse_id !== warehouseId));
    } catch (err) {
      setError(err.message);
    }
  };

  const totalWarehouses = warehouses.length;
  const activeWarehouses = warehouses.filter(wh => wh.status === 'active').length;
  const totalCapacity = warehouses.reduce((sum, wh) => sum + Number(wh.capacity_sq_ft || 0), 0);
  const avgUtilization = totalWarehouses > 0 ? warehouses.reduce((sum, wh) => sum + Number(wh.utilization_pct || 0), 0) / totalWarehouses : 0;
    
  return (
    <DashboardLayout role="admin" menuItems={adminMenuItems}>
      <div>
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Warehouse Management</h1>
          <button onClick={openAddModal} className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg">+ Add Warehouse</button>
        </div>

        {error && <p className="text-center text-red-500 font-semibold py-4">{error}</p>}
        
        {loading ? <p className="text-center">Loading warehouse data...</p> : (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-md"><p className="text-sm text-gray-600 dark:text-gray-400">Total Warehouses</p><p className="text-2xl font-bold mt-1">{totalWarehouses}</p></div>
              <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-md"><p className="text-sm text-gray-600 dark:text-gray-400">Active</p><p className="text-2xl font-bold text-green-500 mt-1">{activeWarehouses}</p></div>
              <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-md"><p className="text-sm text-gray-600 dark:text-gray-400">Total Capacity</p><p className="text-2xl font-bold mt-1">{(totalCapacity / 1000).toFixed(1)}K sq ft</p></div>
              <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-md"><p className="text-sm text-gray-600 dark:text-gray-400">Avg Utilization</p><p className="text-2xl font-bold text-blue-500 mt-1">{avgUtilization.toFixed(0)}%</p></div>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 dark:bg-gray-700">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium uppercase">Name</th>
                    <th className="px-6 py-3 text-left text-xs font-medium uppercase">Location</th>
                    <th className="px-6 py-3 text-left text-xs font-medium uppercase">Capacity</th>
                    <th className="px-6 py-3 text-left text-xs font-medium uppercase">Utilization</th>
                    <th className="px-6 py-3 text-left text-xs font-medium uppercase">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                  {warehouses.map((wh) => (
                    <tr key={wh.warehouse_id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                      <td className="px-6 py-4 whitespace-nowrap font-medium">{wh.name}</td>
                      <td className="px-6 py-4 whitespace-nowrap">{wh.region}</td>
                      <td className="px-6 py-4 whitespace-nowrap">{Number(wh.capacity_sq_ft).toLocaleString()} sq ft</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center gap-2">
                          <div className="flex-1 bg-gray-200 rounded-full h-2 w-20"><div className="bg-indigo-600 h-2 rounded-full" style={{ width: `${wh.utilization_pct}%` }}></div></div>
                          <span>{wh.utilization_pct}%</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs font-semibold rounded-full capitalize ${wh.status === 'active' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-400' : wh.status === 'maintenance' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-400' : 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-400'}`}>
                          {wh.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <button onClick={() => openEditModal(wh)} className="text-indigo-600 hover:text-indigo-900 mr-3 dark:text-indigo-400">Edit</button>
                        <button onClick={() => handleDelete(wh.warehouse_id)} className="text-red-600 hover:text-red-900 dark:text-red-400">Delete</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}
      </div>

      <WarehouseModal 
        isOpen={isModalOpen} 
        onClose={handleModalClose}
        onSubmit={handleFormSubmit}
        warehouse={editingWarehouse}
      />
    </DashboardLayout>
  );
}