'use client';

import { useState, FormEvent } from 'react';
import apiClient from '../../../lib/apiClient';
import Link from 'next/link';

// Sample product catalog for the user to choose from
const productCatalog = [
  { sku: "PROD0001", name: "Industrial Widget", price: 75.50 },
  { sku: "PROD0002", name: "Heavy-Duty Gear", price: 120.00 },
  { sku: "PROD0007", name: "Precision Bearing", price: 45.99 },
  { sku: "PROD0008", name: "Hydraulic Pump", price: 250.00 },
];

export default function PlaceOrderPage() {
  const [selectedItems, setSelectedItems] = useState<{ sku: string; name: string; price: number }[]>([]);
  const [destinationAddress, setDestinationAddress] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<{ message: string; orderId: string } | null>(null);

  const handleAddItem = (product: { sku: string; name: string; price: number }) => {
    setSelectedItems(prev => [...prev, product]);
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (selectedItems.length === 0 || !destinationAddress.trim()) {
      setError("Please add at least one item and provide a destination address.");
      return;
    }

    setIsLoading(true);
    setError(null);
    setSuccess(null);

    try {
      // For this demo, we'll use a hardcoded customer ID from our seed data.
      // In a real auth system, this would come from the logged-in user's context.
      const DEMO_CUSTOMER_ID = "bd47177f-ce4b-422d-81ef-f3058b3848d9"; // Replace with a valid customer_id from your 'profiles' table

      const payload = {
        customer_id: DEMO_CUSTOMER_ID,
        items: selectedItems,
        destination: { address: destinationAddress }, // Simple destination for now
      };

      const response = await apiClient.post('/orders', payload);
      
      setSuccess({ message: response.data.message, orderId: response.data.order.order_id });
      setSelectedItems([]);
      setDestinationAddress('');
    } catch (err: any) {
      setError(err.response?.data?.detail || "An unexpected error occurred while placing the order.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-4xl font-bold text-slate-900">Place a New Order</h1>
        <p className="text-lg text-slate-600 mt-1">
          Select products from the catalog and specify a destination to create a new order.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Product Catalog Section */}
        <div className="lg:col-span-1">
          <div className="bg-white p-6 rounded-xl shadow-lg">
            <h2 className="text-2xl font-bold text-slate-800 mb-4">Product Catalog</h2>
            <div className="space-y-3">
              {productCatalog.map(product => (
                <div key={product.sku} className="flex justify-between items-center p-3 border rounded-lg">
                  <div>
                    <p className="font-semibold text-slate-800">{product.name}</p>
                    <p className="text-sm text-slate-500">{product.sku} - ${product.price.toFixed(2)}</p>
                  </div>
                  <button onClick={() => handleAddItem(product)} className="px-3 py-1 bg-blue-100 text-blue-800 text-sm font-semibold rounded-full hover:bg-blue-200">
                    + Add
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Order Form Section */}
        <div className="lg:col-span-2">
          <div className="bg-white p-8 rounded-xl shadow-lg">
            <form onSubmit={handleSubmit} className="space-y-6">
              <h2 className="text-2xl font-bold text-slate-800 mb-4">Your Order</h2>
              
              <div>
                <label htmlFor="items" className="block text-base font-semibold text-slate-800">
                  Selected Items ({selectedItems.length})
                </label>
                <div className="mt-2 p-4 border border-slate-300 rounded-lg min-h-[120px] bg-slate-50">
                  {selectedItems.length === 0 ? (
                    <p className="text-slate-400">Click "Add" on products from the catalog.</p>
                  ) : (
                    <ul className="space-y-2">
                      {selectedItems.map((item, index) => (
                        <li key={index} className="flex justify-between items-center">
                          <span className="text-slate-700">{item.name}</span>
                          <span className="font-mono text-slate-500">${item.price.toFixed(2)}</span>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              </div>

              <div>
                <label htmlFor="destination" className="block text-base font-semibold text-slate-800">
                  Destination Address
                </label>
                <input
                  id="destination" type="text" value={destinationAddress}
                  onChange={(e) => setDestinationAddress(e.target.value)}
                  placeholder="e.g., 123 Main St, Anytown, USA"
                  className="mt-2 w-full p-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" required
                />
              </div>

              <button type="submit"
                className="w-full px-6 py-4 bg-green-600 text-white font-bold text-lg rounded-lg hover:bg-green-700 transition-colors disabled:bg-slate-400"
                disabled={isLoading || selectedItems.length === 0}
              >
                {isLoading ? 'Placing Order...' : 'Place Order'}
              </button>
            </form>

            {success && 
              <div className="mt-4 text-center p-4 bg-green-100 text-green-800 rounded-lg">
                <p className="font-bold">{success.message}</p>
                <p className="text-sm mt-1">Order ID: <span className="font-mono">{success.orderId}</span></p>
                <Link href="/dashboard/tracking" className="text-blue-600 hover:underline text-sm mt-2 block">
                  Go to Tracking Page
                </Link>
              </div>
            }
            {error && <div className="mt-4 text-center p-3 bg-red-100 text-red-800 rounded-lg">{error}</div>}
          </div>
        </div>
      </div>
    </div>
  );
}