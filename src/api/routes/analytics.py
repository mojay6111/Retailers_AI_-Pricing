import pandas as pd
from fastapi import APIRouter
from pathlib import Path
from src.api.schemas import AnalyticsResponse, AnalyticsSummary, AnalyticsTopProduct

router = APIRouter(prefix="/analytics", tags=["analytics"])

PROCESSED_PATH = Path(__file__).resolve().parents[3] / "data" / "processed"

_products: pd.DataFrame = None
_recs: pd.DataFrame     = None


def _load():
    global _products, _recs
    if _products is None:
        _products = pd.read_parquet(PROCESSED_PATH / "product_features.parquet")
    if _recs is None:
        _recs = pd.read_parquet(PROCESSED_PATH / "price_recommendations.parquet")


@router.get("/", response_model=AnalyticsResponse)
def get_analytics():
    """Get full analytics summary including top products and elasticity breakdown."""
    _load()

    increase = _recs[_recs["action"].str.startswith("increase price")]
    estimated_uplift = (increase["total_revenue"] * increase["final_change_pct"] / 100).sum() * 12

    summary = AnalyticsSummary(
        total_products=len(_products),
        total_revenue=round(float(_products["total_revenue"].sum()), 2),
        products_with_increase=len(increase),
        estimated_annual_uplift=round(estimated_uplift, 2),
        avg_recommended_increase_pct=round(float(increase["final_change_pct"].mean()), 2),
        action_breakdown=_recs["action"].value_counts().to_dict(),
    )

    top_products = [
        AnalyticsTopProduct(
            stock_code=row["StockCode"],
            description=row["description"],
            total_revenue=round(float(row["total_revenue"]), 2),
            avg_unit_price=round(float(row["avg_unit_price"]), 2),
            total_quantity=int(row["total_quantity"]),
            num_customers=int(row["num_customers"]),
            revenue_rank=int(row["revenue_rank"]),
        )
        for _, row in _products.nsmallest(20, "revenue_rank").iterrows()
    ]

    elasticity_breakdown = _recs["elasticity_category"].value_counts().to_dict()

    return AnalyticsResponse(
        summary=summary,
        top_products=top_products,
        elasticity_breakdown=elasticity_breakdown,
    )