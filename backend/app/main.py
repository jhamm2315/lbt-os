"""
LBT OS — FastAPI Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from .config import settings
from .routers import audit, customers, expenses, integrations, leads, metrics, organizations, sales, stripe_webhooks

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="LBT OS API",
    description="Lean Business Tracker OS — Backend API",
    version="1.0.0",
    docs_url="/docs" if settings.app_env != "production" else None,
    redoc_url=None,
)

# --- Rate limiting ---
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:5176",
        "http://localhost:5177",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers ---
app.include_router(organizations.router,    prefix="/api/v1")
app.include_router(leads.router,            prefix="/api/v1")
app.include_router(customers.router,        prefix="/api/v1")
app.include_router(sales.router,            prefix="/api/v1")
app.include_router(expenses.router,         prefix="/api/v1")
app.include_router(metrics.router,          prefix="/api/v1")
app.include_router(audit.router,            prefix="/api/v1")
app.include_router(integrations.router,     prefix="/api/v1")
app.include_router(stripe_webhooks.router,  prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok", "env": settings.app_env}
