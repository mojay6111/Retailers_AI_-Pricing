# Retailers AI Pricing

A production-ready retail pricing intelligence system powered by machine learning.
Analyses transaction history, estimates price elasticity per product, forecasts demand,
and recommends optimal prices — all exposed via a FastAPI backend and React dashboard.

**Live Demo**

- Dashboard: https://retailers-ai-pricing.vercel.app
- API: https://retailers-ai-pricing.onrender.com
- API Docs: https://retailers-ai-pricing.onrender.com/docs

---

## What It Does

| Stage           | Description                            | Output                           |
| --------------- | -------------------------------------- | -------------------------------- |
| ETL             | Cleans 541k raw transactions           | 396k clean rows, 3 parquet files |
| EDA             | Explores revenue, pricing, seasonality | 6 analysis notebooks             |
| Demand forecast | LightGBM model per product             | MAE 69 units/month               |
| Elasticity      | Log-log OLS regression per SKU         | 1,763 products estimated         |
| Optimizer       | Price sweep + business rules           | 71 recommendations               |
| API             | FastAPI with 3 route groups            | /price /forecast /analytics      |
| Dashboard       | React + Recharts frontend              | Live charts and search           |

**Key results on the UCI Online Retail dataset (Dec 2010 — Dec 2011):**

- 3,665 unique products analysed
- £8,744,951 total revenue
- 71 products recommended for price increases
- £77,009 estimated annual revenue uplift

---

## Project Structure

```
Retailers_AI_Pricing/
├── app.py                        # FastAPI entry point
├── Dockerfile                    # Production container
├── requirements.txt              # Python dependencies
├── render.yaml                   # Render deployment config
├── test_environment.py           # 61-test suite
│
├── src/
│   ├── etl/
│   │   └── pipeline.py          # Load, clean, feature engineer
│   ├── models/
│   │   ├── demand_forecast.py   # LightGBM demand model
│   │   ├── elasticity.py        # Price elasticity estimation
│   │   └── optimizer.py         # Price recommendation engine
│   ├── api/
│   │   ├── schemas.py           # Pydantic request/response models
│   │   └── routes/
│   │       ├── pricing.py       # GET /price/{sku}
│   │       ├── forecast.py      # GET /forecast/{sku}
│   │       └── analytics.py     # GET /analytics/
│   └── utils/
│       └── helpers.py           # Formatting, loading, validation
│
├── notebooks/
│   ├── 01_eda.ipynb             # Exploratory data analysis
│   ├── 02_cleaning.ipynb        # ETL validation
│   ├── 03_demand_forecast.ipynb # Model training
│   ├── 04_elasticity.ipynb      # Elasticity estimation
│   ├── 05_optimizer.ipynb       # Price optimisation
│   └── 06_evaluation.ipynb      # Pipeline summary dashboard
│
├── frontend/                     # React dashboard
│   └── src/
│       ├── api.js               # API fetch functions
│       ├── App.jsx              # Main app component
│       └── components/
│           ├── NavBar.jsx
│           ├── SummaryCards.jsx
│           ├── ElasticityChart.jsx
│           ├── TopProductsChart.jsx
│           ├── ForecastChart.jsx
│           ├── SKUSearch.jsx
│           └── RecommendationsTable.jsx
│
├── data/
│   ├── raw/                     # Online Retail.xlsx (not committed)
│   └── processed/               # Generated parquet files
│
└── models/                      # Trained model artifacts
```

---

## Prerequisites

- Python 3.11
- Node.js 18+
- Conda (recommended) or virtualenv
- Git

---

## Local Setup — Step by Step

### 1. Clone the repository

```bash
git clone https://github.com/mojay6111/Retailers_AI_Pricing.git
cd Retailers_AI_Pricing
```

### 2. Create and activate conda environment

