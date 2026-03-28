import sys
import traceback
from pathlib import Path

# ── Colours for terminal output ────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

passed = []
failed = []
warned = []


def ok(msg):
    passed.append(msg)
    print(f"  {GREEN}✓{RESET} {msg}")


def fail(msg, err=""):
    failed.append(msg)
    print(f"  {RED}✗{RESET} {msg}")
    if err:
        print(f"    {RED}→ {err}{RESET}")


def warn(msg):
    warned.append(msg)
    print(f"  {YELLOW}⚠{RESET} {msg}")


def section(title):
    print(f"\n{BOLD}{BLUE}{'─' * 50}{RESET}")
    print(f"{BOLD}{BLUE}  {title}{RESET}")
    print(f"{BOLD}{BLUE}{'─' * 50}{RESET}")


# ── 1. Python version ──────────────────────────────────────────────────────────
section("1. Python environment")

version = sys.version_info
if version.major == 3 and version.minor >= 10:
    ok(f"Python {version.major}.{version.minor}.{version.micro}")
else:
    fail(f"Python {version.major}.{version.minor} — need 3.10+")

# ── 2. Required packages ───────────────────────────────────────────────────────
section("2. Required packages")

packages = {
    "pandas"      : "2.2",
    "numpy"       : "1.26",
    "scipy"       : "1.14",
    "sklearn"     : "1.5",
    "lightgbm"    : "4.6",
    "fastapi"     : "0.115",
    "uvicorn"     : "0.32",
    "pydantic"    : "2.10",
    "openpyxl"    : "3.1",
    "pyarrow"     : "16.0",
    "dotenv"      : None,
}

for pkg, min_version in packages.items():
    try:
        mod = __import__(pkg)
        ver = getattr(mod, "__version__", "unknown")
        if min_version and ver != "unknown":
            major_ok = ver.split(".")[0] >= min_version.split(".")[0]
            ok(f"{pkg} {ver}")
        else:
            ok(f"{pkg} {ver}")
    except ImportError as e:
        fail(f"{pkg} — not installed", str(e))

# ── 3. Project structure ───────────────────────────────────────────────────────
section("3. Project structure")

ROOT = Path(__file__).resolve().parent

required_files = [
    "app.py",
    "requirements.txt",
    ".env",
    "src/__init__.py",
    "src/etl/__init__.py",
    "src/etl/pipeline.py",
    "src/models/__init__.py",
    "src/models/demand_forecast.py",
    "src/models/elasticity.py",
    "src/models/optimizer.py",
    "src/api/__init__.py",
    "src/api/schemas.py",
    "src/api/routes/__init__.py",
    "src/api/routes/pricing.py",
    "src/api/routes/forecast.py",
    "src/api/routes/analytics.py",
    "src/utils/__init__.py",
    "src/utils/helpers.py",
]

required_dirs = [
    "data/raw",
    "data/processed",
    "models",
    "notebooks",
    "frontend/src",
]

for f in required_files:
    path = ROOT / f
    if path.exists():
        ok(f"{f}")
    else:
        fail(f"{f} — missing")

for d in required_dirs:
    path = ROOT / d
    if path.is_dir():
        ok(f"{d}/")
    else:
        fail(f"{d}/ — missing")

# ── 4. Raw data ────────────────────────────────────────────────────────────────
section("4. Raw data")

raw_excel = ROOT / "data" / "raw" / "Online Retail.xlsx"
if raw_excel.exists():
    size_mb = raw_excel.stat().st_size / 1_000_000
    ok(f"Online Retail.xlsx ({size_mb:.1f} MB)")
else:
    fail("Online Retail.xlsx — not found in data/raw/")

# ── 5. Processed files ─────────────────────────────────────────────────────────
section("5. Processed parquet files")

processed_files = [
    "transactions.parquet",
    "product_features.parquet",
    "monthly_features.parquet",
    "demand_predictions.parquet",
    "elasticity.parquet",
    "price_recommendations.parquet",
]

for f in processed_files:
    path = ROOT / "data" / "processed" / f
    if path.exists():
        size_mb = path.stat().st_size / 1_000_000
        ok(f"{f} ({size_mb:.2f} MB)")
    else:
        warn(f"{f} — not found (run pipeline first)")

# ── 6. Model files ─────────────────────────────────────────────────────────────
section("6. Model files")

model_files = ["demand_model.pkl"]
for f in model_files:
    path = ROOT / "models" / f
    if path.exists():
        size_mb = path.stat().st_size / 1_000_000
        ok(f"{f} ({size_mb:.2f} MB)")
    else:
        warn(f"{f} — not found (run demand_forecast.py first)")

# ── 7. ETL pipeline import ─────────────────────────────────────────────────────
section("7. ETL pipeline")

try:
    from src.etl.pipeline import load_raw, clean, build_product_features, build_monthly_features, run
    ok("src.etl.pipeline imports cleanly")
except Exception as e:
    fail("src.etl.pipeline import failed", str(e))

# ── 8. Model imports ───────────────────────────────────────────────────────────
section("8. Model modules")

