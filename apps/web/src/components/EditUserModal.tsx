// src/components/EditUserModal.tsx

import { useState, useEffect, FormEvent } from 'react';

// Define the component's props
interface EditUserModalProps {
  isOpen: boolean;
  user: any | null; // The user object to edit
  onClose: () => void;
  onUserUpdated: () => void; // A function to refresh the user list
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1/admin';

export default function EditUserModal({ isOpen, user, onClose, onUserUpdated }: EditUserModalProps) {
  // Internal state for the form fields
  const [formData, setFormData] = useState({
    name: '',
    phone: '',
    is_active: true,
  });
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // This effect runs when the 'user' prop changes.
  // It populates the form with the user's current data when the modal opens.
  useEffect(() => {
    if (user) {
      setFormData({
        name: user.name || '',
        phone: user.phone || '',
        is_active: user.is_active,
      });
    }
  }, [user]);

  if (!isOpen || !user) return null;

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    const token = localStorage.getItem('logimas_token');
    if (!token) {
      setError("Authentication error. Please log in again.");
      setIsLoading(false);
      return;
    }

    try {
      // Use the PATCH method and include the user's ID in the URL
      const response = await fetch(`${API_URL}/users/${user.customer_id}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to update user.');
      }

      alert('User updated successfully!');
      onUserUpdated(); // Refresh the list on the main page
      onClose(); // Close the modal

    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    // Handle the boolean value from the select dropdown
    const newValue = type === 'select-one' ? (value === 'true') : value;
    setFormData(prev => ({ ...prev, [name]: newValue }));
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-60 flex justify-center items-center z-50">
      <div className="bg-gray-800 p-8 rounded-xl shadow-lg w-full max-w-md">
        <h2 className="text-2xl font-bold text-white mb-6">Edit User</h2>
        
        {error && <p className="bg-red-900/50 text-red-400 p-3 rounded-lg mb-4">{error}</p>}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="text-sm text-gray-400">Email (cannot be changed)</label>
            <input
              type="email"
              value={user.email}
              readOnly
              className="w-full mt-1 px-4 py-3 bg-gray-900 text-gray-400 border border-gray-700 rounded-lg cursor-not-allowed"
            />
          </div>
          <div>
            <label className="text-sm text-gray-400">Role (cannot be changed)</label>
            <input
              type="text"
              value={user.role}
              readOnly
              className="w-full mt-1 px-4 py-3 bg-gray-900 text-gray-400 border border-gray-700 rounded-lg cursor-not-allowed"
            />
          </div>
          <div>
            <label className="text-sm text-gray-400">Full Name</label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              required
              className="w-full mt-1 px-4 py-3 bg-gray-700 text-white border border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          <div>
            <label className="text-sm text-gray-400">Phone Number</label>
            <input
              type="tel"
              name="phone"
              value={formData.phone}
              onChange={handleInputChange}
              className="w-full mt-1 px-4 py-3 bg-gray-700 text-white border border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          <div>
            <label className="text-sm text-gray-400">Status</label>
            <select
              name="is_active"
              value={String(formData.is_active)}
              onChange={handleInputChange}
              className="w-full mt-1 px-4 py-3 bg-gray-700 text-white border border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500"
            >
              <option value="true">Active</option>
              <option value="false">Inactive</option>
            </select>
          </div>

          <div className="flex justify-end gap-4 pt-4">
            <button type="button" onClick={onClose} className="px-4 py-2 text-gray-300">Cancel</button>
            <button type="submit" disabled={isLoading} className="px-6 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg disabled:opacity-50">
              {isLoading ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}