import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from .errors import ErrorResponse
from .logging_config import setup_logging
from .routes.api import protected_router, public_router
from .services.db import client, ensure_indexes, init_firebase


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add basic security headers to each response."""

    def __init__(self, app: FastAPI, csp: str = "default-src 'self'") -> None:
        super().__init__(app)
        self.csp = csp

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers.setdefault(
            "Strict-Transport-Security", "max-age=63072000; includeSubDomains"
        )
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("Content-Security-Policy", self.csp)
        return response


ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

# Parse allowed origins from the required environment variable
allowed_origins_env = os.getenv("ALLOWED_ORIGINS")
if not allowed_origins_env:
    raise RuntimeError("ALLOWED_ORIGINS environment variable must be set")

allowed_origins = [
    origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()
]
if not allowed_origins:
    raise RuntimeError("ALLOWED_ORIGINS environment variable must not be empty")

app = FastAPI(
    title="MCP-CMS",
    description="Model Context Protocol based Content Management System",
)

# Security headers middleware must run before other middleware
app.add_middleware(SecurityHeadersMiddleware)

# Register API routes
app.include_router(public_router)
app.include_router(protected_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize Firebase when the module is imported
init_firebase()


@app.on_event("startup")
async def startup_db_client():
    await ensure_indexes()


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()


# FastAPI exception handlers
@app.exception_handler(HTTPException)
async def handle_http_exception(request: Request, exc: HTTPException) -> JSONResponse:
    logger.warning("HTTPException: %s", exc.detail)
    if isinstance(exc.detail, dict):
        error_detail = exc.detail
    else:
        error_detail = ErrorResponse(message="An error occurred").dict()
    return JSONResponse(status_code=exc.status_code, content={"error": error_detail})


@app.exception_handler(Exception)
async def handle_unexpected_exception(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception")
    return JSONResponse(status_code=500, content={"error": "Internal Server Error"})
