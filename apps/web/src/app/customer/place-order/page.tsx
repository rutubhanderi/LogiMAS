"use client";

import { useState, useEffect } from 'react';
import DashboardLayout from '@/components/DashboardLayout';

// ... (customerMenuItems, initial states, and ProductSelector component are all UNCHANGED)
const customerMenuItems = [
    { name: 'Dashboard', href: '/customer/dashboard', icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" /></svg> },
    { name: 'Chat', href: '/customer/chat', icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" /></svg> },
    { name: 'Tracking', href: '/customer/tracking', icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" /></svg> },
    { name: 'Place Order', href: '/customer/place-order', icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" /></svg> },
    { name: 'My Orders', href: '/customer/orders', icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" /></svg> },
];
const initialItem = { sku: '', name: '', qty: 1, price: 0 };
const initialDestination = { address: '', city: '', postal_code: '' };

const ProductSelector = ({ inventory, selectedSku, onSelect }) => {
    const [searchTerm, setSearchTerm] = useState('');
    const [isOpen, setIsOpen] = useState(false);
    const filteredInventory = inventory.filter(item => item.product_name.toLowerCase().includes(searchTerm.toLowerCase()) || item.sku.toLowerCase().includes(searchTerm.toLowerCase()));
    const selectedProduct = inventory.find(item => item.sku === selectedSku);
    return (
        <div className="relative md:col-span-6">
            <div onClick={() => setIsOpen(!isOpen)} className="w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-700 cursor-pointer flex justify-between items-center">
                {selectedProduct ? `${selectedProduct.sku} - ${selectedProduct.product_name}` : <span className="text-gray-400">Select a Product</span>}
                <span>▼</span>
            </div>
            {isOpen && (
                <div className="absolute z-10 w-full mt-1 bg-white dark:bg-gray-800 border rounded-lg shadow-lg">
                    <input type="text" placeholder="Search by name or SKU..." className="w-full px-3 py-2 border-b" value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} />
                    <ul className="max-h-60 overflow-y-auto">
                        {filteredInventory.length > 0 ? filteredInventory.map(item => (
                            <li key={item.sku} onClick={() => { onSelect(item.sku); setIsOpen(false); setSearchTerm(''); }} className="p-3 hover:bg-indigo-500 hover:text-white cursor-pointer flex justify-between">
                                <div><p className="font-bold">{item.product_name}</p><p className="text-xs text-gray-500 dark:text-gray-400">{item.sku}</p></div>
                                <p className="font-semibold">${item.price.toFixed(2)}</p>
                            </li>
                        )) : <li className="p-3 text-gray-500">No products found.</li>}
                    </ul>
                </div>
            )}
        </div>
    );
};


export default function PlaceOrder() {
  const [items, setItems] = useState([initialItem]);
  const [destination, setDestination] = useState(initialDestination);
  const [orderTotal, setOrderTotal] = useState(0);
  const [inventory, setInventory] = useState([]);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // ... (All helper functions and useEffect hooks are UNCHANGED)
  useEffect(() => {
    const fetchInventory = async () => {
        try {
            const token = localStorage.getItem('logimas_token');
            if (!token) { setError('You must be logged in to view products.'); return; }
            const response = await fetch('http://localhost:8000/api/v1/inventory/skus', { headers: { 'Authorization': `Bearer ${token}` } });
            if (response.status === 401) { setError('Your session has expired. Please log in again.'); return; }
            if (!response.ok) { throw new Error('Could not fetch inventory from the server.'); }
            const data = await response.json();
            if (data.length === 0) { setError('No inventory items are available at this time.'); }
            setInventory(data);
        } catch (err) { setError(err.message); }
    };
    fetchInventory();
  }, []);

  useEffect(() => {
    const total = items.reduce((sum, item) => sum + (Number(item.qty) * Number(item.price)), 0);
    setOrderTotal(total);
  }, [items]);
  
  const handleItemChange = (index, selectedSku) => {
    const selectedProduct = inventory.find(invItem => invItem.sku === selectedSku);
    if (selectedProduct) {
      const newItems = [...items];
      newItems[index] = { ...newItems[index], sku: selectedProduct.sku, name: selectedProduct.product_name, price: selectedProduct.price };
      setItems(newItems);
    }
  };

  const handleQtyChange = (index, qty) => {
      const newItems = [...items];
      newItems[index].qty = Math.max(1, parseInt(qty, 10) || 1);
      setItems(newItems);
  };

  const addItem = () => setItems([...items, { ...initialItem }]);
  const removeItem = (index) => setItems(items.filter((_, i) => i !== index));
  const resetForm = () => {
    setItems([{ ...initialItem }]);
    setDestination({ ...initialDestination });
  };
  
  // --- MODIFIED: handleSubmit to handle the simpler response ---
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    if (items.some(item => !item.sku) || !destination.address || !destination.city) {
      setError('Please fill out all required fields.');
      setIsLoading(false);
      return;
    }

    const orderData = { items, destination };

    try {
      const token = localStorage.getItem('logimas_token');
      if (!token) {
        setError('You must be logged in to place an order.');
        setIsLoading(false);
        return;
      }
      
      const response = await fetch('http://localhost:8000/api/v1/orders/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify(orderData),
      });

      if (!response.ok) {
        const errorResult = await response.json();
        throw new Error(errorResult.detail || 'An unknown error occurred.');
      }

      // The result is now the order object directly
      const result = await response.json();
      
      // Access order_id directly from the result
      alert(`Order placed successfully! Order ID: ${result.order_id}`);
      resetForm();

    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    // ... (The JSX for the form is UNCHANGED)
    <DashboardLayout role="customer" menuItems={customerMenuItems}>
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-6">Place New Order</h1>
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-8">
          <form onSubmit={handleSubmit} className="space-y-8">
            <div className="space-y-4 p-4 border rounded-lg">
              <h2 className="text-xl font-semibold">Destination Details</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <input type="text" placeholder="Full Street Address" value={destination.address} onChange={(e) => setDestination({ ...destination, address: e.target.value })} required className="md:col-span-3 w-full px-3 py-2 border rounded-lg" />
                <input type="text" placeholder="City" value={destination.city} onChange={(e) => setDestination({ ...destination, city: e.target.value })} required className="w-full px-3 py-2 border rounded-lg" />
                <input type="text" placeholder="Postal Code" value={destination.postal_code} onChange={(e) => setDestination({ ...destination, postal_code: e.target.value })} required className="w-full px-3 py-2 border rounded-lg" />
              </div>
            </div>
            <div className="space-y-4 p-4 border rounded-lg">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold">Items</h2>
                <button type="button" onClick={addItem} className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 font-bold">+</button>
              </div>
              {inventory.length === 0 && error && <p className="text-yellow-500 text-center py-2">{error}</p>}
              {items.map((item, index) => (
                <div key={index} className="grid grid-cols-1 md:grid-cols-10 gap-3 items-center p-2 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <ProductSelector inventory={inventory} selectedSku={item.sku} onSelect={(sku) => handleItemChange(index, sku)} />
                  <input type="number" placeholder="Qty" value={item.qty} onChange={(e) => handleQtyChange(index, e.target.value)} required className="md:col-span-1 w-full px-3 py-2 border rounded-lg" min="1" />
                  <input type="text" placeholder="Price" value={item.price > 0 ? `$${item.price.toFixed(2)}` : '$0.00'} readOnly className="md:col-span-2 w-full px-3 py-2 border rounded-lg bg-gray-200 dark:bg-gray-600 text-center" />
                  <div className="md:col-span-1 flex justify-end"><button type="button" onClick={() => removeItem(index)} className="px-3 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 font-bold">-</button></div>
                </div>
              ))}
            </div>
            {error && <p className="text-red-500 text-center text-sm font-semibold">{error}</p>}
            <div className="flex justify-between items-center pt-4 border-t">
              <div><h3 className="text-lg font-bold">Total: ${orderTotal.toFixed(2)}</h3></div>
              <div className="flex gap-4">
                <button type="submit" disabled={isLoading} className="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg disabled:bg-indigo-400 disabled:cursor-not-allowed">
                  {isLoading ? 'Placing Order...' : 'Place Order'}
                </button>
                <button type="button" onClick={resetForm} className="px-6 py-3 bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600">Reset</button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </DashboardLayout>
  );
}