"""FastAPI application entry point."""

import contextlib
import logging
from collections.abc import AsyncGenerator

import fastapi
import fastapi.responses
import opentelemetry.instrumentation.fastapi as otel_fastapi
from fastapi.middleware.cors import CORSMiddleware

from .modules.items import items_router
from .modules.projects import projects_router
from .telemetry import configure_opentelemetry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@contextlib.asynccontextmanager
async def lifespan(app: fastapi.FastAPI) -> AsyncGenerator[None]:
    """Application lifespan handler - configure telemetry on startup."""
    configure_opentelemetry()
    logger.info("Application started with OpenTelemetry configured")
    yield
    logger.info("Application shutting down")


# Create FastAPI application
app = fastapi.FastAPI(
    title="FastAPI React Aspire Starter",
    description="A minimal starter template with FastAPI, React Router, and Aspire",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(items_router, prefix="/api")
app.include_router(projects_router, prefix="/api")


@app.get("/", response_class=fastapi.responses.HTMLResponse)
async def root() -> str:
    """Root endpoint with welcome message."""
    return """
    <html>
        <head><title>FastAPI React Aspire Starter</title></head>
        <body>
            <h1>Welcome to the FastAPI React Aspire Starter</h1>
            <p>API documentation: <a href="/docs">/docs</a></p>
            <p>Health check: <a href="/health">/health</a></p>
        </body>
    </html>
    """


@app.get("/health", response_class=fastapi.responses.PlainTextResponse)
async def health_check() -> str:
    """Health check endpoint for Aspire and container orchestration."""
    return "Healthy"


# Instrument FastAPI with OpenTelemetry
otel_fastapi.FastAPIInstrumentor.instrument_app(
    app,
    exclude_spans=["send", "receive"],
    excluded_urls="health",
)
