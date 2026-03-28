import pandas as pd
from fastapi import APIRouter, HTTPException
from pathlib import Path
from src.api.schemas import PriceRecommendation

router = APIRouter(prefix="/price", tags=["pricing"])

PROCESSED_PATH = Path(__file__).resolve().parents[3] / "data" / "processed"

_recs: pd.DataFrame = None


def _load() -> pd.DataFrame:
    global _recs
    if _recs is None:
        _recs = pd.read_parquet(PROCESSED_PATH / "price_recommendations.parquet")
    return _recs


@router.get("/{stock_code}", response_model=PriceRecommendation)
def get_price_recommendation(stock_code: str):
    """Get pricing recommendation for a single product SKU."""
    df = _load()
    row = df[df["StockCode"].str.upper() == stock_code.upper()]

    if row.empty:
        raise HTTPException(status_code=404, detail=f"SKU '{stock_code}' not found")

    row = row.iloc[0]
    return PriceRecommendation(
        stock_code=row["StockCode"],
        description=row["description"],
        elasticity_category=row["elasticity_category"],
        confidence=row["confidence"],
        current_price=round(float(row["current_price"]), 2),
        recommended_price=round(float(row["recommended_price"]), 2),
        price_change_pct=round(float(row["final_change_pct"]), 2),
        action=row["action"],
        elasticity=round(float(row["elasticity"]), 4),
        p_value=round(float(row["p_value"]), 4),
        r_squared=round(float(row["r_squared"]), 4),
        total_revenue=round(float(row["total_revenue"]), 2),
    )


@router.get("/", response_model=list[PriceRecommendation])
def get_all_recommendations(
    action: str = None,
    min_revenue: float = None,
    limit: int = 50
):
    """Get all pricing recommendations with optional filters."""
    df = _load()

    if action:
        df = df[df["action"].str.contains(action, case=False)]
    if min_revenue:
        df = df[df["total_revenue"] >= min_revenue]

    df = df.head(limit)

    return [
        PriceRecommendation(
            stock_code=row["StockCode"],
            description=row["description"],
            elasticity_category=row["elasticity_category"],
            confidence=row["confidence"],
            current_price=round(float(row["current_price"]), 2),
            recommended_price=round(float(row["recommended_price"]), 2),
            price_change_pct=round(float(row["final_change_pct"]), 2),
            action=row["action"],
            elasticity=round(float(row["elasticity"]), 4),
            p_value=round(float(row["p_value"]), 4),
            r_squared=round(float(row["r_squared"]), 4),
            total_revenue=round(float(row["total_revenue"]), 2),
        )
        for _, row in df.iterrows()
    ]