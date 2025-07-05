from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from ..models import (
    Page,
    Article,
    Category,
    ToolCall,
    ToolResponse,
    User,
)
from ..services.auth import get_current_user
from ..services.tools import tool_registry
from ..services.db import db

router = APIRouter(prefix="/api")


@router.post("/mcp/dispatch", response_model=ToolResponse)
async def dispatch_tool(tool_call: ToolCall, user: User = Depends(get_current_user)):
    """Main MCP endpoint for tool dispatching."""
    try:
        tool = tool_registry.get_tool(tool_call.tool)
        if not tool:
            return ToolResponse(success=False, error=f"Tool '{tool_call.tool}' not found")

        result = await tool.execute(tool_call.args, user)
        return ToolResponse(success=True, data=result)
    except HTTPException as e:
        return ToolResponse(success=False, error=str(e.detail))
    except Exception as e:
        return ToolResponse(success=False, error=str(e))


@router.get("/mcp/tools")
async def list_tools(user: User = Depends(get_current_user)):
    """List available MCP tools."""
    return {"tools": tool_registry.list_tools()}


@router.post("/auth/register")
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
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/auth/me")
async def get_current_user_info(user: User = Depends(get_current_user)):
    """Get current user information."""
    return user


@router.get("/pages", response_model=List[Page])
async def get_pages(user: User = Depends(get_current_user)):
    """Get all pages."""
    pages = await db.pages.find().to_list(1000)
    return [Page(**page) for page in pages]


@router.get("/pages/{page_id}", response_model=Page)
async def get_page(page_id: str, user: User = Depends(get_current_user)):
    """Get a specific page."""
    page = await db.pages.find_one({"id": page_id})
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return Page(**page)


@router.get("/articles", response_model=List[Article])
async def get_articles(user: User = Depends(get_current_user)):
    """Get all articles."""
    articles = await db.articles.find().to_list(1000)
    return [Article(**article) for article in articles]


@router.get("/articles/{article_id}", response_model=Article)
async def get_article(article_id: str, user: User = Depends(get_current_user)):
    """Get a specific article."""
    article = await db.articles.find_one({"id": article_id})
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return Article(**article)


@router.get("/categories", response_model=List[Category])
async def get_categories(user: User = Depends(get_current_user)):
    """Get all categories."""
    categories = await db.categories.find().to_list(1000)
    return [Category(**category) for category in categories]


@router.get("/dashboard/stats")
async def get_dashboard_stats(user: User = Depends(get_current_user)):
    """Get dashboard statistics."""
    stats = {
        "total_pages": await db.pages.count_documents({}),
        "total_articles": await db.articles.count_documents({}),
        "total_users": await db.users.count_documents({}),
        "published_pages": await db.pages.count_documents({"status": "published"}),
        "published_articles": await db.articles.count_documents({"status": "published"}),
        "draft_pages": await db.pages.count_documents({"status": "draft"}),
        "draft_articles": await db.articles.count_documents({"status": "draft"}),
    }
    return stats


@router.get("/health")
async def health_check() -> dict:
    return {"status": "healthy", "timestamp": datetime.utcnow()}
