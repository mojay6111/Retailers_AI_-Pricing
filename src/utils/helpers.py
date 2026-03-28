import pandas as pd
import numpy as np
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

log = logging.getLogger(__name__)

PROCESSED_PATH = Path(__file__).resolve().parents[2] / "data" / "processed"
MODELS_PATH    = Path(__file__).resolve().parents[2] / "models"


# ── Formatting helpers ─────────────────────────────────────────────────────────

def fmt_currency(value: float, symbol: str = "£") -> str:
    """Format a number as a currency string. e.g. 1234.5 → £1,234.50"""
    return f"{symbol}{value:,.2f}"


def fmt_pct(value: float, decimals: int = 1) -> str:
    """Format a number as a percentage string. e.g. 0.053 → +5.3%"""
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.{decimals}f}%"


def fmt_large(value: float, symbol: str = "£") -> str:
    """Format large numbers with k/M suffix. e.g. 77009 → £77.0k"""
    if abs(value) >= 1_000_000:
        return f"{symbol}{value/1_000_000:.1f}M"
    elif abs(value) >= 1_000:
        return f"{symbol}{value/1_000:.1f}k"
    return fmt_currency(value, symbol)


# ── Data loading helpers ───────────────────────────────────────────────────────

def load_processed(filename: str) -> pd.DataFrame:
    """Load a parquet file from the processed data directory."""
    path = PROCESSED_PATH / filename
    if not path.exists():
        raise FileNotFoundError(
            f"{filename} not found in {PROCESSED_PATH}. "
            f"Run the ETL pipeline first: python -m src.etl.pipeline"
        )
    df = pd.read_parquet(path)
    log.debug(f"Loaded {filename}: {df.shape}")
    return df


def load_all() -> dict:
    """Load all processed parquet files into a dict."""
    files = {
        "transactions"         : "transactions.parquet",
        "product_features"     : "product_features.parquet",
        "monthly_features"     : "monthly_features.parquet",
        "demand_predictions"   : "demand_predictions.parquet",
        "elasticity"           : "elasticity.parquet",
        "price_recommendations": "price_recommendations.parquet",
    }
    data = {}
    missing = []
    for key, filename in files.items():
        try:
            data[key] = load_processed(filename)
        except FileNotFoundError:
            missing.append(filename)
            log.warning(f"Missing: {filename}")

    if missing:
        log.warning(f"{len(missing)} files not found: {missing}")

    log.info(f"Loaded {len(data)}/{len(files)} processed files")
    return data


# ── Validation helpers ─────────────────────────────────────────────────────────

def validate_sku(sku: str, df: pd.DataFrame, col: str = "StockCode") -> bool:
    """Check if a SKU exists in a dataframe."""
    return sku.upper() in df[col].str.upper().values


def validate_processed_files() -> dict:
    """Check which processed files exist and return a status report."""
    files = [
        "transactions.parquet",
        "product_features.parquet",
        "monthly_features.parquet",
        "demand_predictions.parquet",
        "elasticity.parquet",
        "price_recommendations.parquet",
    ]
    status = {}
    for f in files:
        path = PROCESSED_PATH / f
        status[f] = {
            "exists"      : path.exists(),
            "size_mb"     : round(path.stat().st_size / 1_000_000, 2) if path.exists() else None,
            "modified"    : datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                           if path.exists() else None,
        }
    return status


def validate_model_files() -> dict:
    """Check which model files exist and return a status report."""
    files = ["demand_model.pkl"]
    status = {}
    for f in files:
        path = MODELS_PATH / f
        status[f] = {
            "exists"  : path.exists(),
            "size_mb" : round(path.stat().st_size / 1_000_000, 2) if path.exists() else None,
            "modified": datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                       if path.exists() else None,
        }
    return status


# ── Pipeline summary helpers ───────────────────────────────────────────────────

