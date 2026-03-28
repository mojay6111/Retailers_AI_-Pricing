import pandas as pd
import numpy as np
import logging
from pathlib import Path
from scipy import stats

log = logging.getLogger(__name__)

PROCESSED_PATH = Path(__file__).resolve().parents[2] / "data" / "processed"


def estimate(monthly: pd.DataFrame, products: pd.DataFrame, min_months: int = 4, min_cv: float = 0.01) -> pd.DataFrame:
    """
    Estimate price elasticity per product via log-log OLS regression.
    Returns a DataFrame with elasticity, r_squared, p_value per product.
    """
    log.info("Filtering products eligible for elasticity estimation...")

    monthly_stats = monthly.groupby("StockCode").agg(
        n_months=("InvoiceMonth", "count"),
        price_std=("avg_price", "std"),
        price_mean=("avg_price", "mean")
    ).reset_index()
    monthly_stats["price_cv"] = monthly_stats["price_std"] / monthly_stats["price_mean"]

    eligible = monthly_stats[
        (monthly_stats["n_months"] >= min_months) &
        (monthly_stats["price_cv"] > min_cv)
    ]["StockCode"].tolist()

    log.info(f"Eligible products: {len(eligible):,} of {len(monthly_stats):,}")

    results = []
    for sku in eligible:
        sub = monthly[monthly["StockCode"] == sku].copy()
        sub = sub[sub["avg_price"] > 0]
        if len(sub) < 4:
            continue

        log_price = np.log(sub["avg_price"])
        log_qty   = np.log(sub["monthly_quantity"] + 1)

        if log_price.std() < 1e-6:
            continue

        slope, intercept, r, p_value, se = stats.linregress(log_price, log_qty)

        results.append({
            "StockCode":  sku,
            "elasticity": round(slope, 4),
            "r_squared":  round(r ** 2, 4),
            "p_value":    round(p_value, 4),
            "n_months":   len(sub),
            "avg_price":  sub["avg_price"].mean().round(2),
            "price_cv":   sub["avg_price"].std() / sub["avg_price"].mean(),
        })

    elasticity_df = pd.DataFrame(results)
    elasticity_df = elasticity_df.merge(
        products[["StockCode", "description", "total_revenue", "revenue_rank"]],
        on="StockCode", how="left"
    )
    elasticity_df["category"] = elasticity_df["elasticity"].apply(_classify)
    elasticity_df["confidence"] = pd.cut(
        elasticity_df["p_value"],
        bins=[0, 0.05, 0.20, 1.0],
        labels=["high", "medium", "low"]
    ).astype(str)

    log.info(f"Elasticity estimated for {len(elasticity_df):,} products")
    log.info(f"Category breakdown:\n{elasticity_df['category'].value_counts().to_string()}")

    return elasticity_df


def _classify(e: float) -> str:
    if e < -1.5:  return "highly elastic"
    elif e < -0.5: return "elastic"
    elif e < 0:    return "inelastic"
    else:          return "unusual"


def run(save_output: bool = True) -> pd.DataFrame:
    """Full elasticity estimation pipeline."""
    monthly  = pd.read_parquet(PROCESSED_PATH / "monthly_features.parquet")
    products = pd.read_parquet(PROCESSED_PATH / "product_features.parquet")

    elasticity_df = estimate(monthly, products)

    if save_output:
        elasticity_df.to_parquet(PROCESSED_PATH / "elasticity.parquet", index=False)
        log.info(f"Saved elasticity.parquet — {len(elasticity_df):,} products")

    return elasticity_df


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    df = run()
    print(f"\nElasticity shape: {df.shape}")
    print(df["category"].value_counts())
    print(df.head())