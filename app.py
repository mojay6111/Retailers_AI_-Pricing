from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from pathlib import Path
from src.api.schemas import HealthResponse
from src.api.routes import pricing, forecast, analytics

app = FastAPI(
    title="Retailers AI Pricing API",
    description="Dynamic pricing recommendations powered by demand forecasting and price elasticity.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pricing.router)
app.include_router(forecast.router)
app.include_router(analytics.router)


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health():
    processed = Path("data/processed")
    models    = Path("models")
    return HealthResponse(
        status="ok",
        timestamp=datetime.utcnow(),
        models_loaded=(models / "demand_model.pkl").exists(),
        products_loaded=(processed / "product_features.parquet").exists(),
    )


@app.get("/", tags=["system"])
def root():
    return {
        "name"       : "Retailers AI Pricing API",
        "version"    : "1.0.0",
        "docs"       : "/docs",
        "health"     : "/health",
        "endpoints"  : ["/price", "/forecast", "/analytics"],
    }