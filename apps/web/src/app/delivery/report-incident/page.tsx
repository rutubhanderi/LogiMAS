'use client';

import { useState } from 'react';
import DashboardLayout from '@/components/DashboardLayout';

// Define the menu items for the delivery guy's dashboard
const deliveryMenuItems = [
  { name: 'Dashboard', href: '/delivery/dashboard', icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" /></svg> },
  { name: 'Chat', href: '/delivery/chat', icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" /></svg> },
  { name: 'Tracking', href: '/delivery/tracking', icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" /></svg> },
  { name: 'Report Incident', href: '/delivery/report-incident', icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg> }
  //{ name: 'My Deliveries', href: '/delivery/deliveries', icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" /></svg> },
];

export default function ReportIncident() {
  // State to manage the form's input values
  const [formData, setFormData] = useState({
    shipmentId: '',
    incidentType: 'delay',
    description: '',
    severity: 'medium',
  });

  /**
   * Handles form submission by sending data to the backend API.
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault(); // Prevent the default browser form submission

    try {
      // Send a POST request to the backend endpoint
      const response = await fetch('http://localhost:8000/api/v1/delivery/report-incident', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      // Check if the request was successful
      if (!response.ok) {
        // If not, throw an error to be caught by the catch block
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Parse the JSON response from the server
      const result = await response.json();
      console.log('Incident reported:', result);
      alert('Incident reported successfully!');
      
      // Reset the form to its initial state after a successful submission
      setFormData({
        shipmentId: '',
        incidentType: 'delay',
        description: '',
        severity: 'medium',
      });

    } catch (error) {
      // Handle any errors that occurred during the fetch operation
      console.error('Failed to submit incident report:', error);
      alert('Failed to submit incident report. Please try again.');
    }
  };

  return (
    <DashboardLayout role="delivery_guy" menuItems={deliveryMenuItems}>
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-6">Report Incident</h1>

        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Shipment ID Input */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Shipment ID</label>
              <input type="text" value={formData.shipmentId} onChange={(e) => setFormData({ ...formData, shipmentId: e.target.value })} required className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-red-500 dark:bg-gray-700 dark:text-white" placeholder="SHP-001" />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Incident Type Selector */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Incident Type</label>
                <select value={formData.incidentType} onChange={(e) => setFormData({ ...formData, incidentType: e.target.value })} className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-red-500 dark:bg-gray-700 dark:text-white">
                  <option value="delay">Delay</option>
                  <option value="damage">Package Damage</option>
                  <option value="accident">Vehicle Accident</option>
                  <option value="theft">Theft</option>
                  <option value="other">Other</option>
                </select>
              </div>
              {/* Severity Selector */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Severity</label>
                <select value={formData.severity} onChange={(e) => setFormData({ ...formData, severity: e.target.value })} className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-red-500 dark:bg-gray-700 dark:text-white">
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="critical">Critical</option>
                </select>
              </div>
            </div>

            {/* Description Textarea */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Description</label>
              <textarea value={formData.description} onChange={(e) => setFormData({ ...formData, description: e.target.value })} required className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-red-500 dark:bg-gray-700 dark:text-white" rows={5} placeholder="Describe the incident in detail..."></textarea>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-4">
              <button type="submit" className="px-6 py-3 bg-red-600 hover:bg-red-700 text-white font-medium rounded-lg transition-colors">Submit Report</button>
              <button type="button" onClick={() => setFormData({ shipmentId: '', incidentType: 'delay', description: '', severity: 'medium' })} className="px-6 py-3 bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-900 dark:text-white font-medium rounded-lg transition-colors">Reset</button>
            </div>
          </form>
        </div>
      </div>
    </DashboardLayout>
  );
}