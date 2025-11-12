'use client';

import { useState } from "react";
import DashboardLayout from "@/components/DashboardLayout";
import TrackingMap from "@/components/TrackingMap";
import { fetchShipmentById } from "@/lib/supabase/client";

const adminMenuItems = [
  { name: "Dashboard", href: "/admin/dashboard", icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/></svg> },
  { name: 'Dispatch Orders', href: '/admin/dispatch', icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" /></svg> },
  { name: "Chat", href: "/admin/chat", icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"/></svg> },
  { name: "Tracking", href: "/admin/tracking", icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"/></svg> },
  { name: "Knowledge Base", href: "/admin/knowledge-base", icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/></svg> },
  //{ name: "Analysis", href: "/admin/analysis", icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg> },
  { name: "Users", href: "/admin/users", icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"/></svg> },
  { name: "Warehouses", href: "/admin/warehouses", icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/></svg> },
  { name: "Vehicles", href: "/admin/vehicles", icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z"/></svg> },
];

export default function AdminTracking() {
  const [shipmentId, setShipmentId] = useState("");
  const [selectedShipment, setSelectedShipment] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleTrack = () => {
    (async () => {
      if (!shipmentId) return;
      setLoading(true);
      try {
        const data = await fetchShipmentById(shipmentId);
        if (!data) {
          alert("Shipment not found");
          setSelectedShipment(null);
        } else {
          setSelectedShipment({
            id: data.id, order: data.order, customer: data.customer, status: data.status, eta: data.eta,
            progress: data.progress || 0, origin: data.origin, destination: data.destination,
            currentLocation: data.currentLocation,
          });
        }
      } catch (e) {
        console.error(e);
        alert("Error fetching shipment");
        setSelectedShipment(null);
      } finally {
        setLoading(false);
      }
    })();
  };
  return (
    <DashboardLayout role="admin" menuItems={adminMenuItems}>
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-6">Shipment Tracking</h1>

        <div className="mb-6">
          <div className="flex gap-3">
            <div className="relative flex-1">
              <input
                type="text"
                value={shipmentId}
                onChange={(e) => setShipmentId(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && handleTrack()}
                placeholder="Enter Shipment ID to track live location"
                className="w-full px-4 py-3 pl-12 border rounded-lg dark:bg-gray-800 dark:text-white"
              />
              <svg className="absolute left-4 top-3.5 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
            </div>
            <button onClick={handleTrack} className="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg">
              {loading ? 'Tracking...' : 'Track Shipment'}
            </button>
          </div>
        </div>

        {selectedShipment && (
          <div className="mb-8 space-y-6">
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Shipment Details</h2>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div><p className="text-sm text-gray-500 dark:text-gray-400">Shipment ID</p><p className="font-semibold dark:text-white">{selectedShipment.id}</p></div>
                <div><p className="text-sm text-gray-500 dark:text-gray-400">Customer</p><p className="font-semibold dark:text-white">{selectedShipment.customer}</p></div>
                <div><p className="text-sm text-gray-500 dark:text-gray-400">Status</p><span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${selectedShipment.status === "delivered" ? "bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400" : "bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400"}`}>{selectedShipment.status}</span></div>
                <div><p className="text-sm text-gray-500 dark:text-gray-400">ETA</p><p className="font-semibold dark:text-white">{selectedShipment.eta}</p></div>
              </div>
              <div className="mt-4"><p className="text-sm text-gray-500 dark:text-gray-400 mb-2">Progress</p><div className="flex items-center gap-3"><div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-3"><div className="bg-indigo-600 h-3 rounded-full" style={{ width: `${selectedShipment.progress}%` }}></div></div><span className="text-sm font-medium dark:text-white">{selectedShipment.progress}%</span></div></div>
            </div>
            <TrackingMap origin={selectedShipment.origin} destination={selectedShipment.destination} currentLocation={selectedShipment.currentLocation} />
          </div>
        )}

        
        
      </div>
    </DashboardLayout>
  );
}