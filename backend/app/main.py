import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import engine, Base, check_db_connection
from .routes import health, commodities, mandis, prices, forecast, query

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mandi_bhav_bot")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-Powered Agricultural Market Price Advisor (Mandi Bhav Bot) with PostgreSQL & Time-Series Forecasting",
    version=settings.PROJECT_VERSION
)

# CORS setup for Flutter Web & Mobile
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers under /api
app.include_router(health.router, prefix=settings.API_PREFIX)
app.include_router(commodities.router, prefix=settings.API_PREFIX)
app.include_router(mandis.router, prefix=settings.API_PREFIX)
app.include_router(prices.router, prefix=settings.API_PREFIX)
app.include_router(forecast.router, prefix=settings.API_PREFIX)
app.include_router(query.router, prefix=settings.API_PREFIX)


@app.on_event("startup")
def on_startup():
    logger.info("Initializing Mandi Bhav Bot Backend...")
    db_status = check_db_connection()
    if db_status.get("connected"):
        logger.info("Successfully connected to PostgreSQL! Verifying tables...")
        try:
            if Base and getattr(Base, "metadata", None) and engine:
                Base.metadata.create_all(bind=engine)
                logger.info("PostgreSQL tables checked/created.")
        except Exception as e:
            logger.warning(f"Could not automatically create tables in PostgreSQL: {e}")
    else:
        logger.warning(
            f"PostgreSQL is not connected ({db_status.get('error', 'unknown')}). "
            "System will use initial seed dataset cache for API responses until PostgreSQL is available."
        )


@app.get("/")
def home():
    return {
        "project": "CROPORA AI - Mandi Bhav Bot",
        "description": "AI-Powered Agricultural Market Price Advisor",
        "version": settings.PROJECT_VERSION,
        "database": "PostgreSQL",
        "docs_url": "/docs",
        "api_health": "/api/health"
    }
