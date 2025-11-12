"use client";

import { useEffect, useMemo, useState } from "react";
import DashboardLayout from "@/components/DashboardLayout";

type RevenuePoint = { label: string; value: number };

async function fetchAnalytics() {
  const res = await fetch("http://localhost:8000/api/v1/analytics/summary");
  if (!res.ok) throw new Error("Failed to load analytics");
  return res.json();
}

const adminMenuItems = [
  {
    name: "Dashboard",
    href: "/admin/dashboard",
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
  {
    name: "Tracking",
    href: "/admin/tracking",
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
    name: "Knowledge Base",
    href: "/admin/knowledge-base",
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
          d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
        />
      </svg>
    ),
  },
  {
    name: "Analysis",
    href: "/admin/analysis",
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
          d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
        />
      </svg>
    ),
  },
  {
    name: "Users",
    href: "/admin/users",
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
          d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"
        />
      </svg>
    ),
  },
  {
    name: "Warehouses",
    href: "/admin/warehouses",
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
          d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
        />
      </svg>
    ),
  },
  {
    name: "Vehicles",
    href: "/admin/vehicles",
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
          d="M13 10V3L4 14h7v7l9-11h-7z"
        />
      </svg>
    ),
  },
];

export default function Analysis() {
  const [revenueTrend, setRevenueTrend] = useState<RevenuePoint[]>([]);
  const [statusDist, setStatusDist] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(true);
  const [kpis, setKpis] = useState<{
    total_revenue?: number;
    delivery_success_rate?: number;
    avg_delivery_time?: string;
    customer_satisfaction?: number;
  }>({});
  const [topPersonnel, setTopPersonnel] = useState<
    Array<{ name: string; deliveries?: number; rating?: number }>
  >([]);
  const [popularRoutes, setPopularRoutes] = useState<
    Array<{ route: string; shipments?: number }>
  >([]);

  const last7Labels = useMemo(() => {
    const arr: string[] = [];
    const now = new Date();
    for (let i = 6; i >= 0; i--) {
      const d = new Date(now);
      d.setDate(now.getDate() - i);
      arr.push(d.toLocaleDateString(undefined, { weekday: "short" }));
    }
    return arr;
  }, []);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const analytics = await fetchAnalytics();

        setKpis({
          total_revenue: Number(analytics.total_revenue || 0),
          delivery_success_rate: Number(analytics.delivery_success_rate || 0),
          avg_delivery_time: analytics.avg_delivery_time || null,
          customer_satisfaction: Number(analytics.customer_satisfaction || 0),
        });

        // revenue_trend_json is expected as { 'YYYY-MM-DD': amount }
        const trend = analytics.revenue_trend_json || {};
        // build last 7 days using last7Labels and the trend data
        const now = new Date();
        const sevenDaysAgo = new Date(now);
        sevenDaysAgo.setDate(now.getDate() - 6);
        const revPoints: RevenuePoint[] = [];
        for (let i = 0; i < 7; i++) {
          const d = new Date(sevenDaysAgo);
          d.setDate(sevenDaysAgo.getDate() + i);
          const key = d.toISOString().slice(0, 10);
          const val = trend[key] ? Number(trend[key]) : 0;
          revPoints.push({ label: last7Labels[i], value: Math.round(val) });
        }
        setRevenueTrend(revPoints);

        // status distribution
        const dist = analytics.delivery_status_distribution || {};
        setStatusDist(dist as Record<string, number>);

        // top personnel and popular routes
        const tp =
          (analytics.top_delivery_personnel &&
            analytics.top_delivery_personnel.personnel) ||
          [];
        setTopPersonnel(Array.isArray(tp) ? tp : []);
        const pr =
          (analytics.popular_routes && analytics.popular_routes.routes) || [];
        setPopularRoutes(Array.isArray(pr) ? pr : []);
      } catch (e) {
        console.error("Failed to load analysis data", e);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [last7Labels]);

  const totalStatuses =
    Object.values(statusDist).reduce((a, b) => a + b, 0) || 1;

  return (
    <DashboardLayout role="admin" menuItems={adminMenuItems}>
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-6">
          Analytics & Reports
        </h1>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-gradient-to-br from-blue-500 to-blue-600 p-6 rounded-xl shadow-md text-white">
            <p className="text-sm opacity-90">Total Revenue</p>
            <p className="text-3xl font-bold mt-2">
              {kpis.total_revenue
                ? `$${kpis.total_revenue.toLocaleString()}`
                : "—"}
            </p>
            <p className="text-sm mt-2 opacity-75">
              {kpis.total_revenue ? "30d" : ""}
            </p>
          </div>
          <div className="bg-gradient-to-br from-green-500 to-green-600 p-6 rounded-xl shadow-md text-white">
            <p className="text-sm opacity-90">Delivery Success Rate</p>
            <p className="text-3xl font-bold mt-2">
              {kpis.delivery_success_rate
                ? `${kpis.delivery_success_rate}%`
                : "—"}
            </p>
            <p className="text-sm mt-2 opacity-75">
              {kpis.delivery_success_rate ? "30d" : ""}
            </p>
          </div>
          <div className="bg-gradient-to-br from-purple-500 to-purple-600 p-6 rounded-xl shadow-md text-white">
            <p className="text-sm opacity-90">Avg Delivery Time</p>
            <p className="text-3xl font-bold mt-2">
              {kpis.avg_delivery_time ?? "—"}
            </p>
            <p className="text-sm mt-2 opacity-75">
              {kpis.avg_delivery_time ? "" : ""}
            </p>
          </div>
          <div className="bg-gradient-to-br from-orange-500 to-orange-600 p-6 rounded-xl shadow-md text-white">
            <p className="text-sm opacity-90">Customer Satisfaction</p>
            <p className="text-3xl font-bold mt-2">
              {kpis.customer_satisfaction
                ? kpis.customer_satisfaction > 5
                  ? `${kpis.customer_satisfaction}%`
                  : `${kpis.customer_satisfaction}/5`
                : "—"}
            </p>
            <p className="text-sm mt-2 opacity-75">
              {kpis.customer_satisfaction ? "" : ""}
            </p>
          </div>
        </div>

        {/* Charts Grid (Dynamic) */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Revenue Chart */}
          <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-md">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Revenue Trend
            </h3>
            {loading ? (
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Loading revenue…
              </p>
            ) : (
              <>
                <div className="h-64 flex items-end justify-around gap-2">
                  {revenueTrend.map((pt, i) => {
                    const max = Math.max(
                      1,
                      ...revenueTrend.map((p) => p.value)
                    );
                    const height = Math.round((pt.value / max) * 100);
                    return (
                      <div
                        key={i}
                        className="flex-1 bg-indigo-500 rounded-t"
                        style={{ height: `${height}%` }}
                        title={`$${pt.value}`}
                      ></div>
                    );
                  })}
                </div>
                <div className="flex justify-around mt-2 text-xs text-gray-500 dark:text-gray-400">
                  {revenueTrend.map((pt) => (
                    <span key={pt.label}>{pt.label}</span>
                  ))}
                </div>
              </>
            )}
          </div>

          {/* Delivery Status */}
          <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-md">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Delivery Status Distribution
            </h3>
            {loading ? (
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Loading statuses…
              </p>
            ) : (
              <div className="space-y-4">
                {Object.keys(statusDist).length === 0 && (
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    No shipment data in the last 7 days.
                  </p>
                )}
                {Object.entries(statusDist).map(([label, count]) => {
                  const pct = Math.round((count / totalStatuses) * 100);
                  const color =
                    label === "delivered"
                      ? "bg-green-500"
                      : label === "in-transit"
                      ? "bg-blue-500"
                      : label === "pending"
                      ? "bg-yellow-500"
                      : "bg-gray-400";
                  return (
                    <div key={label}>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-gray-600 dark:text-gray-400 capitalize">
                          {label.replace("_", " ")}
                        </span>
                        <span className="font-medium text-gray-900 dark:text-white">
                          {pct}%
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
                        <div
                          className={`${color} h-3 rounded-full`}
                          style={{ width: `${pct}%` }}
                        ></div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* Top Performers */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-md">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Top Delivery Personnel
            </h3>
            <div className="space-y-3">
              {topPersonnel.length === 0 && (
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  No top personnel data available.
                </p>
              )}
              {topPersonnel.map((person, i) => (
                <div
                  key={i}
                  className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg"
                >
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">
                      {person.name}
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {person.deliveries ?? 0} deliveries
                    </p>
                  </div>
                  <div className="flex items-center gap-1">
                    <svg
                      className="w-4 h-4 text-yellow-400"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                    <span className="text-sm font-medium text-gray-900 dark:text-white">
                      {person.rating ?? "-"}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-md">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Popular Routes
            </h3>
            <div className="space-y-3">
              {popularRoutes.length === 0 && (
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  No popular routes available.
                </p>
              )}
              {popularRoutes.map((route, i) => (
                <div
                  key={i}
                  className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg"
                >
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">
                      {route.route}
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {route.shipments ?? 0} shipments
                    </p>
                  </div>
                  <svg
                    className="w-5 h-5 text-indigo-600 dark:text-indigo-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M13 7l5 5m0 0l-5 5m5-5H6"
                    />
                  </svg>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
