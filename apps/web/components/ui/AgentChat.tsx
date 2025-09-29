'use client';

import { useState, FormEvent } from 'react';
import ReactMarkdown from 'react-markdown';

export function AgentChat() {
  const [query, setQuery] = useState<string>('');
  const [response, setResponse] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!query.trim() || isLoading) return;

    setIsLoading(true);
    setResponse('');
    setError(null);

    try {
      // OLD: http://127.0.0.1:8000/query/rag
      // NEW:
      const res = await fetch('http://127.0.0.1:8000/agent/invoke', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      });

      if (!res.ok) {
        throw new Error(`API Error: ${res.statusText}`);
      }
     
      const data = await res.json();
      if (data.error) {
        throw new Error(data.error);
      }
      
    
      setResponse(data.response || "Agent did not provide a response.");

    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-slate-800 border border-slate-700 p-6 rounded-xl shadow-2xl max-w-2xl w-full mx-auto text-white">
      <h2 className="text-xl font-semibold mb-2">Ask the Logistics Coordinator</h2>
      <p className="text-slate-400 mb-6 text-sm">
        Query the RAG agent about recent logistics incidents.
      </p>
      
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="e.g., What happened on the I-405?"
          className="w-full p-3 bg-slate-700 border border-slate-600 rounded-md placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-shadow"
          disabled={isLoading}
        />
        <button
          type="submit"
          className="mt-4 w-full bg-blue-600 font-semibold p-3 rounded-md hover:bg-blue-700 transition-colors disabled:bg-slate-600 disabled:cursor-not-allowed"
          disabled={isLoading}
        >
          {isLoading ? 'Thinking...' : 'Ask Agent'}
        </button>
      </form>

      {/* Conditional rendering for error or response */}
      {(error || response) && (
        <div className="mt-6 border-t border-slate-700 pt-6">
          {error && (
            <div className="p-4 bg-red-900/50 text-red-300 border border-red-800 rounded-md">
              <h3 className="font-semibold">Error:</h3>
              <p className="mt-1 text-sm">{error}</p>
            </div>
          )}
          {response && (
            <div>
              <h3 className="font-semibold text-slate-300">Agent Response:</h3>
              <div className="mt-2 text-slate-200 prose prose-invert prose-p:text-slate-200">
                {/* Use ReactMarkdown to render the response */}
                <ReactMarkdown>{response}</ReactMarkdown>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}