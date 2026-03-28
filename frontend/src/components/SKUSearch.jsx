import { useState } from "react";
import { fetchSKU, fetchForecast } from "../api";

export default function SKUSearch({ onResult }) {
  const [sku, setSku] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const search = async () => {
    if (!sku.trim()) return;
    setLoading(true);
    setError("");
    try {
      const [rec, forecast] = await Promise.all([
        fetchSKU(sku.trim().toUpperCase()),
        fetchForecast(sku.trim().toUpperCase()),
      ]);
      onResult({ rec, forecast, sku: sku.trim().toUpperCase() });
    } catch {
      setError("SKU not found. Try: 85123A, 22178, 22697");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-5">
      <h2 className="text-slate-700 font-semibold text-base mb-3">
        Search product by SKU
      </h2>
      <div className="flex gap-2">
        <input
          className="flex-1 border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-sky-400"
          placeholder="e.g. 85123A, 22178, 22697..."
          value={sku}
          onChange={(e) => setSku(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && search()}
        />
        <button
          onClick={search}
          disabled={loading}
          className="bg-sky-600 hover:bg-sky-700 text-white px-5 py-2.5 rounded-xl text-sm font-medium transition-colors disabled:opacity-50"
        >
          {loading ? "Searching..." : "Search"}
        </button>
      </div>
      {error && <p className="text-red-500 text-xs mt-2">{error}</p>}
    </div>
  );
}
