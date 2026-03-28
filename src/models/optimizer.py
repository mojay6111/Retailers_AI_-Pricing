import pandas as pd
import numpy as np
import logging
from pathlib import Path

log = logging.getLogger(__name__)

PROCESSED_PATH = Path(__file__).resolve().parents[2] / "data" / "processed"


def _optimise_row(row: pd.Series, price_floor: float = 0.5, price_ceiling: float = 2.5) -> pd.Series:
    """Sweep a price grid and return the revenue-maximising price."""
    e  = row["elasticity"]
    p0 = row["current_price"]
    q0 = max(row["predicted_qty"], 1)

    prices     = np.linspace(p0 * price_floor, p0 * price_ceiling, 100)
    quantities = np.maximum(q0 * (prices / p0) ** e, 0)
    revenues   = prices * quantities
    best       = np.argmax(revenues)

    return pd.Series({
        "optimal_price"  : round(prices[best], 2),
        "optimal_revenue": round(revenues[best], 2),
        "current_revenue": round(p0 * q0, 2),
        "raw_change_pct" : round((prices[best] - p0) / p0 * 100, 1),
    })


def _recommend(row: pd.Series) -> pd.Series:
    """Apply tiered business rules to convert optimal price into a recommendation."""
    cat        = row["category"]
    confidence = str(row["confidence"])
    p0         = row["current_price"]
    change     = row["raw_change_pct"]

    if confidence == "low":
        return pd.Series({"recommended_price": p0, "action": "hold — low confidence"})

    if cat == "inelastic":
        cap      = 25 if confidence == "high" else 10
        increase = min(change, cap)
        increase = max(increase, 3)
        return pd.Series({
            "recommended_price": round(p0 * (1 + increase / 100), 2),
            "action": f"increase price ({confidence} confidence)"
        })

    elif cat == "elastic":
        if change > 5 and confidence == "high":
            cap = min(change, 10)
            return pd.Series({
                "recommended_price": round(p0 * (1 + cap / 100), 2),
                "action": "small increase — elastic"
            })
        return pd.Series({"recommended_price": p0, "action": "hold — elastic"})

    elif cat == "highly elastic":
        return pd.Series({"recommended_price": p0, "action": "hold — price sensitive"})

    else:
        return pd.Series({"recommended_price": p0, "action": "manual review"})


def _apply_rule_based(df: pd.DataFrame) -> pd.DataFrame:
    """
    For fixed-price inelastic products (high p_value, no statistical confidence),
    apply a conservative +5% rule-based recommendation.
    """
    mask = (
        (df["category"] == "inelastic") &
        (df["confidence"] == "low") &
        (df["description"] != "manual")
    )
    df.loc[mask, "recommended_price"] = (df.loc[mask, "current_price"] * 1.05).round(2)
    df.loc[mask, "final_change_pct"]  = 5.0
    df.loc[mask, "action"]            = "increase price (rule-based)"
    df.loc[mask, "confidence"]        = "rule-based"

    log.info(f"Rule-based recommendations applied to {mask.sum()} fixed-price inelastic products")
    return df


def build_recommendations(
    elasticity: pd.DataFrame,
    demand_preds: pd.DataFrame,
    products: pd.DataFrame
) -> pd.DataFrame:
    """
    Combine elasticity, demand predictions and product features
    into a full pricing recommendations table.
    """
    log.info("Building master pricing table...")

    latest_month  = demand_preds["InvoiceMonth"].max()
    latest_demand = demand_preds[demand_preds["InvoiceMonth"] == latest_month][
        ["StockCode", "monthly_quantity", "predicted_quantity", "avg_price"]
    ].copy()
    latest_demand.columns = ["StockCode", "actual_qty", "predicted_qty", "current_price"]

    df = elasticity.merge(latest_demand, on="StockCode", how="left")
    df = df.merge(
        products[["StockCode", "total_revenue", "revenue_rank", "avg_unit_price"]],
        on="StockCode", how="left"
    )

    df["current_price"] = df["current_price"].fillna(df["avg_price"])
    df["predicted_qty"] = df["predicted_qty"].fillna(df["actual_qty"]).fillna(50)
    df = df[df["current_price"] > 0].copy()

    # Convert confidence to string before any assignment
    df["confidence"] = df["confidence"].astype(str)

    log.info(f"Master table: {len(df):,} products")

    # Optimise prices
    log.info("Running price optimisation...")
    opt = df.apply(_optimise_row, axis=1)
    df  = pd.concat([df, opt], axis=1)

    # Apply statistical recommendations
    rules = df.apply(_recommend, axis=1)
    df    = pd.concat([df, rules], axis=1)
    df["final_change_pct"] = ((df["recommended_price"] - df["current_price"]) / df["current_price"] * 100).round(1)

    # Apply rule-based recommendations for fixed-price inelastic products
    df = _apply_rule_based(df)

    # Rename for clean output
    if "total_revenue_x" in df.columns:
        df = df.rename(columns={"total_revenue_x": "total_revenue"})

    output_cols = [
        "StockCode", "description", "category", "confidence",
        "current_price", "recommended_price", "final_change_pct",
        "action", "elasticity", "p_value", "r_squared", "total_revenue"
    ]
    recs = df[output_cols].copy()
    recs = recs.rename(columns={"category": "elasticity_category"})
    recs = recs.sort_values("total_revenue", ascending=False).reset_index(drop=True)

    log.info(f"Recommendations built: {len(recs):,} products")
    log.info(f"Action breakdown:\n{recs['action'].value_counts().to_string()}")

    return recs


def run(save_output: bool = True) -> pd.DataFrame:
    """Full optimisation pipeline."""
    elasticity   = pd.read_parquet(PROCESSED_PATH / "elasticity.parquet")
    demand_preds = pd.read_parquet(PROCESSED_PATH / "demand_predictions.parquet")
    products     = pd.read_parquet(PROCESSED_PATH / "product_features.parquet")

    recs = build_recommendations(elasticity, demand_preds, products)

    if save_output:
        recs.to_parquet(PROCESSED_PATH / "price_recommendations.parquet", index=False)
        log.info(f"Saved price_recommendations.parquet — {len(recs):,} products")

    increase = recs[recs["action"].str.startswith("increase price")]
    estimated_uplift = (increase["total_revenue"] * increase["final_change_pct"] / 100).sum()

    log.info(f"Products with price increase : {len(increase)}")
    log.info(f"Estimated annual uplift      : £{estimated_uplift * 12:,.0f}")

    return recs


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    recs = run()
    print(f"\nRecommendations shape: {recs.shape}")
    print(recs["action"].value_counts())
    print("\nTop 5 opportunities:")
    increase = recs[recs["action"].str.startswith("increase price")]
    print(increase.nlargest(5, "total_revenue")[
        ["description", "current_price", "recommended_price", "final_change_pct", "confidence"]
    ].to_string(index=False))