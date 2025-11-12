"use client";

import DashboardLayout from "@/components/DashboardLayout";
import { useState, useEffect } from "react";
import { supabase } from "@/lib/supabase/client";

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
  {
    name: "Dispatch Orders",
    href: "/admin/dispatch",
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
  }
  /*{
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
  }*/,
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

const tables = [
  {
    name: "customers",
    description: "User accounts with roles (customer, delivery_guy, admin)",
    columns: 10,
  },
  {
    name: "orders",
    description: "Customer orders with items and delivery details",
    columns: 9,
  },
  {
    name: "shipments",
    description: "Delivery shipments linked to orders and vehicles",
    columns: 9,
  },
  {
    name: "warehouses",
    description: "Warehouse locations and regions",
    columns: 5,
  },
  {
    name: "vehicles",
    description: "Fleet vehicles with capacity and status",
    columns: 6,
  },
  {
    name: "inventory",
    description: "Warehouse inventory and stock levels",
    columns: 6,
  },
  {
    name: "vehicle_telemetry",
    description: "Real-time vehicle tracking data",
    columns: 7,
  },
  {
    name: "fuel_prices",
    description: "Current and historical fuel prices",
    columns: 3,
  },
  {
    name: "packaging_types",
    description: "Packaging options with dimensions",
    columns: 7,
  },
  {
    name: "documents",
    description: "Vector embeddings for AI search",
    columns: 9,
  },
  {
    name: "agent_audit_logs",
    description: "AI agent decision tracking",
    columns: 6,
  },
];

