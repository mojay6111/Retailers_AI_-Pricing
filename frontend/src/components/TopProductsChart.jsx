import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

const fmt = (n) => `£${(n / 1000).toFixed(0)}k`;

export default function TopProductsChart({ products }) {
  if (!products) return null;

  const data = products
    .slice(0, 10)
    .map((p) => ({
      name: p.description.slice(0, 22),
      revenue: p.total_revenue,
    }))
    .reverse();

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-5">
      <h2 className="text-slate-700 font-semibold text-base mb-4">
        Top 10 products by revenue
      </h2>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart
          data={data}
          layout="vertical"
          margin={{ left: 10, right: 30 }}
        >
          <XAxis type="number" tickFormatter={fmt} tick={{ fontSize: 11 }} />
          <YAxis
            type="category"
            dataKey="name"
            width={150}
            tick={{ fontSize: 11 }}
          />
          <Tooltip formatter={(v) => [`£${v.toLocaleString()}`, "Revenue"]} />
          <Bar dataKey="revenue" radius={[0, 6, 6, 0]}>
            {data.map((_, i) => (
              <Cell
                key={i}
                fill={i === data.length - 1 ? "#0ea5e9" : "#bae6fd"}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
