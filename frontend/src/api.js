const BASE = "http://localhost:8001";

export async function fetchHealth() {
  const r = await fetch(`${BASE}/health`);
  return r.json();
}

export async function fetchAnalytics() {
  const r = await fetch(`${BASE}/analytics/`);
  return r.json();
}

export async function fetchRecommendations(action = "", limit = 100) {
  const params = new URLSearchParams();
  if (action) params.append("action", action);
  params.append("limit", limit);
  const r = await fetch(`${BASE}/price/?${params}`);
  return r.json();
}

export async function fetchSKU(sku) {
  const r = await fetch(`${BASE}/price/${sku}`);
  if (!r.ok) throw new Error("SKU not found");
  return r.json();
}

export async function fetchForecast(sku) {
  const r = await fetch(`${BASE}/forecast/${sku}`);
  if (!r.ok) throw new Error("Forecast not found");
  return r.json();
}
