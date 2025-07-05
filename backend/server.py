import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from .routes.api import protected_router, public_router
from .services.db import client, init_firebase

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "")
allowed_origins = [
    origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()
]
if not allowed_origins:
    allowed_origins = ["*"]

app = FastAPI(
    title="MCP-CMS",
    description="Model Context Protocol based Content Management System",
)

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
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize Firebase when the module is imported
init_firebase()


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