export default function KnowledgeBase() {
  const [selectedTable, setSelectedTable] = useState<string>("customers");
  const [tableData, setTableData] = useState<any[]>([]);
  const [rowCount, setRowCount] = useState<number | null>(null);
  const [rowLimit, setRowLimit] = useState<number>(50);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [columns, setColumns] = useState<string[]>([]);

  // Search/Filter states
  const [searchColumn, setSearchColumn] = useState<string>("");
  const [searchValue, setSearchValue] = useState<string>("");
  const [appliedSearch, setAppliedSearch] = useState<{
    column: string;
    value: string;
  } | null>(null);

  // Function to fetch table data
  const fetchTableData = async (
    page: number = 1,
    search: { column: string; value: string } | null = null
  ) => {
    if (!selectedTable) return;

    setLoading(true);
    setError(null);

    try {
      const from = (page - 1) * rowLimit;
      const to = from + rowLimit - 1;

      // Build query
      let query = supabase.from(selectedTable).select("*", { count: "exact" });

      // Apply search filter if provided
      if (search && search.column && search.value) {
        query = query.ilike(search.column, `%${search.value}%`);
      }

      // Apply pagination
      const { data, error: fetchError, count } = await query.range(from, to);

      if (fetchError) throw fetchError;

      setTableData(data || []);
      setRowCount(count);
      setCurrentPage(page);

      // Extract column names from first row
      if (data && data.length > 0) {
        setColumns(Object.keys(data[0]));
      } else if (!search) {
        // If no data and no search, fetch columns from empty query
        const { data: sampleData } = await supabase
          .from(selectedTable)
          .select("*")
          .limit(1);
        if (sampleData && sampleData.length > 0) {
          setColumns(Object.keys(sampleData[0]));
        }
      }
    } catch (err: any) {
      setError(err.message || "Failed to fetch table data");
      console.error("Table data error:", err);
      setTableData([]);
      setColumns([]);
    } finally {
      setLoading(false);
    }
  };

  // Handle search
  const handleSearch = () => {
    if (searchColumn && searchValue) {
      const search = { column: searchColumn, value: searchValue };
      setAppliedSearch(search);
      setCurrentPage(1);
      fetchTableData(1, search);
    }
  };

  // Clear search
  const handleClearSearch = () => {
    setSearchColumn("");
    setSearchValue("");
    setAppliedSearch(null);
    setCurrentPage(1);
    fetchTableData(1, null);
  };

  // Reset data when table changes
  useEffect(() => {
    setTableData([]);
    setRowCount(null);
    setError(null);
    setColumns([]);
    setCurrentPage(1);
    setSearchColumn("");
    setSearchValue("");
    setAppliedSearch(null);
  }, [selectedTable]);

  // Calculate total pages
  const totalPages = rowCount ? Math.ceil(rowCount / rowLimit) : 0;

  // Format cell value for display
  const formatCellValue = (value: any): string => {
    if (value === null || value === undefined) return "-";
    if (typeof value === "object") return JSON.stringify(value);
    if (typeof value === "boolean") return value ? "Yes" : "No";
    return String(value);
  };

  return (
    <DashboardLayout role="admin" menuItems={adminMenuItems}>
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-6">
          Knowledge Base
        </h1>

        <p className="text-gray-600 dark:text-gray-400 mb-8">
          Database schema documentation for LogiMAS system
        </p>

        {/* Table Selection and View Data Section */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            Table Data Viewer
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
            {/* Dropdown for table selection */}
            <div className="lg:col-span-2">
              <label
                htmlFor="table-select"
                className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
              >
                Select Table
              </label>
              <select
                id="table-select"
                value={selectedTable}
                onChange={(e) => setSelectedTable(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              >
                {tables.map((table) => (
                  <option key={table.name} value={table.name}>
                    {table.name} ({table.columns} columns)
                  </option>
                ))}
              </select>
            </div>

            {/* Row limit selector */}
            <div>
              <label
                htmlFor="row-limit"
                className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
              >
                Rows per Page
              </label>
              <select
                id="row-limit"
                value={rowLimit}
                onChange={(e) => {
                  setRowLimit(Number(e.target.value));
                  setCurrentPage(1);
                }}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value={10}>10 rows</option>
                <option value={25}>25 rows</option>
                <option value={50}>50 rows</option>
                <option value={100}>100 rows</option>
                <option value={250}>250 rows</option>
              </select>
            </div>

            {/* Button to fetch table data */}
            <div className="flex items-end">
              <button
                onClick={() => fetchTableData(1, appliedSearch)}
                disabled={loading}
                className="w-full px-6 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-400 text-white rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <svg
                      className="animate-spin h-4 w-4 text-white"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      ></circle>
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      ></path>
                    </svg>
                    Loading...
                  </>
                ) : (
                  <>
                    <svg
                      className="w-4 h-4"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                      />
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                      />
                    </svg>
                    View Data
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Search/Filter Section */}
          {columns.length > 0 && (
            <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
              <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">
                Search & Filter
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Column
                  </label>
                  <select
                    value={searchColumn}
                    onChange={(e) => setSearchColumn(e.target.value)}
                    className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500"
                  >
                    <option value="">Select column...</option>
                    {columns.map((col) => (
                      <option key={col} value={col}>
                        {col}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Search Value
                  </label>
                  <input
                    type="text"
                    value={searchValue}
                    onChange={(e) => setSearchValue(e.target.value)}
                    placeholder="Enter search term..."
                    className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
                <div className="flex items-end gap-2">
                  <button
                    onClick={handleSearch}
                    disabled={!searchColumn || !searchValue || loading}
                    className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white text-sm rounded-lg font-medium transition-colors"
                  >
                    Search
                  </button>
                  {appliedSearch && (
                    <button
                      onClick={handleClearSearch}
                      className="px-4 py-2 bg-gray-500 hover:bg-gray-600 text-white text-sm rounded-lg font-medium transition-colors"
                    >
                      Clear
                    </button>
                  )}
                </div>
              </div>
              {appliedSearch && (
                <div className="mt-2 text-xs text-gray-600 dark:text-gray-400">
                  Active filter: <strong>{appliedSearch.column}</strong>{" "}
                  contains "{appliedSearch.value}"
                </div>
              )}
            </div>
          )}

          {/* Selected table description */}
          {selectedTable && (
            <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
              <p className="text-sm text-gray-600 dark:text-gray-400">
                <strong className="text-gray-900 dark:text-white">
                  Description:
                </strong>{" "}
                {tables.find((t) => t.name === selectedTable)?.description}
              </p>
            </div>
          )}

          {/* Display row count */}
          {rowCount !== null && !error && (
            <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
              <div className="flex items-center gap-2">
                <svg
                  className="w-5 h-5 text-blue-600 dark:text-blue-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                <span className="text-blue-800 dark:text-blue-200 font-medium">
                  {appliedSearch ? "Filtered results: " : "Total rows: "}
                  <strong>{rowCount.toLocaleString()}</strong> (showing page{" "}
                  {currentPage} of {totalPages})
                </span>
              </div>
            </div>
          )}

          {/* Display error */}
          {error && (
            <div className="mt-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
              <div className="flex items-center gap-2">
                <svg
                  className="w-5 h-5 text-red-600 dark:text-red-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                <span className="text-red-800 dark:text-red-200 font-medium">
                  Error: {error}
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Table Data Display */}
        {tableData.length > 0 && (
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md overflow-hidden">
            <div className="p-6 border-b border-gray-200 dark:border-gray-700">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                {selectedTable} - Table Entries
              </h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 dark:bg-gray-700">
                  <tr>
                    {columns.map((col) => (
                      <th
                        key={col}
                        className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider whitespace-nowrap"
                      >
                        {col}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                  {tableData.map((row, idx) => (
                    <tr
                      key={idx}
                      className="hover:bg-gray-50 dark:hover:bg-gray-700/50"
                    >
                      {columns.map((col) => (
                        <td
                          key={col}
                          className="px-6 py-4 text-sm text-gray-900 dark:text-gray-300 whitespace-nowrap"
                        >
                          <div
                            className="max-w-xs truncate"
                            title={formatCellValue(row[col])}
                          >
                            {formatCellValue(row[col])}
                          </div>
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination Controls */}
            <div className="px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between">
              <div className="text-sm text-gray-600 dark:text-gray-400">
                Showing {(currentPage - 1) * rowLimit + 1} to{" "}
                {Math.min(currentPage * rowLimit, rowCount || 0)} of{" "}
                {rowCount?.toLocaleString()} results
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => fetchTableData(currentPage - 1, appliedSearch)}
                  disabled={currentPage === 1 || loading}
                  className="px-4 py-2 bg-gray-200 hover:bg-gray-300 disabled:bg-gray-100 disabled:text-gray-400 dark:bg-gray-700 dark:hover:bg-gray-600 dark:disabled:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-lg font-medium transition-colors flex items-center gap-2"
                >
                  <svg
                    className="w-4 h-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M15 19l-7-7 7-7"
                    />
                  </svg>
                  Previous
                </button>
                <span className="px-4 py-2 bg-indigo-100 dark:bg-indigo-900/20 text-indigo-600 dark:text-indigo-400 rounded-lg font-medium">
                  Page {currentPage} of {totalPages}
                </span>
                <button
                  onClick={() => fetchTableData(currentPage + 1, appliedSearch)}
                  disabled={currentPage === totalPages || loading}
                  className="px-4 py-2 bg-gray-200 hover:bg-gray-300 disabled:bg-gray-100 disabled:text-gray-400 dark:bg-gray-700 dark:hover:bg-gray-600 dark:disabled:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-lg font-medium transition-colors flex items-center gap-2"
                >
                  Next
                  <svg
                    className="w-4 h-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 5l7 7-7 7"
                    />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
