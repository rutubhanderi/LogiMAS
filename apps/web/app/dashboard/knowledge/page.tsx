'use client';

import { useState, useEffect } from 'react';

// List of tables that are available for browsing
const BROWSEABLE_TABLES = [
  "profiles", "orders", "shipments", "vehicles", "warehouses", 
  "inventory", "packaging_types", "fuel_prices", "agent_audit_logs", "documents"
];

const ROWS_PER_PAGE_OPTIONS = [10, 25, 50];

export default function KnowledgeBasePage() {
  const [selectedTable, setSelectedTable] = useState<string>(BROWSEABLE_TABLES[0]);
  const [tableData, setTableData] = useState<any[]>([]);
  const [totalRows, setTotalRows] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // State for pagination
  const [currentPage, setCurrentPage] = useState(1);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  // Effect to fetch data from the backend whenever a dependency changes
  useEffect(() => {
    const fetchTableData = async () => {
      if (!selectedTable) return;

      setIsLoading(true);
      setError(null);

      const offset = (currentPage - 1) * rowsPerPage;

      try {
        const response = await fetch(`http://127.0.0.1:8000/browser/${selectedTable}?limit=${rowsPerPage}&offset=${offset}`);
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
  }, [selectedTable, currentPage, rowsPerPage]);

  // Effect to reset the page number when the table or rows per page is changed
  useEffect(() => {
    setCurrentPage(1);
  }, [selectedTable, rowsPerPage]);

  const headers = tableData.length > 0 ? Object.keys(tableData[0]) : [];
  const totalPages = Math.ceil(totalRows / rowsPerPage);

  // SVG for the custom dropdown arrow, URL-encoded for use in CSS
  const customArrow = `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e")`;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold text-slate-900">Data Browser</h1>
        <p className="text-lg text-slate-600 mt-1">
          View the live data from the operational database tables.
        </p>
      </div>

      {/* Control Panel Card */}
      <div className="bg-white p-6 rounded-xl shadow-lg flex flex-col sm:flex-row justify-between items-center gap-6">
        <div className="flex items-center gap-4">
          <label htmlFor="table-select" className="text-base font-semibold text-slate-800 shrink-0">
            Select a table:
          </label>
          <div className="relative">
            <select
              id="table-select"
              value={selectedTable}
              onChange={(e) => setSelectedTable(e.target.value)}
              className="w-64 appearance-none bg-white border border-slate-300 text-slate-800 font-mono text-base rounded-lg focus:ring-blue-500 focus:border-blue-500 block p-3 pr-10"
              style={{ backgroundImage: customArrow, backgroundRepeat: 'no-repeat', backgroundPosition: 'right 0.7rem center', backgroundSize: '1.5em 1.5em' }}
            >
              {BROWSEABLE_TABLES.map((tableName) => (
                <option key={tableName} value={tableName}>{tableName}</option>
              ))}
            </select>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <label htmlFor="rows-select" className="text-base font-semibold text-slate-800">
            Rows per page:
          </label>
          <div className="relative">
            <select
              id="rows-select"
              value={rowsPerPage}
              onChange={(e) => setRowsPerPage(Number(e.target.value))}
              className="w-32 appearance-none bg-white border border-slate-300 text-slate-800 text-base rounded-lg focus:ring-blue-500 focus:border-blue-500 block p-3 pr-10"
              style={{ backgroundImage: customArrow, backgroundRepeat: 'no-repeat', backgroundPosition: 'right 0.7rem center', backgroundSize: '1.5em 1.5em' }}
            >
              {ROWS_PER_PAGE_OPTIONS.map((num) => (
                <option key={num} value={num}>{num}</option>
              ))}
            </select>
          </div>
        </div>
      </div>
      
      {/* Data Table Card */}
      <div className="bg-white p-8 rounded-xl shadow-lg">
        <h2 className="text-2xl font-bold text-slate-800 mb-4 capitalize">
          Entries For: <span className="font-mono text-blue-600">{selectedTable}</span>
        </h2>
        
        {isLoading && <p className="text-slate-500 py-8 text-center">Loading data...</p>}
        {error && <p className="text-red-500 py-8 text-center">Error: {error}</p>}
        
        {!isLoading && !error && (
          <div className="overflow-x-auto border border-slate-200 rounded-lg">
            {tableData.length > 0 ? (
              <table className="min-w-full divide-y divide-slate-200 text-base">
                <thead className="bg-slate-50">
                  <tr>
                    {headers.map(header => (
                      <th key={header} className="px-6 py-4 text-left text-sm font-semibold text-slate-600 uppercase tracking-wider">
                        {header.replace(/_/g, ' ')}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-slate-200">
                  {tableData.map((row, rowIndex) => (
                    <tr key={rowIndex} className="hover:bg-slate-50">
                      {headers.map(header => (
                        <td key={header} className="px-6 py-4 whitespace-nowrap font-mono text-slate-700 max-w-sm truncate" title={String(row[header])}>
                          {String(row[header])}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p className="p-8 text-center text-slate-500">No entries found for this table.</p>
            )}
          </div>
        )}

        {/* Pagination Controls */}
        {!isLoading && totalRows > rowsPerPage && (
          <div className="flex justify-between items-center mt-6">
            <span className="text-base text-slate-600">
              Showing <span className="font-semibold">{(currentPage - 1) * rowsPerPage + 1}</span>-
              <span className="font-semibold">{Math.min(currentPage * rowsPerPage, totalRows)}</span> of <span className="font-semibold">{totalRows}</span>
            </span>
            <div className="flex gap-2">
              <button onClick={() => setCurrentPage(p => p - 1)} disabled={currentPage === 1}
                className="px-4 py-2 border rounded-lg bg-white hover:bg-slate-100 disabled:opacity-50 disabled:cursor-not-allowed">
                Previous
              </button>
              <span className="self-center px-2 text-slate-600">Page {currentPage} of {totalPages}</span>
              <button onClick={() => setCurrentPage(p => p + 1)} disabled={currentPage === totalPages}
                className="px-4 py-2 border rounded-lg bg-white hover:bg-slate-100 disabled:opacity-50 disabled:cursor-not-allowed">
                Next
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}