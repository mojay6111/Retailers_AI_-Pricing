function Card({ title, value, subtitle, color }) {
  const colors = {
    blue: "from-sky-500 to-sky-600",
    green: "from-emerald-500 to-emerald-600",
    amber: "from-amber-500 to-amber-600",
    purple: "from-purple-500 to-purple-600",
  };
  return (
    <div
      className={`bg-gradient-to-br ${colors[color]} rounded-2xl p-5 text-white shadow-md`}
    >
      <p className="text-sm font-medium opacity-80 mb-1">{title}</p>
      <p className="text-3xl font-bold tracking-tight">{value}</p>
      {subtitle && <p className="text-xs opacity-70 mt-1">{subtitle}</p>}
    </div>
  );
}

export default function SummaryCards({ summary }) {
  if (!summary) return null;

  const fmt = (n) =>
    new Intl.NumberFormat("en-GB", {
      style: "currency",
      currency: "GBP",
      maximumFractionDigits: 0,
    }).format(n);

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <Card
        title="Total Products"
        value={summary.total_products.toLocaleString()}
        subtitle="unique SKUs analysed"
        color="blue"
      />
      <Card
        title="Total Revenue"
        value={fmt(summary.total_revenue)}
        subtitle="Dec 2010 — Dec 2011"
        color="purple"
      />
      <Card
        title="Price Increases"
        value={summary.products_with_increase}
        subtitle="products recommended"
        color="amber"
      />
      <Card
        title="Est. Annual Uplift"
        value={fmt(summary.estimated_annual_uplift)}
        subtitle={`avg +${summary.avg_recommended_increase_pct}% per product`}
        color="green"
      />
    </div>
  );
}
