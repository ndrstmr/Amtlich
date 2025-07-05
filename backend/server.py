from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
import logging

from .services.db import client, init_firebase
from .routes.api import router as api_router

app = FastAPI(
    title="MCP-CMS",
    description="Model Context Protocol based Content Management System",
)

# Register API routes
app.include_router(api_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
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
