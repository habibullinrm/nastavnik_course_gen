"""Main FastAPI application for backend service."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.src.core.database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events."""
    # Startup: Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    # Shutdown: Close database connections
    await engine.dispose()


# Create FastAPI app
app = FastAPI(
    title="Nastavnik Backend API",
    description="Backend API для сервиса тестирования алгоритма генерации учебных треков",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "backend"}


# Register routers
from backend.src.api import profiles

app.include_router(profiles.router, prefix="/api")

# TODO: Register remaining routers as they are implemented
# from backend.src.api import tracks, qa, logs, export
# app.include_router(tracks.router, prefix="/api")
# app.include_router(qa.router, prefix="/api")
# app.include_router(logs.router, prefix="/api")
# app.include_router(export.router, prefix="/api")
