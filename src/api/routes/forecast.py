import pandas as pd
from fastapi import APIRouter, HTTPException
from pathlib import Path
from src.api.schemas import ForecastRequest, ForecastResponse

router = APIRouter(prefix="/forecast", tags=["forecasting"])

PROCESSED_PATH = Path(__file__).resolve().parents[3] / "data" / "processed"

_demand: pd.DataFrame = None


def _load() -> pd.DataFrame:
    global _demand
    if _demand is None:
        _demand = pd.read_parquet(PROCESSED_PATH / "demand_predictions.parquet")
    return _demand


@router.get("/{stock_code}", response_model=list[ForecastResponse])
def get_forecast(stock_code: str):
    """Get all demand forecast data for a product SKU."""
    df = _load()
    rows = df[df["StockCode"].str.upper() == stock_code.upper()]

    if rows.empty:
        raise HTTPException(status_code=404, detail=f"SKU '{stock_code}' not found")

    return [
        ForecastResponse(
            stock_code=row["StockCode"],
            invoice_month=row["InvoiceMonth"],
            actual_quantity=float(row["monthly_quantity"]) if pd.notna(row["monthly_quantity"]) else None,
            predicted_quantity=round(float(row["predicted_quantity"]), 1),
            avg_price=round(float(row["avg_price"]), 2),
        )
        for _, row in rows.iterrows()
    ]


@router.get("/", response_model=list[ForecastResponse])
def get_latest_forecasts(limit: int = 50):
    """Get latest month demand forecasts for all products."""
    df = _load()
    latest = df[df["InvoiceMonth"] == df["InvoiceMonth"].max()].head(limit)

    return [
        ForecastResponse(
            stock_code=row["StockCode"],
            invoice_month=row["InvoiceMonth"],
            actual_quantity=float(row["monthly_quantity"]) if pd.notna(row["monthly_quantity"]) else None,
            predicted_quantity=round(float(row["predicted_quantity"]), 1),
            avg_price=round(float(row["avg_price"]), 2),
        )
        for _, row in latest.iterrows()
    ]