import React from "react";

export default function ResultsTable({ results, loading }) {
  if (loading) {
    return <div className="mt-6">Loading results...</div>;
  }
  if (!results || results.length === 0) {
    return <div className="mt-6 text-gray-500">No results yet. Try a query above.</div>;
  }
  return (
    <div className="mt-6">
      <table className="w-full table-auto border-collapse">
        <thead>
          <tr className="text-left">
            <th className="border-b py-2">#</th>
            <th className="border-b py-2">Assessment</th>
            <th className="border-b py-2">Type</th>
            <th className="border-b py-2">Score</th>
            <th className="border-b py-2">Link</th>
          </tr>
        </thead>
        <tbody>
          {results.map((r, i) => (
            <tr key={`${r.url}-${i}`} className="align-top">
              <td className="py-2">{i + 1}</td>
              <td className="py-2 font-medium">{r.assessment_name}</td>
              <td className="py-2">{r.test_type || "-"}</td>
              <td className="py-2">{(r.score || 0).toFixed(3)}</td>
              <td className="py-2">
                <a className="text-indigo-600 hover:underline" href={r.url} target="_blank" rel="noreferrer">
                  Open
                </a>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
