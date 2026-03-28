import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

export default function ForecastChart({ data, sku }) {
  if (!data || data.length === 0) return null;

  const chartData = data.map((d) => ({
    month: d.invoice_month,
    Actual: d.actual_quantity,
    Predicted: Math.round(d.predicted_quantity),
  }));

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-5">
      <h2 className="text-slate-700 font-semibold text-base mb-1">
        Demand forecast — <span className="text-sky-600">{sku}</span>
      </h2>
      <p className="text-slate-400 text-xs mb-4">
        Monthly actual vs predicted quantity
      </p>
      <ResponsiveContainer width="100%" height={240}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
          <XAxis dataKey="month" tick={{ fontSize: 11 }} />
          <YAxis tick={{ fontSize: 11 }} />
          <Tooltip />
          <Legend />
          <Line
            type="monotone"
            dataKey="Actual"
            stroke="#0ea5e9"
            strokeWidth={2}
            dot={{ r: 3 }}
          />
          <Line
            type="monotone"
            dataKey="Predicted"
            stroke="#f97316"
            strokeWidth={2}
            strokeDasharray="5 5"
            dot={{ r: 3 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
