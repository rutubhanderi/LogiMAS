'use client';

import { useState, useEffect } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import AddUserModal from '@/components/AddUserModal';
import EditUserModal from '@/components/EditUserModal';

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

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1/admin';

export default function Users() {
  const [allUsers, setAllUsers] = useState<any[]>([]); // Master list from API
  const [filteredUsers, setFilteredUsers] = useState<any[]>([]); // List to display
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [editingUser, setEditingUser] = useState<any | null>(null);

  // --- NEW: State for search and filter ---
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState('all');

  // This function fetches users, now with role filtering
  const fetchUsers = async (role = 'all') => {
    setIsLoading(true);
    const token = localStorage.getItem('logimas_token');
    
    if (!token) {
      setError("Authentication token not found. Please log in.");
      setIsLoading(false);
      return;
    }
    
    // Build the URL with the role filter if it's not 'all'
    let url = `${API_URL}/users`;
    if (role !== 'all') {
      url += `?role=${role}`;
    }

    try {
      const response = await fetch(url, {
        headers: { 'Authorization': `Bearer ${token}` },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch users.');
      }

      const data = await response.json();
      setAllUsers(data.users || []); // Update the master list
      setError(null);
    } catch (err: any) {
      setError(err.message);
      setAllUsers([]); // Clear users on error
    } finally {
      setIsLoading(false);
    }
  };

  // --- MODIFIED: This hook now re-fetches data when the roleFilter changes ---
  useEffect(() => {
    fetchUsers(roleFilter);
  }, [roleFilter]);

  // --- NEW: This hook handles client-side searching whenever the master list or search term changes ---
  useEffect(() => {
    const results = allUsers.filter(user =>
      (user.name?.toLowerCase() || '').includes(searchTerm.toLowerCase()) ||
      (user.email?.toLowerCase() || '').includes(searchTerm.toLowerCase())
    );
    setFilteredUsers(results);
  }, [searchTerm, allUsers]);


  const handleDeleteUser = async (userId: string) => {
    // ... (This function is unchanged)
    if (!confirm('Are you sure you want to deactivate this user?')) return;
    const token = localStorage.getItem('logimas_token');
    try {
      const response = await fetch(`${API_URL}/users/${userId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (!response.ok) { const errorData = await response.json(); throw new Error(errorData.detail || 'Failed to deactivate user.'); }
      // Optimistically update the UI for instant feedback
      setAllUsers(prev => prev.filter(user => user.customer_id !== userId));
      alert('User deactivated successfully.');
    } catch (err: any) { alert(`Error: ${err.message}`); }
  };

  const handleDataUpdate = () => {
    fetchUsers(roleFilter); // Re-fetch with the current filter
  };

  const handleOpenEditModal = (user: any) => {
    setEditingUser(user);
    setIsEditModalOpen(true);
  };

  return (
    <>
      <AddUserModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} onUserAdded={handleDataUpdate} />
      <EditUserModal isOpen={isEditModalOpen} user={editingUser} onClose={() => setIsEditModalOpen(false)} onUserUpdated={handleDataUpdate} />
      <DashboardLayout role="admin" menuItems={adminMenuItems}>
        <div>
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-3xl font-bold text-white">User Management</h1>
            <button onClick={() => setIsModalOpen(true)} className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg"> + Add User </button>
          </div>

          {/* --- NEW: Search and Filter Controls --- */}
          <div className="flex flex-col md:flex-row gap-4 mb-6">
            <input
              type="text"
              placeholder="Search by name or email..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="flex-grow p-3 bg-gray-800 border-2 border-gray-700 rounded-lg text-white focus:outline-none focus:border-indigo-500"
            />
            <select
              value={roleFilter}
              onChange={(e) => setRoleFilter(e.target.value)}
              className="p-3 bg-gray-800 border-2 border-gray-700 rounded-lg text-white focus:outline-none focus:border-indigo-500"
            >
              <option value="all">All Roles</option>
              <option value="admin">Admin</option>
              <option value="customer">Customer</option>
              <option value="delivery_guy">Delivery Guy</option>
            </select>
          </div>

          {isLoading && <p className="text-white text-center">Loading users...</p>}
          {error && <p className="text-red-400 text-center bg-red-900/20 p-3 rounded-lg">{error}</p>}
          
          {!isLoading && !error && (
            <div className="bg-gray-800 rounded-xl shadow-md overflow-hidden">
              <table className="w-full">
                <thead className="bg-gray-700">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Name</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Email</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Role</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Actions</th>
                    </tr>
                </thead>
                <tbody className="divide-y divide-gray-700">
                  {filteredUsers.length > 0 ? filteredUsers.map((user) => (
                    <tr key={user.customer_id} className="hover:bg-gray-700">
                      <td className="px-6 py-4 whitespace-nowrap text-white">{user.name}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-gray-400">{user.email}</td>
                      <td className="px-6 py-4 whitespace-nowrap"><span className="px-2 py-1 text-xs font-semibold rounded-full capitalize bg-indigo-900/50 text-indigo-300">{user.role.replace('_', ' ')}</span></td>
                      <td className="px-6 py-4 whitespace-nowrap"><span className={`px-2 py-1 text-xs font-semibold rounded-full ${user.is_active ? 'bg-green-900/50 text-green-300' : 'bg-red-900/50 text-red-300'}`}>{user.is_active ? 'Active' : 'Inactive'}</span></td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <button onClick={() => handleOpenEditModal(user)} className="text-indigo-400 hover:text-indigo-300 mr-4 font-medium">Edit</button>
                        <button onClick={() => handleDeleteUser(user.customer_id)} className="text-red-400 hover:text-red-300 font-medium">Delete</button>
                      </td>
                    </tr>
                  )) : (
                    <tr><td colSpan="5" className="text-center py-8 text-gray-400">No users found.</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </DashboardLayout>
    </>
  );
}