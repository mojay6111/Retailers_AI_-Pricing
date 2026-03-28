import { useEffect, useState } from "react";
import { fetchHealth, fetchAnalytics, fetchRecommendations } from "./api";
import NavBar from "./components/NavBar";
import SummaryCards from "./components/SummaryCards";
import ElasticityChart from "./components/ElasticityChart";
import TopProductsChart from "./components/TopProductsChart";
import ForecastChart from "./components/ForecastChart";
import RecommendationsTable from "./components/RecommendationsTable";
import SKUSearch from "./components/SKUSearch";

export default function App() {
  const [apiStatus, setApiStatus] = useState("checking");
  const [analytics, setAnalytics] = useState(null);
  const [recs, setRecs] = useState(null);
  const [filter, setFilter] = useState("");
  const [skuResult, setSkuResult] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const health = await fetchHealth();
        setApiStatus(health.status);
        const [analyticsData, recsData] = await Promise.all([
          fetchAnalytics(),
          fetchRecommendations("", 200),
        ]);
        setAnalytics(analyticsData);
        setRecs(recsData);
      } catch {
        setApiStatus("offline");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  return (
    <div className="min-h-screen bg-slate-50">
      <NavBar apiStatus={apiStatus} />

      {apiStatus === "offline" && (
        <div className="bg-red-50 border-b border-red-200 px-6 py-3 text-red-700 text-sm text-center">
          API is offline. Start the server with:{" "}
          <code className="font-mono bg-red-100 px-1 rounded">
            uvicorn app:app --reload --port 8001
          </code>
        </div>
      )}

      <main className="max-w-7xl mx-auto px-4 py-6 space-y-6">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="w-10 h-10 border-4 border-sky-500 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
              <p className="text-slate-500 text-sm">Loading pricing data...</p>
            </div>
          </div>
        ) : (
          <>
            {/* Summary cards */}
            <SummaryCards summary={analytics?.summary} />

            {/* Charts row */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <ElasticityChart breakdown={analytics?.elasticity_breakdown} />
              <TopProductsChart products={analytics?.top_products} />
            </div>

            {/* SKU search + forecast */}
            <SKUSearch onResult={setSkuResult} />

            {skuResult && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* SKU recommendation card */}
                <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-5">
                  <h2 className="text-slate-700 font-semibold text-base mb-4">
                    Recommendation —{" "}
                    <span className="text-sky-600">{skuResult.sku}</span>
                  </h2>
                  <div className="space-y-3">
                    <div className="flex justify-between py-2 border-b border-slate-50">
                      <span className="text-slate-500 text-sm">Product</span>
                      <span className="text-slate-800 text-sm font-medium capitalize">
                        {skuResult.rec.description}
                      </span>
                    </div>
                    <div className="flex justify-between py-2 border-b border-slate-50">
                      <span className="text-slate-500 text-sm">
                        Current price
                      </span>
                      <span className="text-slate-800 text-sm font-medium">
                        £{skuResult.rec.current_price}
                      </span>
                    </div>
                    <div className="flex justify-between py-2 border-b border-slate-50">
                      <span className="text-slate-500 text-sm">
                        Recommended price
                      </span>
                      <span className="text-emerald-600 text-sm font-bold">
                        £{skuResult.rec.recommended_price}
                      </span>
                    </div>
                    <div className="flex justify-between py-2 border-b border-slate-50">
                      <span className="text-slate-500 text-sm">Change</span>
                      <span
                        className={`text-sm font-medium ${skuResult.rec.price_change_pct > 0 ? "text-emerald-600" : "text-slate-400"}`}
                      >
                        {skuResult.rec.price_change_pct > 0
                          ? `+${skuResult.rec.price_change_pct}%`
                          : "No change"}
                      </span>
                    </div>
                    <div className="flex justify-between py-2 border-b border-slate-50">
                      <span className="text-slate-500 text-sm">Elasticity</span>
                      <span className="text-slate-800 text-sm">
                        {skuResult.rec.elasticity} (
                        {skuResult.rec.elasticity_category})
                      </span>
                    </div>
                    <div className="flex justify-between py-2 border-b border-slate-50">
                      <span className="text-slate-500 text-sm">Confidence</span>
                      <span className="text-slate-800 text-sm capitalize">
                        {skuResult.rec.confidence}
                      </span>
                    </div>
                    <div className="flex justify-between py-2">
                      <span className="text-slate-500 text-sm">Action</span>
                      <span className="text-sky-700 text-sm font-medium">
                        {skuResult.rec.action}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Forecast chart */}
                <ForecastChart data={skuResult.forecast} sku={skuResult.sku} />
              </div>
            )}

            {/* Recommendations table */}
            <RecommendationsTable
              recs={recs}
              filter={filter}
              onFilterChange={setFilter}
            />
          </>
        )}
      </main>
    </div>
  );
}
