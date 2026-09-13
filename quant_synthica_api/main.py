from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from quant_synthica_api.core.config import get_settings
from quant_synthica_api.core.logging import logger
from quant_synthica_api.core.exceptions import (
    QuantSynthicaException, SymbolResolutionError, ProviderError
)
from quant_synthica_api.api.router import api_v1_router
from quant_synthica_api.database.init_db import init_db

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing QuantSynthica Market API...")
    init_db()
    logger.info("Database initialized.")
    yield
    logger.info("Shutting down QuantSynthica Market API...")

app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="Unified Financial-Data API integrating yfinance, TradingView-Screener, and Screener.in with quantitative analytics.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception Handlers
@app.exception_handler(SymbolResolutionError)
async def symbol_resolution_error_handler(request: Request, exc: SymbolResolutionError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"error": "SymbolResolutionError", "message": exc.message, "details": exc.details}
    )

@app.exception_handler(ProviderError)
async def provider_error_handler(request: Request, exc: ProviderError):
    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY,
        content={"error": "ProviderError", "provider": exc.provider, "message": exc.message, "details": exc.details}
    )

@app.exception_handler(QuantSynthicaException)
async def generic_quantsynthica_error_handler(request: Request, exc: QuantSynthicaException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "QuantSynthicaException", "message": exc.message, "details": exc.details}
    )

# Root redirect to OpenAPI Docs
@app.get("/", include_in_schema=False)
def root_redirect():
    return RedirectResponse(url="/docs")

# Standard container health check for Render/K8s/AWS
@app.get("/healthz", include_in_schema=False)
def healthz():
    return {"status": "ok", "service": "QuantSynthica Market API"}


# Include master API router
app.include_router(api_v1_router)
