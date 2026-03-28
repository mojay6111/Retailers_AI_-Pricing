const ACTION_STYLES = {
  "increase price (rule-based)": "bg-emerald-100 text-emerald-700",
  "increase price (medium confidence)": "bg-green-100 text-green-700",
  "small increase — elastic": "bg-sky-100 text-sky-700",
  "hold — elastic": "bg-slate-100 text-slate-600",
  "hold — price sensitive": "bg-red-100 text-red-600",
  "hold — low confidence": "bg-slate-100 text-slate-500",
  "manual review": "bg-amber-100 text-amber-700",
};

const fmt = (n) => `£${Number(n).toFixed(2)}`;

export default function RecommendationsTable({ recs, filter, onFilterChange }) {
  if (!recs) return null;

  const filtered = filter
    ? recs.filter((r) => r.action.includes(filter))
    : recs;

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-5">
      <div className="flex items-center justify-between mb-4 flex-wrap gap-2">
        <h2 className="text-slate-700 font-semibold text-base">
          Pricing recommendations
          <span className="ml-2 text-slate-400 font-normal text-sm">
            ({filtered.length} products)
          </span>
        </h2>
        <select
          className="border border-slate-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-sky-400"
          value={filter}
          onChange={(e) => onFilterChange(e.target.value)}
        >
          <option value="">All actions</option>
          <option value="increase price">Price increases only</option>
          <option value="hold — price sensitive">Hold — price sensitive</option>
          <option value="manual review">Manual review</option>
        </select>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-100">
              <th className="text-left py-2 px-3 text-slate-500 font-medium">
                SKU
              </th>
              <th className="text-left py-2 px-3 text-slate-500 font-medium">
                Product
              </th>
              <th className="text-right py-2 px-3 text-slate-500 font-medium">
                Current £
              </th>
              <th className="text-right py-2 px-3 text-slate-500 font-medium">
                Recommended £
              </th>
              <th className="text-right py-2 px-3 text-slate-500 font-medium">
                Change
              </th>
              <th className="text-left py-2 px-3 text-slate-500 font-medium">
                Action
              </th>
              <th className="text-right py-2 px-3 text-slate-500 font-medium">
                Revenue £
              </th>
            </tr>
          </thead>
          <tbody>
            {filtered.slice(0, 50).map((r) => (
              <tr
                key={r.stock_code}
                className="border-b border-slate-50 hover:bg-slate-50 transition-colors"
              >
                <td className="py-2.5 px-3 font-mono text-sky-600 font-medium">
                  {r.stock_code}
                </td>
                <td className="py-2.5 px-3 text-slate-700 max-w-[200px] truncate">
                  {r.description}
                </td>
                <td className="py-2.5 px-3 text-right text-slate-600">
                  {fmt(r.current_price)}
                </td>
                <td className="py-2.5 px-3 text-right font-medium text-slate-800">
                  {fmt(r.recommended_price)}
                </td>
                <td
                  className={`py-2.5 px-3 text-right font-medium ${r.price_change_pct > 0 ? "text-emerald-600" : "text-slate-400"}`}
                >
                  {r.price_change_pct > 0 ? `+${r.price_change_pct}%` : "—"}
                </td>
                <td className="py-2.5 px-3">
                  <span
                    className={`px-2 py-1 rounded-lg text-xs font-medium ${ACTION_STYLES[r.action] || "bg-slate-100 text-slate-500"}`}
                  >
                    {r.action}
                  </span>
                </td>
                <td className="py-2.5 px-3 text-right text-slate-600">
                  £
                  {Number(r.total_revenue).toLocaleString("en-GB", {
                    maximumFractionDigits: 0,
                  })}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
