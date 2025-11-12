"use client";

import { useEffect, useState } from "react";
import DashboardLayout from "@/components/DashboardLayout";
import Link from "next/link";
import { api } from "@/lib/api";
import { fetchOrdersForCustomer } from "@/lib/supabase/client";

const customerMenuItems = [
  {
    name: "Dashboard",
    href: "/customer/dashboard",
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
          d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
        />
      </svg>
    ),
  },
  {
    name: "Chat",
    href: "/customer/chat",
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
  {
    name: "Tracking",
    href: "/customer/tracking",
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
          d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"
        />
      </svg>
    ),
  },
  {
    name: "Place Order",
    href: "/customer/place-order",
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
          d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"
        />
      </svg>
    ),
  },
  {
    name: "My Orders",
    href: "/customer/orders",
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
          d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
        />
      </svg>
    ),
  },
];

const OrdersPlaceholder: any[] = [];

export default function MyOrders() {
  const [orders, setOrders] = useState<any[]>(OrdersPlaceholder);
  const [filteredOrders, setFilteredOrders] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("all"); // 'all', 'pending', 'in_transit', 'delivered'

  useEffect(() => {
    const load = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const token = localStorage.getItem("logimas_token");
        if (!token) throw new Error("Not authenticated");
        const user = await api.getCurrentUser(token);
        const data = await fetchOrdersForCustomer(user.customer_id, 100);

        // Map to expected UI shape, handling schema fields
        const mapped = (data || []).map((o: any) => ({
          id: o.order_id,
          shipmentId:
            Array.isArray(o.shipments) && o.shipments.length > 0
              ? o.shipments[0].shipment_id
              : null,
          date: o.order_date
            ? new Date(o.order_date).toLocaleDateString("en-US", {
                year: "numeric",
                month: "short",
                day: "numeric",
              })
            : "—",
          status: (o.shipments?.[0]?.status || o.status || "pending").replace(
            /_/g,
            " "
          ), // Normalize status (e.g., 'in_transit' -> 'in transit')
          items: o.items
            ? Array.isArray(o.items)
              ? o.items
                  .map((it: any) => it.name || it.product_name || "Item")
                  .join(", ")
              : JSON.stringify(o.items)
            : "—",
          amount: o.order_total
            ? `₹${Number(o.order_total).toFixed(2)}`
            : "₹0.00",
          eta: o.shipments?.[0]?.expected_arrival
            ? new Date(o.shipments[0].expected_arrival).toLocaleDateString(
                "en-US",
                { month: "short", day: "numeric" }
              )
            : "—",
          destination: o.destination
            ? `${o.destination.address || ""}, ${
                o.destination.city || ""
              }`.trim() || "—"
            : "—",
        }));
        setOrders(mapped);
        setFilteredOrders(mapped); // Initial filter is all
      } catch (err: any) {
        setError(err.message || "Failed to load orders");
        console.error("Orders load error:", err);
      } finally {
        setIsLoading(false);
      }
    };
    load();
  }, []);

  // Filter orders based on search and status
  useEffect(() => {
    let filtered = orders;
    if (searchTerm) {
      filtered = filtered.filter(
        (order) =>
          order.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
          order.items.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    if (statusFilter !== "all") {
      filtered = filtered.filter(
        (order) => order.status.toLowerCase() === statusFilter.toLowerCase()
      );
    }
    setFilteredOrders(filtered);
  }, [searchTerm, statusFilter, orders]);

  // Status color classes
  const getStatusBadgeClass = (status: string) => {
    const normalized = status.toLowerCase();
    switch (normalized) {
      case "delivered":
        return "bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400";
      case "in-transit":
        return "bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400";
      case "pending":
        return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400";
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400";
    }
  };

  // Loading skeleton for orders
  const LoadingSkeleton = () => (
    <div className="animate-pulse space-y-4">
      {[...Array(5)].map((_, i) => (
        <div
          key={i}
          className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6"
        >
          <div className="flex justify-between items-start mb-4">
            <div>
              <div className="h-5 bg-gray-200 dark:bg-gray-700 rounded w-48 mb-2"></div>
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-32"></div>
            </div>
            <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-20"></div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            {[...Array(3)].map((_, j) => (
              <div key={j}>
                <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-16 mb-1"></div>
                <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-24"></div>
              </div>
            ))}
          </div>
          <div className="flex gap-3">
            {[...Array(2)].map((_, k) => (
              <div
                key={k}
                className="h-8 bg-gray-200 dark:bg-gray-700 rounded-lg w-24"
              ></div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );

  if (isLoading) {
    return (
      <DashboardLayout role="customer" menuItems={customerMenuItems}>
        <div>
          <div className="flex justify-between items-center mb-6 animate-pulse">
            <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-32"></div>
            <div className="h-10 bg-gray-200 dark:bg-gray-700 rounded-lg w-28"></div>
          </div>
          <LoadingSkeleton />
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout role="customer" menuItems={customerMenuItems}>
      <div className="space-y-6">
        {/* Header with CTA */}
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            My Orders ({filteredOrders.length})
          </h1>
          <Link
            href="/customer/place-order"
            className="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-xl transition-colors shadow-md"
          >
            + New Order
          </Link>
        </div>

        {/* Filters */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-4 flex flex-col md:flex-row gap-4 items-center justify-between">
          <div className="flex gap-4 items-center">
            <div className="relative">
              <input
                type="text"
                placeholder="Search by Order ID or Items..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 w-64"
              />
              <svg
                className="absolute left-3 top-2.5 w-5 h-5 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
            </div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="all">All Statuses</option>
              <option value="pending">Pending</option>
              <option value="in transit">In Transit</option>
              <option value="delivered">Delivered</option>
            </select>
          </div>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Showing {filteredOrders.length} of {orders.length} orders
          </p>
        </div>

        {/* Error Handling */}
        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-6 text-center">
            <p className="text-red-600 dark:text-red-400 mb-4">{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="px-4 py-2 bg-red-100 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-lg hover:bg-red-200 dark:hover:bg-red-800/20 transition-colors"
            >
              Retry Load
            </button>
          </div>
        )}

        {/* Orders List */}
        <div className="space-y-4">
          {filteredOrders.length > 0 ? (
            filteredOrders.map((order) => (
              <div
                key={order.id}
                className="bg-white dark:bg-gray-800 rounded-xl shadow-md hover:shadow-lg transition-shadow overflow-hidden"
              >
                <div className="p-6">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                        <span title={order.id}>Order #{order.id}</span>{" "}
                        {/* Full ID with tooltip for copy/paste */}
                      </h3>
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        Placed on {order.date}
                      </p>
                    </div>
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusBadgeClass(
                        order.status
                      )}`}
                    >
                      {order.status}
                    </span>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
                    <div>
                      <p className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">
                        Shipment ID
                      </p>
                      <p
                        className="font-semibold text-gray-900 dark:text-white break-all"
                        title={order.shipmentId || ""}
                      >
                        {order.shipmentId ? `#${order.shipmentId}` : "—"}{" "}
                        {/* Full ID with tooltip and break-all for long text */}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">
                        Items
                      </p>
                      <p className="font-semibold text-gray-900 dark:text-white text-sm">
                        {order.items}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">
                        Destination
                      </p>
                      <p className="font-semibold text-gray-900 dark:text-white text-sm">
                        {order.destination}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">
                        Amount
                      </p>
                      <p className="font-bold text-indigo-600 dark:text-indigo-400 text-lg">
                        {order.amount}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        ETA: {order.eta}
                      </p>
                    </div>
                  </div>
                  <div className="flex flex-col sm:flex-row gap-3 justify-end">
                    <Link
                      href={`/customer/tracking?id=${
                        order.shipmentId || order.id
                      }`}
                      className="px-6 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg transition-colors text-sm flex-1 text-center sm:flex-none"
                    >
                      Track Order
                    </Link>
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-12 text-center">
              <svg
                className="mx-auto h-12 w-12 text-gray-400 dark:text-gray-500 mb-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"
                />
              </svg>
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                No orders found
              </h3>
              <p className="text-gray-500 dark:text-gray-400 mb-6">
                {searchTerm || statusFilter !== "all"
                  ? "Try adjusting your search or filters."
                  : "Get started by placing your first order."}
              </p>
              <Link
                href="/customer/place-order"
                className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
              >
                Place Your First Order
              </Link>
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}
