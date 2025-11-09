import React, { useState } from "react";
import SearchBox from "./components/SearchBox";
import ResultsTable from "./components/ResultsTable";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export default function App() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [k, setK] = useState(5);
  const [error, setError] = useState("");

  async function handleSearch(q) {
    setError("");
    setLoading(true);
    setResults([]);
    try {
      const resp = await fetch(`${API_BASE}/recommend`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: q, k })
      });
      if (!resp.ok) {
        const txt = await resp.text();
        throw new Error(`Server error: ${resp.status} ${txt}`);
      }
      const data = await resp.json();
      setResults(data.recommendations || []);
    } catch (err) {
      console.error(err);
      setError(err.message || "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto bg-white p-6 rounded-2xl shadow">
        <h1 className="text-2xl font-semibold mb-2">SHL Assessment Recommender</h1>
        <p className="text-sm text-gray-600 mb-4">
          Type your hiring requirement query and get recommended SHL assessments with links.
        </p>

        <SearchBox
          query={query}
          setQuery={setQuery}
          k={k}
          setK={setK}
          onSearch={() => {
            if (!query.trim()) {
              setError("Please enter a query");
              return;
            }
            handleSearch(query);
          }}
          loading={loading}
        />

        {error && <div className="mt-4 text-red-600">{error}</div>}

        <ResultsTable results={results} loading={loading} />

        <div className="mt-6 text-sm text-gray-500">
          Tip: Use the example queries from your dataset to test. You can run the backend locally
          (uvicorn main:app --reload) and use this frontend to call it.
        </div>
      </div>
    </div>
  );
}
