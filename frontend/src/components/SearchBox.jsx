import React from "react";
import { Search } from "lucide-react";

export default function SearchBox({ query, setQuery, onSearch, loading, k, setK }) {
  return (
    <div className="flex flex-col md:flex-row gap-3 items-start md:items-center">
      <div className="flex-1">
        <label className="block text-xs text-gray-600 mb-1">Hiring Query</label>
        <div className="flex">
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g., I need a 40-min Java + collaboration assessment..."
            className="flex-1 border rounded-l-lg px-4 py-2 focus:outline-none"
          />
          <button
            onClick={onSearch}
            disabled={loading}
            className="bg-indigo-600 text-white px-4 rounded-r-lg hover:bg-indigo-700 flex items-center gap-2"
          >
            <Search size={16} />
            {loading ? "Searching..." : "Search"}
          </button>
        </div>
      </div>

      <div>
        <label className="block text-xs text-gray-600 mb-1">Results (k)</label>
        <input
          type="number"
          min="1"
          max="10"
          value={k}
          onChange={(e) => setK(Math.max(1, Math.min(10, Number(e.target.value || 1))))}
          className="w-20 border rounded px-2 py-1"
        />
      </div>
    </div>
  );
}
