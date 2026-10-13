"""
Support Ticket Automation System
FastAPI Application Entrypoint
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.config import APP_NAME, APP_VERSION, API_PREFIX, CORS_ORIGINS
from app.database import init_db
from app.classifier import get_classifier
from app.routes import health, tickets, approvals, metrics

# Configure clean logging format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown lifecycle management.
    Initializes database tables and trains/loads the ML classifier.
    """
    logger.info("Initializing Support Ticket Automation backend...")
    init_db()
    # Eagerly initialize and train the ML classifier pipeline
    classifier = get_classifier()
    if classifier.is_trained:
        logger.info("Machine learning classifier pipeline initialized successfully.")
    else:
        logger.warning("Classifier pipeline encountered issues during startup training.")
    yield
    logger.info("Shutting down Support Ticket Automation backend.")


app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=(
        "Enterprise, zero-cost AI-assisted support ticket processing backend."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# CORS middleware for local frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handler for Clean Validation Errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        field = ".".join(str(loc) for loc in err.get("loc", []))
        errors.append({
            "field": field,
            "message": err.get("msg")
        })
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Input validation failed. Please check the submitted fields.",
            "errors": errors
        }
    )


# Exception handler to prevent leaking internal stack traces
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled server error on {request.method} {request.url.path}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An internal server error occurred. Please contact the administrator."
        }
    )


# Register routes at both root and /api for compatibility with direct tests and API clients
app.include_router(health.router)
app.include_router(tickets.router)
app.include_router(approvals.router)
app.include_router(metrics.router)

# Mount also under /api prefix for API clients
app.include_router(health.router, prefix=API_PREFIX)
app.include_router(tickets.router, prefix=API_PREFIX)
app.include_router(approvals.router, prefix=API_PREFIX)
app.include_router(metrics.router, prefix=API_PREFIX)


@app.get("/", tags=["Root"])
def root():
    return {
        "app": APP_NAME,
        "version": APP_VERSION,
        "docs": "/docs",
        "health": "/health",
        "api_prefix": API_PREFIX
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
