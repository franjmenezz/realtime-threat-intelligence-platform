"""
FastAPI Application
────────────────────
REST API + Server-Sent Events for the Threat Intelligence Pipeline.

Endpoints:
  /api/v1/iocs      — IoC CRUD and search
  /api/v1/alerts    — Alert management
  /api/v1/stats     — Dashboard metrics
  /api/v1/stream    — SSE real-time feed
  /api/v1/auth      — JWT authentication
"""

from contextlib import asynccontextmanager

import structlog
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config.settings import settings

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("api_starting", host=settings.API_HOST, port=settings.API_PORT)
    yield
    logger.info("api_shutting_down")


app = FastAPI(
    title="Threat Intelligence Pipeline API",
    description="Real-time IoC ingestion, enrichment and risk scoring.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────────────────────
from api.routes import iocs, alerts, stats, stream, auth  # noqa: E402

app.include_router(auth.router,   prefix="/api/v1/auth",   tags=["Authentication"])
app.include_router(iocs.router,   prefix="/api/v1/iocs",   tags=["IoCs"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["Alerts"])
app.include_router(stats.router,  prefix="/api/v1/stats",  tags=["Statistics"])
app.include_router(stream.router, prefix="/api/v1/stream", tags=["Streaming"])


@app.get("/health", tags=["Health"])
async def health_check():
    return JSONResponse({"status": "ok", "service": "threat-intel-pipeline"})


if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_DEBUG,
        log_level="info",
    )
