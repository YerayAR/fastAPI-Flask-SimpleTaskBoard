"""Application entry point for the FastAPI example project."""

import os
from typing import List

# FastAPI provides the web framework used throughout the project
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse
import time

# Import controllers that expose authentication and item related endpoints
from .controllers import auth, items, tasks

# Database metadata and engine are required to create tables on startup
from .config.database import Base, engine

# Security configuration
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS", 
    "http://localhost:3000,http://localhost:5000,http://127.0.0.1:5000"
).split(",")

ALLOWED_HOSTS = os.getenv(
    "ALLOWED_HOSTS",
    "localhost,127.0.0.1,0.0.0.0"
).split(",")

# Create the FastAPI application instance with security metadata
app = FastAPI(
    title="SimpleTaskBoard API",
    description="Secure Task Board API with authentication",
    version="1.0.0",
    docs_url="/docs" if os.getenv("ENABLE_DOCS", "false").lower() == "true" else None,
    redoc_url="/redoc" if os.getenv("ENABLE_DOCS", "false").lower() == "true" else None,
)

# Security middleware - Trusted Host (prevents Host header attacks)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=ALLOWED_HOSTS
)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Add security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self'; frame-ancestors 'none'"
    response.headers["X-Process-Time"] = str(process_time)
    
    # Remove server headers
    response.headers.pop("server", None)
    
    return response

# CORS middleware with restricted origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
    expose_headers=["X-Process-Time"]
)


@app.on_event("startup")
def on_startup() -> None:
    """Create database tables when the application starts."""
    Base.metadata.create_all(bind=engine)

# Register API routers for authentication and item resources
app.include_router(auth.router)
app.include_router(items.router)
app.include_router(tasks.router)


@app.get("/")
async def read_root() -> dict:
    """Root endpoint with API information."""
    return {
        "message": "SimpleTaskBoard API",
        "version": "1.0.0",
        "status": "healthy",
        "docs_url": "/docs" if os.getenv("ENABLE_DOCS", "false").lower() == "true" else None
    }


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint for container orchestration."""
    return {
        "status": "healthy",
        "timestamp": int(time.time()),
        "version": "1.0.0"
    }