```bash
conda create -n Retailers_AI_Pricing python=3.11 -y
conda activate Retailers_AI_Pricing
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Add the raw dataset

Download the UCI Online Retail dataset and place it at:

```
data/raw/Online Retail.xlsx
```

Direct link: https://archive.ics.uci.edu/ml/datasets/online+retail

### 5. Verify the environment

```bash
python test_environment.py
```

Expected output:

```
Passed : 61
Warned : 0
Failed : 0
All 61 tests passed.
```

---

## Running the ML Pipeline

Run each step in order. Each script reads from the previous step's output.

### Step 1 — ETL pipeline

Loads the raw Excel file, cleans it and engineers features.
Saves 3 parquet files to `data/processed/`.

```bash
python -m src.etl.pipeline
```

Expected output:

```
Loaded 541,909 rows, 8 columns
Cleaned: 541,909 → 396,777 rows (145,132 removed)
Product features: 3,665 products, 16 features
Monthly features: 30,336 rows
Saved processed files to data/processed
```

### Step 2 — Demand forecasting

Trains a LightGBM model on monthly demand per product.
Saves the model to `models/demand_model.pkl` and predictions to `data/processed/`.

```bash
python -m src.models.demand_forecast
```

Expected output:

```
Train: 15,638 rows | Val: 4,405 rows
Validation — MAE: 68.6 | RMSE: 233.9 | MAPE: 62.9%
Saved demand_model.pkl
Saved demand_predictions.parquet
```

### Step 3 — Price elasticity

Estimates price elasticity per product using log-log OLS regression.
Saves results to `data/processed/elasticity.parquet`.

```bash
python -m src.models.elasticity
```

Expected output:

```
Eligible products: 1,763 of 3,665
Elasticity estimated for 1,763 products
highly elastic    : 1069
unusual           : 335
elastic           : 287
inelastic         : 72
```

### Step 4 — Price optimizer

Combines demand forecasts and elasticity to generate pricing recommendations.
Saves results to `data/processed/price_recommendations.parquet`.

```bash
python -m src.models.optimizer
```

Expected output:

```
Master table: 1,763 products
Rule-based recommendations applied to 67 fixed-price inelastic products
Products with price increase : 71
Estimated annual uplift      : £77,009
```

### Step 5 — Pipeline summary

Validates all outputs and prints a full summary report.

```bash
python -m src.utils.helpers
```

Expected output:

```
TRANSACTIONS
  Rows         : 396,777
  Period       : Dec 2010 — Dec 2011
  Revenue      : £8,744,950.52
  Products     : 3,665
  Customers    : 4,337
  Countries    : 37

ELASTICITY
  Estimated    : 1,763 products
  High conf.   : 651 (p < 0.05)

RECOMMENDATIONS
  Increases    : 71
  Annual uplift: £77.0k

PROCESSED FILES
  ✓ transactions.parquet         3.12 MB
  ✓ product_features.parquet     0.30 MB
  ✓ monthly_features.parquet     0.53 MB
  ✓ demand_predictions.parquet   0.32 MB
  ✓ elasticity.parquet           0.13 MB
  ✓ price_recommendations.parquet 0.11 MB

MODEL FILES
  ✓ demand_model.pkl             1.52 MB
```

---

## Running the Notebooks

The notebooks walk through each stage interactively with charts and analysis.
Run them in order — each one depends on the outputs of the previous.

```bash
# Register the conda env as a Jupyter kernel first
python -m ipykernel install --user \
  --name Retailers_AI_Pricing \
  --display-name "Retailers_AI_Pricing"

# Start Jupyter
jupyter notebook
```

Then open and run in order:

1. `notebooks/01_eda.ipynb` — raw data exploration
2. `notebooks/02_cleaning.ipynb` — ETL validation and audit
3. `notebooks/03_demand_forecast.ipynb` — model training and evaluation
4. `notebooks/04_elasticity.ipynb` — elasticity estimation and charts
5. `notebooks/05_optimizer.ipynb` — price optimisation
6. `notebooks/06_evaluation.ipynb` — full pipeline dashboard

---

## Running the API

### Development mode

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8001
```

### Test the endpoints

```bash
# Health check
curl http://localhost:8001/health

# Get pricing recommendation for a SKU
curl http://localhost:8001/price/22178

# Get all recommendations with price increases
curl "http://localhost:8001/price/?action=increase&limit=10"

# Get demand forecast for a SKU
curl http://localhost:8001/forecast/85123A

# Get full analytics summary
curl http://localhost:8001/analytics/
```

