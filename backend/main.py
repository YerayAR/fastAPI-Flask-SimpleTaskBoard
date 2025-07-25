"""Application entry point for the FastAPI example project."""

# FastAPI provides the web framework used throughout the project
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import controllers that expose authentication and item related endpoints
from .controllers import auth, items, tasks

# Database metadata and engine are required to create tables on startup
from .config.database import Base, engine

# Create the FastAPI application instance
app = FastAPI()

# Allow cross-origin requests so the Flask frontend can reach the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    """Basic health check endpoint."""
    return {"message": "Hello World"}