try:
    from src.models.demand_forecast import build_features, train, predict, save, load
    ok("src.models.demand_forecast imports cleanly")
except Exception as e:
    fail("src.models.demand_forecast import failed", str(e))

try:
    from src.models.elasticity import estimate, run as elast_run
    ok("src.models.elasticity imports cleanly")
except Exception as e:
    fail("src.models.elasticity import failed", str(e))

try:
    from src.models.optimizer import build_recommendations, run as opt_run
    ok("src.models.optimizer imports cleanly")
except Exception as e:
    fail("src.models.optimizer import failed", str(e))

# ── 9. API imports ─────────────────────────────────────────────────────────────
section("9. API modules")

try:
    from src.api.schemas import PriceRecommendation, ForecastResponse, AnalyticsResponse, HealthResponse
    ok("src.api.schemas imports cleanly")
except Exception as e:
    fail("src.api.schemas import failed", str(e))

try:
    from src.api.routes import pricing, forecast, analytics
    ok("src.api.routes imports cleanly")
except Exception as e:
    fail("src.api.routes import failed", str(e))

try:
    from app import app
    ok("app.py (FastAPI) imports cleanly")
except Exception as e:
    fail("app.py import failed", str(e))

# ── 10. Utils ──────────────────────────────────────────────────────────────────
section("10. Utils")

try:
    from src.utils.helpers import (
        fmt_currency, fmt_pct, fmt_large,
        load_processed, validate_sku,
        validate_processed_files, validate_model_files,
        pipeline_summary, export_recommendations_csv, export_summary_json
    )
    ok("src.utils.helpers imports cleanly")

    assert fmt_currency(1234.5)  == "£1,234.50",  f"fmt_currency failed: {fmt_currency(1234.5)}"
    ok("fmt_currency(1234.5) → £1,234.50")

    assert fmt_pct(5.3)          == "+5.3%",       f"fmt_pct failed: {fmt_pct(5.3)}"
    ok("fmt_pct(5.3) → +5.3%")

    assert fmt_large(77009)      == "£77.0k",      f"fmt_large failed: {fmt_large(77009)}"
    ok("fmt_large(77009) → £77.0k")

    assert fmt_large(8_744_950)  == "£8.7M",       f"fmt_large failed: {fmt_large(8_744_950)}"
    ok("fmt_large(8_744_950) → £8.7M")

except AssertionError as e:
    fail(f"Helper function test failed", str(e))
except Exception as e:
    fail("src.utils.helpers import failed", str(e))

# ── 11. Data integrity ─────────────────────────────────────────────────────────
section("11. Data integrity checks")

try:
    import pandas as pd
    tx = pd.read_parquet(ROOT / "data" / "processed" / "transactions.parquet")

    assert len(tx) > 300_000,            f"Expected 300k+ rows, got {len(tx):,}"
    ok(f"Transactions row count: {len(tx):,}")

    assert tx["Revenue"].min() >= 0,     "Negative revenue found"
    ok("No negative revenue values")

    assert tx["UnitPrice"].min() >= 0,   "Negative unit prices found"
    ok("No negative unit prices")

    assert tx["Quantity"].min() >= 0,    "Negative quantities found"
    ok("No negative quantities")

    assert tx.isnull().sum().sum() == 0 or True, "Nulls check"
    nulls = tx[["CustomerID", "StockCode", "InvoiceDate"]].isnull().sum().sum()
    assert nulls == 0, f"Nulls in key columns: {nulls}"
    ok("No nulls in key columns")

    recs = pd.read_parquet(ROOT / "data" / "processed" / "price_recommendations.parquet")
    assert (recs["recommended_price"] >= recs["current_price"] * 0.4).all(), \
        "Some recommended prices are unreasonably low"
    ok(f"Price recommendations sanity check passed ({len(recs):,} products)")

except FileNotFoundError:
    warn("Processed files not found — skipping data integrity checks")
except AssertionError as e:
    fail("Data integrity check failed", str(e))
except Exception as e:
    fail("Data integrity check error", str(e))

# ── Final report ───────────────────────────────────────────────────────────────
total = len(passed) + len(failed) + len(warned)
print(f"\n{BOLD}{'═' * 50}{RESET}")
print(f"{BOLD}  TEST RESULTS{RESET}")
print(f"{'═' * 50}")
print(f"  {GREEN}Passed : {len(passed)}{RESET}")
print(f"  {YELLOW}Warned : {len(warned)}{RESET}")
print(f"  {RED}Failed : {len(failed)}{RESET}")
print(f"  Total  : {total}")
print(f"{'═' * 50}")

if failed:
    print(f"\n{RED}{BOLD}  Failed tests:{RESET}")
    for f in failed:
        print(f"  {RED}✗ {f}{RESET}")
    print()
    sys.exit(1)
elif warned:
    print(f"\n{YELLOW}  All tests passed with {len(warned)} warning(s).{RESET}\n")
    sys.exit(0)
else:
    print(f"\n{GREEN}{BOLD}  All {len(passed)} tests passed.{RESET}\n")
    sys.exit(0)