### Interactive API docs

Open in browser:

```
http://localhost:8001/docs
```

---

## Running the Frontend

```bash
cd frontend
npm install
npm run dev
```

Open in browser:

```
http://localhost:5173
```

The frontend expects the API running on port 8001 locally.
To change the API URL edit `frontend/src/api.js` line 1:

```js
const BASE = "http://localhost:8001";
```

---

## Running with Docker

### Build the image

```bash
docker build -t retailers-ai-pricing .
```

### Run the container

```bash
docker run -p 8002:8000 --name pricing-api retailers-ai-pricing
```

### Test the containerised API

```bash
curl http://localhost:8002/health
curl http://localhost:8002/analytics/
```

---

## API Reference

### `GET /health`

Returns API status and whether models and data are loaded.

```json
{
  "status": "ok",
  "timestamp": "2026-03-28T17:47:06.030830",
  "models_loaded": true,
  "products_loaded": true
}
```

### `GET /price/{stock_code}`

Returns pricing recommendation for a single SKU.

```json
{
  "stock_code": "22178",
  "description": "victorian glass hanging t-light",
  "elasticity_category": "inelastic",
  "confidence": "rule-based",
  "current_price": 1.94,
  "recommended_price": 2.03,
  "price_change_pct": 5.0,
  "action": "increase price (rule-based)",
  "elasticity": -0.1008,
  "p_value": 0.8434,
  "r_squared": 0.0037,
  "total_revenue": 28776.51
}
```

### `GET /price/`

Returns all recommendations. Optional query params:

- `action` — filter by action string e.g. `increase`
- `limit` — max results (default 50)

### `GET /forecast/{stock_code}`

Returns monthly demand forecast for a SKU.

```json
[
  {
    "stock_code": "22178",
    "invoice_month": "2011-03",
    "actual_quantity": 2408.0,
    "predicted_quantity": 2201.3,
    "avg_price": 1.94
  }
]
```

### `GET /analytics/`

Returns full analytics summary including top products,
elasticity breakdown and recommendation action counts.

---

## Deployment

### API — Render (free tier)

1. Push to GitHub
2. Go to render.com → New Web Service
3. Connect your GitHub repository
4. Render auto-detects `render.yaml`
5. Click Deploy

Live at: https://retailers-ai-pricing.onrender.com

### Frontend — Vercel (free tier)

1. Go to vercel.com → Add New Project
2. Import your GitHub repository
3. Set root directory to `frontend`
4. Framework: Vite | Build: `npm run build` | Output: `dist`
5. Click Deploy

Live at: https://retailers-ai-pricing.vercel.app

### Environment variables

For local development create a `.env` file in the project root:

```
# Add any environment-specific config here
# e.g. API keys if you extend the project
```

---

## Tech Stack

| Layer            | Technology                          |
| ---------------- | ----------------------------------- |
| Data processing  | pandas, numpy, openpyxl             |
| ML models        | LightGBM, scikit-learn, scipy       |
| API              | FastAPI, uvicorn, pydantic          |
| Frontend         | React, Vite, Recharts, Tailwind CSS |
| Containerisation | Docker                              |
| API hosting      | Render                              |
| Frontend hosting | Vercel                              |
| Notebooks        | Jupyter, ipykernel                  |

---

## Limitations and Next Steps

**Current limitations:**

- Dataset covers only 13 months (Dec 2010 — Dec 2011)
- Short time window limits statistical significance of elasticity estimates
- No competitor pricing data
- Rule-based recommendations for fixed-price products

**Potential improvements:**

- Add more years of data to improve elasticity confidence
- Integrate competitor price scraping
- Add A/B testing framework to validate recommendations
- Build a retrain schedule (monthly) as new data arrives
- Add customer segmentation for personalised pricing
- Extend the API with a POST /retrain endpoint

---

## License

MIT License — free to use, modify and distribute.

---

## Author

Built by Edwin George (cap_mojay)

- GitHub: https://github.com/mojay6111/Retailers_AI_Pricing
- Live demo: https://retailers-ai-pricing.vercel.app