def pipeline_summary() -> dict:
    """Generate a full summary of the pipeline outputs."""
    data = load_all()
    summary = {}

    if "transactions" in data:
        tx = data["transactions"]
        summary["transactions"] = {
            "total_rows"    : len(tx),
            "date_range"    : f"{tx['InvoiceDate'].min().strftime('%b %Y')} — {tx['InvoiceDate'].max().strftime('%b %Y')}",
            "total_revenue" : fmt_currency(tx["Revenue"].sum()),
            "unique_skus"   : tx["StockCode"].nunique(),
            "unique_customers": tx["CustomerID"].nunique(),
            "countries"     : tx["Country"].nunique(),
        }

    if "product_features" in data:
        products = data["product_features"]
        summary["products"] = {
            "total"          : len(products),
            "avg_price"      : fmt_currency(products["avg_unit_price"].mean()),
            "median_price"   : fmt_currency(products["avg_unit_price"].median()),
            "total_revenue"  : fmt_large(products["total_revenue"].sum()),
        }

    if "elasticity" in data:
        elast = data["elasticity"]
        summary["elasticity"] = {
            "products_estimated": len(elast),
            "category_breakdown": elast["category"].value_counts().to_dict(),
            "high_confidence"   : int((elast["p_value"] < 0.05).sum()),
            "medium_confidence" : int((elast["p_value"] < 0.20).sum()),
        }

    if "price_recommendations" in data:
        recs     = data["price_recommendations"]
        increase = recs[recs["action"].str.startswith("increase price")]
        uplift   = (increase["total_revenue"] * increase["final_change_pct"] / 100).sum()
        summary["recommendations"] = {
            "total_products"          : len(recs),
            "price_increases"         : len(increase),
            "avg_increase_pct"        : round(float(increase["final_change_pct"].mean()), 1),
            "estimated_annual_uplift" : fmt_large(uplift * 12),
            "action_breakdown"        : recs["action"].value_counts().to_dict(),
        }

    return summary


def print_summary() -> None:
    """Pretty print the full pipeline summary to console."""
    summary = pipeline_summary()
    print("\n" + "=" * 55)
    print("  RETAILERS AI PRICING — PIPELINE SUMMARY")
    print("=" * 55)

    if "transactions" in summary:
        t = summary["transactions"]
        print(f"\n TRANSACTIONS")
        print(f"  Rows         : {t['total_rows']:,}")
        print(f"  Period       : {t['date_range']}")
        print(f"  Revenue      : {t['total_revenue']}")
        print(f"  Products     : {t['unique_skus']:,}")
        print(f"  Customers    : {t['unique_customers']:,}")
        print(f"  Countries    : {t['countries']}")

    if "elasticity" in summary:
        e = summary["elasticity"]
        print(f"\n ELASTICITY")
        print(f"  Estimated    : {e['products_estimated']:,} products")
        print(f"  High conf.   : {e['high_confidence']} (p < 0.05)")
        print(f"  Medium conf. : {e['medium_confidence']} (p < 0.20)")
        for cat, count in e["category_breakdown"].items():
            print(f"  {cat:<18}: {count}")

    if "recommendations" in summary:
        r = summary["recommendations"]
        print(f"\n RECOMMENDATIONS")
        print(f"  Analysed     : {r['total_products']:,} products")
        print(f"  Increases    : {r['price_increases']}")
        print(f"  Avg increase : +{r['avg_increase_pct']}%")
        print(f"  Annual uplift: {r['estimated_annual_uplift']}")

    print("\n" + "=" * 55)

    print("\n PROCESSED FILES")
    for fname, info in validate_processed_files().items():
        status = "✓" if info["exists"] else "✗"
        size   = f"{info['size_mb']} MB" if info["size_mb"] else "missing"
        print(f"  {status} {fname:<40} {size}")

    print("\n MODEL FILES")
    for fname, info in validate_model_files().items():
        status = "✓" if info["exists"] else "✗"
        size   = f"{info['size_mb']} MB" if info["size_mb"] else "missing"
        print(f"  {status} {fname:<40} {size}")

    print("=" * 55 + "\n")


# ── Export helpers ─────────────────────────────────────────────────────────────

def export_recommendations_csv(output_path: Optional[Path] = None) -> Path:
    """Export price recommendations to CSV for sharing."""
    recs = load_processed("price_recommendations.parquet")
    path = output_path or PROCESSED_PATH / "price_recommendations.csv"
    recs.to_csv(path, index=False)
    log.info(f"Exported recommendations to {path}")
    return path


def export_summary_json(output_path: Optional[Path] = None) -> Path:
    """Export pipeline summary to JSON."""
    summary = pipeline_summary()
    path = output_path or PROCESSED_PATH / "pipeline_summary.json"
    with open(path, "w") as f:
        json.dump(summary, f, indent=2)
    log.info(f"Exported summary to {path}")
    return path


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    print_summary()
    export_recommendations_csv()
    export_summary_json()
    print("Exports saved to data/processed/")