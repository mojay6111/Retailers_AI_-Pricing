import pandas as pd
import numpy as np
import pickle
import logging
from pathlib import Path
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.preprocessing import LabelEncoder
import lightgbm as lgb

log = logging.getLogger(__name__)

PROCESSED_PATH = Path(__file__).resolve().parents[2] / "data" / "processed"
MODELS_PATH    = Path(__file__).resolve().parents[2] / "models"


def build_features(monthly: pd.DataFrame, products: pd.DataFrame) -> pd.DataFrame:
    """Engineer lag and rolling features for demand forecasting."""
    df = monthly.copy()
    df = df.sort_values(["StockCode", "InvoiceMonth"]).reset_index(drop=True)

    for lag in [1, 2, 3]:
        df[f"qty_lag{lag}"] = df.groupby("StockCode")["monthly_quantity"].shift(lag)

    df["qty_roll3"] = (
        df.groupby("StockCode")["monthly_quantity"]
        .transform(lambda x: x.shift(1).rolling(3, min_periods=1).mean())
    )
    df["price_lag1"] = df.groupby("StockCode")["avg_price"].shift(1)
    df["month_num"]  = pd.to_datetime(df["InvoiceMonth"]).dt.month

    le = LabelEncoder()
    df["stock_code_enc"] = le.fit_transform(df["StockCode"])

    df = df.merge(
        products[["StockCode", "total_revenue", "num_customers", "avg_unit_price", "revenue_rank"]],
        on="StockCode", how="left"
    )
    df = df.dropna(subset=["qty_lag1", "qty_lag2", "qty_lag3"])
    df["log_quantity"] = np.log1p(df["monthly_quantity"])

    return df, le


FEATURES = [
    "stock_code_enc", "qty_lag1", "qty_lag2", "qty_lag3", "qty_roll3",
    "price_lag1", "month_num", "avg_price", "num_orders", "num_customers_x",
    "total_revenue", "avg_unit_price", "revenue_rank"
]


def train(monthly: pd.DataFrame, products: pd.DataFrame) -> dict:
    """Train LightGBM demand forecasting model. Returns model artifact dict."""
    log.info("Building features for demand model...")
    df, le = build_features(monthly, products)

    sorted_months = sorted(df["InvoiceMonth"].unique())
    val_months    = sorted_months[-2:]
    train_months  = sorted_months[:-2]

    train_df = df[df["InvoiceMonth"].isin(train_months)]
    val_df   = df[df["InvoiceMonth"].isin(val_months)]

    X_train, y_train = train_df[FEATURES], train_df["log_quantity"]
    X_val,   y_val   = val_df[FEATURES],   val_df["log_quantity"]

    log.info(f"Train: {len(train_df):,} rows | Val: {len(val_df):,} rows")

    model = lgb.LGBMRegressor(
        n_estimators=500, learning_rate=0.05,
        num_leaves=31, min_child_samples=10,
        subsample=0.8, colsample_bytree=0.8,
        random_state=42, verbose=-1
    )
    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        callbacks=[lgb.early_stopping(50, verbose=False), lgb.log_evaluation(100)]
    )

    preds   = np.expm1(np.maximum(model.predict(X_val), 0))
    actuals = np.expm1(y_val.values)
    mae     = mean_absolute_error(actuals, preds)
    rmse    = np.sqrt(mean_squared_error(actuals, preds))
    mape    = np.mean(np.abs((actuals - preds) / (actuals + 1))) * 100

    log.info(f"Validation — MAE: {mae:.1f} | RMSE: {rmse:.1f} | MAPE: {mape:.1f}%")

    artifact = {
        "model":         model,
        "features":      FEATURES,
        "label_encoder": le,
        "metrics":       {"mae": mae, "rmse": rmse, "mape": mape},
        "val_months":    val_months,
    }
    return artifact


def save(artifact: dict, path: Path = None) -> Path:
    """Save model artifact to disk."""
    path = path or MODELS_PATH / "demand_model.pkl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(artifact, f)
    log.info(f"Saved demand model to {path}")
    return path


def load(path: Path = None) -> dict:
    """Load model artifact from disk."""
    path = path or MODELS_PATH / "demand_model.pkl"
    with open(path, "rb") as f:
        artifact = pickle.load(f)
    log.info(f"Loaded demand model from {path}")
    return artifact


def predict(monthly: pd.DataFrame, products: pd.DataFrame, artifact: dict) -> pd.DataFrame:
    """Generate demand predictions for all products and months."""
    df, _ = build_features(monthly, products)

    # Use the saved label encoder to handle unseen codes gracefully
    le: LabelEncoder = artifact["label_encoder"]
    known = set(le.classes_)
    df = df[df["StockCode"].isin(known)].copy()
    df["stock_code_enc"] = le.transform(df["StockCode"])

    df["predicted_quantity"] = np.expm1(
        np.maximum(artifact["model"].predict(df[artifact["features"]]), 0)
    )

    return df[["StockCode", "InvoiceMonth", "monthly_quantity", "predicted_quantity", "avg_price"]]


def run(save_output: bool = True) -> pd.DataFrame:
    """Full train + predict pipeline. Saves model and predictions."""
    monthly  = pd.read_parquet(PROCESSED_PATH / "monthly_features.parquet")
    products = pd.read_parquet(PROCESSED_PATH / "product_features.parquet")

    artifact = train(monthly, products)
    save(artifact)

    predictions = predict(monthly, products, artifact)

    if save_output:
        predictions.to_parquet(PROCESSED_PATH / "demand_predictions.parquet", index=False)
        log.info(f"Saved demand predictions — {len(predictions):,} rows")

    return predictions


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    preds = run()
    print(f"\nPredictions shape: {preds.shape}")
    print(preds.head())