import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

const COLORS = {
  "highly elastic": "#ef4444",
  elastic: "#f97316",
  inelastic: "#22c55e",
  unusual: "#94a3b8",
};

export default function ElasticityChart({ breakdown }) {
  if (!breakdown) return null;

  const data = Object.entries(breakdown).map(([name, value]) => ({
    name,
    value,
  }));

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-5">
      <h2 className="text-slate-700 font-semibold text-base mb-4">
        Elasticity breakdown
      </h2>
      <ResponsiveContainer width="100%" height={240}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={90}
            paddingAngle={3}
            dataKey="value"
          >
            {data.map((entry) => (
              <Cell key={entry.name} fill={COLORS[entry.name] || "#94a3b8"} />
            ))}
          </Pie>
          <Tooltip formatter={(v, n) => [v.toLocaleString(), n]} />
          <Legend iconType="circle" iconSize={10} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
