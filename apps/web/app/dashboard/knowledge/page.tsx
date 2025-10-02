"use client";

import { useState, useEffect } from "react";

const BROWSEABLE_TABLES = [
  "profiles",
  "orders",
  "shipments",
  "vehicles",
  "warehouses",
  "inventory",
  "packaging_types",
  "fuel_prices",
  "agent_audit_logs",
  "documents",
];

export default function KnowledgeBasePage() {
  const [selectedTable, setSelectedTable] = useState<string>(
    BROWSEABLE_TABLES[0]
  );
  const [tableData, setTableData] = useState<any[]>([]);
  const [totalRows, setTotalRows] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // --- New state for pagination ---
  const [currentPage, setCurrentPage] = useState(1);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  useEffect(() => {
    const fetchTableData = async () => {
      if (!selectedTable) return;

      setIsLoading(true);
      setError(null);

      // Calculate the offset for the API call
      const offset = (currentPage - 1) * rowsPerPage;

      try {
        const response = await fetch(
          `http://127.0.0.1:8000/browser/${selectedTable}?limit=${rowsPerPage}&offset=${offset}`
        );
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || "Failed to fetch table data.");
        }
        const { total, data } = await response.json();
        setTableData(data);
        setTotalRows(total);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchTableData();
  }, [selectedTable, currentPage, rowsPerPage]); // Re-fetch when table, page, or limit changes

  // Reset to page 1 when the table or rowsPerPage changes
  useEffect(() => {
    setCurrentPage(1);
  }, [selectedTable, rowsPerPage]);

  const headers = tableData.length > 0 ? Object.keys(tableData[0]) : [];
  const totalPages = Math.ceil(totalRows / rowsPerPage);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-800">Data Browser</h1>
        <p className="text-gray-500 mt-1">
          View the live data from the operational database tables.
        </p>
      </div>

      <div className="bg-white p-4 rounded-lg shadow-md flex justify-between items-center">
        <div>
          <label
            htmlFor="table-select"
            className="block text-sm font-medium text-gray-700 mb-2"
          >
            Select a table to view:
          </label>
          <select
            id="table-select"
            value={selectedTable}
            onChange={(e) => setSelectedTable(e.target.value)}
            className="p-2 border border-gray-300 rounded-md"
          >
            {BROWSEABLE_TABLES.map((tableName) => (
              <option key={tableName} value={tableName}>
                {tableName}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label
            htmlFor="rows-select"
            className="block text-sm font-medium text-gray-700 mb-2"
          >
            Rows per page:
          </label>
          <select
            id="rows-select"
            value={rowsPerPage}
            onChange={(e) => setRowsPerPage(Number(e.target.value))}
            className="p-2 border border-gray-300 rounded-md"
          >
            <option value={10}>10</option>
            <option value={25}>25</option>
            <option value={50}>50</option>
          </select>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-semibold mb-4 text-gray-700 capitalize">
          Entries for:{" "}
          <span className="font-mono text-blue-600">{selectedTable}</span>
        </h2>
        {isLoading && <p className="text-gray-500">Loading data...</p>}
        {error && <p className="text-red-500">Error: {error}</p>}

        {!isLoading && !error && (
          <div className="overflow-x-auto border rounded-lg">
            {tableData.length > 0 ? (
              <table className="min-w-full divide-y divide-gray-200 text-sm">
                <thead className="bg-gray-50">
                  {/* ... table headers ... */}
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {tableData.map((row, rowIndex) => (
                    <tr key={rowIndex}>
                      {headers.map((header) => (
                        <td
                          key={header}
                          className="px-4 py-2 whitespace-nowrap font-mono text-gray-600 max-w-xs truncate"
                        >
                          {String(row[header])}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p className="p-4 text-gray-500">
                No entries found in this table.
              </p>
            )}
          </div>
        )}

        {/* --- PAGINATION CONTROLS --- */}
        {!isLoading && totalRows > 0 && (
          <div className="flex justify-between items-center mt-4">
            <span className="text-sm text-gray-600">
              Showing {(currentPage - 1) * rowsPerPage + 1}-
              {Math.min(currentPage * rowsPerPage, totalRows)} of {totalRows}
            </span>
            <div className="flex gap-2">
              <button
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="px-3 py-1 border rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>
              <span className="self-center">
                Page {currentPage} of {totalPages}
              </span>
              <button
                onClick={() =>
                  setCurrentPage((p) => Math.min(totalPages, p + 1))
                }
                disabled={currentPage === totalPages}
                className="px-3 py-1 border rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
