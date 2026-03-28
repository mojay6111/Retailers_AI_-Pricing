import pandas as pd
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger(__name__)

RAW_PATH = Path(__file__).resolve().parents[2] / "data" / "raw" / "Online Retail.xlsx"
PROCESSED_PATH = Path(__file__).resolve().parents[2] / "data" / "processed"


def load_raw(path: Path = RAW_PATH) -> pd.DataFrame:
    log.info(f"Loading raw data from {path}")
    df = pd.read_excel(path, engine="openpyxl")
    log.info(f"Loaded {len(df):,} rows, {df.shape[1]} columns")
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    log.info("Cleaning data...")
    original_len = len(df)
    df = df.dropna(subset=["CustomerID", "Description"])
    df = df[~df["InvoiceNo"].astype(str).str.startswith("C")]
    df = df[df["Quantity"] > 0]
    df = df[df["UnitPrice"] > 0]
    price_cap = df.groupby("StockCode")["UnitPrice"].transform(lambda x: x.quantile(0.99))
    df = df[df["UnitPrice"] <= price_cap]
    df["CustomerID"] = df["CustomerID"].astype(int).astype(str)
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df["StockCode"] = df["StockCode"].astype(str).str.strip()
    df["Description"] = df["Description"].str.strip().str.lower()
    df["Revenue"] = df["Quantity"] * df["UnitPrice"]
    df["InvoiceMonth"] = df["InvoiceDate"].dt.to_period("M").astype(str)
    df["DayOfWeek"] = df["InvoiceDate"].dt.dayofweek
    df["Hour"] = df["InvoiceDate"].dt.hour
    log.info(f"Cleaned: {original_len:,} to {len(df):,} rows ({original_len - len(df):,} removed)")
    return df.reset_index(drop=True)


def build_product_features(df: pd.DataFrame) -> pd.DataFrame:
    log.info("Building product-level features...")
    features = (
        df.groupby("StockCode")
        .agg(
            description=("Description", "first"),
            total_revenue=("Revenue", "sum"),
            total_quantity=("Quantity", "sum"),
            avg_unit_price=("UnitPrice", "mean"),
            min_unit_price=("UnitPrice", "min"),
            max_unit_price=("UnitPrice", "max"),
            price_std=("UnitPrice", "std"),
            num_invoices=("InvoiceNo", "nunique"),
            num_customers=("CustomerID", "nunique"),
            num_countries=("Country", "nunique"),
        )
        .reset_index()
    )
    features["price_range"] = features["max_unit_price"] - features["min_unit_price"]
    features["price_cv"] = features["price_std"] / features["avg_unit_price"]
    features["revenue_per_customer"] = features["total_revenue"] / features["num_customers"]
    features["avg_qty_per_invoice"] = features["total_quantity"] / features["num_invoices"]
    features["revenue_rank"] = features["total_revenue"].rank(ascending=False, method="min").astype(int)
    log.info(f"Product features: {len(features):,} products, {features.shape[1]} features")
    return features


def build_monthly_features(df: pd.DataFrame) -> pd.DataFrame:
    log.info("Building monthly product features...")
    monthly = (
        df.groupby(["StockCode", "InvoiceMonth"])
        .agg(
            monthly_quantity=("Quantity", "sum"),
            monthly_revenue=("Revenue", "sum"),
            avg_price=("UnitPrice", "mean"),
            num_orders=("InvoiceNo", "nunique"),
            num_customers=("CustomerID", "nunique"),
        )
        .reset_index()
    )
    monthly = monthly.sort_values(["StockCode", "InvoiceMonth"])
    monthly["qty_lag1"] = monthly.groupby("StockCode")["monthly_quantity"].shift(1)
    monthly["qty_growth"] = (monthly["monthly_quantity"] - monthly["qty_lag1"]) / (monthly["qty_lag1"] + 1)
    log.info(f"Monthly features: {len(monthly):,} rows")
    return monthly


def run(save: bool = True) -> dict:
    df_raw = load_raw()
    df_clean = clean(df_raw)
    df_products = build_product_features(df_clean)
    df_monthly = build_monthly_features(df_clean)
    if save:
        PROCESSED_PATH.mkdir(parents=True, exist_ok=True)
        df_clean.to_parquet(PROCESSED_PATH / "transactions.parquet", index=False)
        df_products.to_parquet(PROCESSED_PATH / "product_features.parquet", index=False)
        df_monthly.to_parquet(PROCESSED_PATH / "monthly_features.parquet", index=False)
        log.info(f"Saved processed files to {PROCESSED_PATH}")
    return {"transactions": df_clean, "product_features": df_products, "monthly_features": df_monthly}


if __name__ == "__main__":
    data = run()
    print("\n=== Summary ===")
    print(f"Transactions : {len(data['transactions']):,} rows")
    print(f"Products     : {len(data['product_features']):,} unique products")
    print(f"Monthly rows : {len(data['monthly_features']):,} rows")
    print(f"\nSample product features:")
    print(data["product_features"].head(3).to_string())
