"""Main FastAPI application for ML service."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from ml.src.services.deepseek_client import close_deepseek_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events."""
    # Startup
    yield

    # Shutdown: Close DeepSeek client
    await close_deepseek_client()


# Create FastAPI app
app = FastAPI(
    title="Nastavnik ML Service",
    description="ML-сервис для генерации персонализированных учебных треков",
    version="0.1.0",
    lifespan=lifespan,
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "ml"}


# TODO: Register routers here as they are implemented
# from ml.src.api import pipeline, cdv
# app.include_router(pipeline.router)
# app.include_router(cdv.router)
