from datetime import datetime
from typing import List

import logging
from fastapi import APIRouter, Depends, HTTPException, Request

from ..models import (
    Page,
    Article,
    Category,
    ToolCall,
    ToolResponse,
    User,
)
from ..auth import current_user, get_current_user
from ..services.tools import tool_registry
from ..services.db import db

# Public routes don't require authentication
public_router = APIRouter(prefix="/api")

# Protected routes share the authentication dependency
protected_router = APIRouter(prefix="/api", dependencies=[Depends(get_current_user)])

logger = logging.getLogger(__name__)


@protected_router.post("/mcp/dispatch", response_model=ToolResponse)
async def dispatch_tool(tool_call: ToolCall, request: Request):
    user = current_user(request)
    """Main MCP endpoint for tool dispatching."""
    try:
        tool = tool_registry.get_tool(tool_call.tool)
        if not tool:
            return ToolResponse(
                success=False, error=f"Tool '{tool_call.tool}' not found"
            )

        result = await tool.execute(tool_call.args, user)
        return ToolResponse(success=True, data=result)
    except HTTPException as e:
        logger.warning("Tool dispatch error: %s", e.detail)
        return ToolResponse(success=False, error=str(e.detail))
    except Exception as e:
        logger.exception("Unexpected error during tool dispatch")
        return ToolResponse(success=False, error=str(e))


@protected_router.get("/mcp/tools")
async def list_tools(request: Request):
    user = current_user(request)
    """List available MCP tools."""
    return {"tools": tool_registry.list_tools()}


@public_router.post("/auth/register")
async def register_user(firebase_uid: str, email: str, name: str, role: str = "viewer"):
    """Register a new user after Firebase authentication."""
    try:
        existing_user = await db.users.find_one({"firebase_uid": firebase_uid})
        if existing_user:
            return {"message": "User already exists", "user_id": existing_user["id"]}

        user_data = {
            "firebase_uid": firebase_uid,
            "email": email,
            "name": name,
            "role": role,
        }

        user = User(**user_data)
        await db.users.insert_one(user.dict())
        return {"message": "User registered successfully", "user_id": user.id}
    except Exception as e:
        logger.exception("User registration failed")
        raise HTTPException(status_code=400, detail=str(e))


@protected_router.get("/auth/me")
async def get_current_user_info(request: Request):
    """Get current user information."""
    return current_user(request)


@protected_router.get("/pages", response_model=List[Page])
async def get_pages(request: Request):
    user = current_user(request)
    """Get all pages."""
    pages = await db.pages.find().to_list(1000)
    return [Page(**page) for page in pages]


@protected_router.get("/pages/{page_id}", response_model=Page)
async def get_page(page_id: str, request: Request):
    user = current_user(request)
    """Get a specific page."""
    page = await db.pages.find_one({"id": page_id})
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return Page(**page)


@protected_router.get("/articles", response_model=List[Article])
async def get_articles(request: Request):
    user = current_user(request)
    """Get all articles."""
    articles = await db.articles.find().to_list(1000)
    return [Article(**article) for article in articles]


@protected_router.get("/articles/{article_id}", response_model=Article)
async def get_article(article_id: str, request: Request):
    user = current_user(request)
    """Get a specific article."""
    article = await db.articles.find_one({"id": article_id})
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return Article(**article)


@protected_router.get("/categories", response_model=List[Category])
async def get_categories(request: Request):
    user = current_user(request)
    """Get all categories."""
    categories = await db.categories.find().to_list(1000)
    return [Category(**category) for category in categories]


@protected_router.get("/dashboard/stats")
async def get_dashboard_stats(request: Request):
    user = current_user(request)
    """Get dashboard statistics."""
    stats = {
        "total_pages": await db.pages.count_documents({}),
        "total_articles": await db.articles.count_documents({}),
        "total_users": await db.users.count_documents({}),
        "published_pages": await db.pages.count_documents({"status": "published"}),
        "published_articles": await db.articles.count_documents(
            {"status": "published"}
        ),
        "draft_pages": await db.pages.count_documents({"status": "draft"}),
        "draft_articles": await db.articles.count_documents({"status": "draft"}),
    }
    return stats


@public_router.get("/health")
async def health_check() -> dict:
    return {"status": "healthy", "timestamp": datetime.utcnow()}


__all__ = ["public_router", "protected_router"]
