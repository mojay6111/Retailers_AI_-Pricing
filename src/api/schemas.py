from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ── Request schemas ────────────────────────────────────────────────────────────

class ForecastRequest(BaseModel):
    stock_code: str = Field(..., example="85123A", description="Product SKU")
    months_ahead: int = Field(1, ge=1, le=12, description="How many months to forecast")


# ── Response schemas ───────────────────────────────────────────────────────────

class PriceRecommendation(BaseModel):
    stock_code: str
    description: str
    elasticity_category: str
    confidence: str
    current_price: float
    recommended_price: float
    price_change_pct: float
    action: str
    elasticity: float
    p_value: float
    r_squared: float
    total_revenue: float


class ForecastResponse(BaseModel):
    stock_code: str
    invoice_month: str
    actual_quantity: Optional[float] = None
    predicted_quantity: float
    avg_price: float


class AnalyticsSummary(BaseModel):
    total_products: int
    total_revenue: float
    products_with_increase: int
    estimated_annual_uplift: float
    avg_recommended_increase_pct: float
    action_breakdown: dict


class AnalyticsTopProduct(BaseModel):
    stock_code: str
    description: str
    total_revenue: float
    avg_unit_price: float
    total_quantity: int
    num_customers: int
    revenue_rank: int


class AnalyticsResponse(BaseModel):
    summary: AnalyticsSummary
    top_products: list[AnalyticsTopProduct]
    elasticity_breakdown: dict


# ── Health check ───────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    models_loaded: bool
    products_loaded: int