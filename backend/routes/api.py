import logging
import os
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError
from pymongo.errors import PyMongoError

from ..services.ai import AIServiceError

from ..auth import get_current_user, require_roles
from ..errors import ErrorResponse
from ..models import (
    Article,
    ArticleCreate,
    ArticleUpdate,
    Category,
    Page,
    PageCreate,
    PageUpdate,
    ToolCall,
    ToolResponse,
    User,
    UserRole,
    RegisterUserRequest,
)
from ..services.db import db
from ..services.tools import tool_registry

# Public routes don't require authentication
public_router = APIRouter(prefix="/api")

# Protected routes share the authentication dependency
protected_router = APIRouter(prefix="/api", dependencies=[Depends(get_current_user)])

logger = logging.getLogger(__name__)


@protected_router.post("/mcp/dispatch", response_model=ToolResponse)
async def dispatch_tool(tool_call: ToolCall, user: User = Depends(get_current_user)):
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
        return ToolResponse(success=False, error="Tool execution failed")
    except (AIServiceError, PyMongoError, ValidationError) as exc:
        logger.warning("Tool execution failed: %s", exc)
        return ToolResponse(success=False, error="Tool execution failed")


@protected_router.get("/mcp/tools")
async def list_tools(user: User = Depends(get_current_user)):
    """List available MCP tools."""
    return {"tools": tool_registry.list_tools()}


@protected_router.post("/auth/register")
async def register_user(
    registration: RegisterUserRequest,
    user: User = Depends(get_current_user),
    _role_check: None = require_roles(UserRole.ADMIN),
):
    """Register a new user after Firebase authentication."""
    try:
        existing_user = await db.users.find_one(
            {"firebase_uid": registration.firebase_uid}
        )
        if existing_user:
            return {"message": "User already exists", "user_id": existing_user["id"]}

        user_data = {
            "firebase_uid": registration.firebase_uid,
            "email": registration.email,
            "name": registration.name,
            "role": UserRole.VIEWER,
        }

        user = User(**user_data)
        await db.users.insert_one(user.dict())
        return {"message": "User registered successfully", "user_id": user.id}
    except (ValidationError, PyMongoError) as exc:
        logger.warning("User registration failed: %s", exc)
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(
                message="Registration failed", code="registration_failed"
            ).dict(),
        )


@protected_router.get("/auth/me")
async def get_current_user_info(user: User = Depends(get_current_user)):
    """Get current user information."""
    return user


@protected_router.get("/pages", response_model=List[Page])
async def get_pages(user: User = Depends(get_current_user)):
    """Get all pages."""
    pages = await db.pages.find().to_list(1000)
    return [Page(**page) for page in pages]


@protected_router.get("/pages/{page_id}", response_model=Page)
async def get_page(page_id: str, user: User = Depends(get_current_user)):
    """Get a specific page."""
    page = await db.pages.find_one({"id": page_id})
    if not page:
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(
                message="Page not found", code="page_not_found"
            ).dict(),
        )
    return Page(**page)


@protected_router.post(
    "/pages",
    response_model=Page,
)
async def create_page(
    page: PageCreate,
    user: User = Depends(get_current_user),
    _role_check: None = require_roles(UserRole.ADMIN, UserRole.EDITOR, UserRole.AUTHOR),
):
    """Create a new page."""
    page_data = page.dict()
    page_data["slug"] = page_data.get("slug") or page_data["title"].lower().replace(
        " ", "-"
    )
    page_data["author_id"] = user.id
    new_page = Page(**page_data)
    await db.pages.insert_one(new_page.dict())
    return new_page


@protected_router.put(
    "/pages/{page_id}",
    response_model=Page,
)
async def update_page(
    page_id: str,
    page_update: PageUpdate,
    user: User = Depends(get_current_user),
    _role_check: None = require_roles(UserRole.ADMIN, UserRole.EDITOR, UserRole.AUTHOR),
):
    """Update a page."""
    page_doc = await db.pages.find_one({"id": page_id})
    if not page_doc:
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(
                message="Page not found", code="page_not_found"
            ).dict(),
        )

    if user.role == UserRole.AUTHOR and page_doc.get("author_id") != user.id:
        raise HTTPException(
            status_code=403,
            detail=ErrorResponse(
                message="Insufficient permissions", code="insufficient_role"
            ).dict(),
        )

    update_data = page_update.dict(exclude_unset=True)
    if "title" in update_data and "slug" not in update_data:
        update_data["slug"] = update_data["title"].lower().replace(" ", "-")
    update_data["updated_at"] = datetime.utcnow()
    await db.pages.update_one({"id": page_id}, {"$set": update_data})
    page_doc.update(update_data)
    return Page(**page_doc)


@protected_router.delete(
    "/pages/{page_id}",
)
async def delete_page(
    page_id: str,
    user: User = Depends(get_current_user),
    _role_check: None = require_roles(UserRole.ADMIN, UserRole.EDITOR),
):
    """Delete a page."""
    result = await db.pages.delete_one({"id": page_id})
    if not getattr(result, "deleted_count", 0):
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(
                message="Page not found", code="page_not_found"
            ).dict(),
        )
    return {"message": "Page deleted"}


@protected_router.get("/articles", response_model=List[Article])
async def get_articles(user: User = Depends(get_current_user)):
    """Get all articles."""
    articles = await db.articles.find().to_list(1000)
    return [Article(**article) for article in articles]


@protected_router.get("/articles/{article_id}", response_model=Article)
async def get_article(article_id: str, user: User = Depends(get_current_user)):
    """Get a specific article."""
    article = await db.articles.find_one({"id": article_id})
    if not article:
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(
                message="Article not found", code="article_not_found"
            ).dict(),
        )
    return Article(**article)


@protected_router.post(
    "/articles",
    response_model=Article,
)
async def create_article(
    article: ArticleCreate,
    user: User = Depends(get_current_user),
    _role_check: None = require_roles(UserRole.ADMIN, UserRole.EDITOR, UserRole.AUTHOR),
):
    """Create a new article."""
    article_data = article.dict()
    article_data["slug"] = article_data.get("slug") or article_data[
        "title"
    ].lower().replace(" ", "-")
    article_data["author_id"] = user.id
    new_article = Article(**article_data)
    await db.articles.insert_one(new_article.dict())
    return new_article


@protected_router.put(
    "/articles/{article_id}",
    response_model=Article,
)
async def update_article(
    article_id: str,
    article_update: ArticleUpdate,
    user: User = Depends(get_current_user),
    _role_check: None = require_roles(UserRole.ADMIN, UserRole.EDITOR, UserRole.AUTHOR),
):
    """Update an article."""
    article_doc = await db.articles.find_one({"id": article_id})
    if not article_doc:
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(
                message="Article not found", code="article_not_found"
            ).dict(),
        )

    if user.role == UserRole.AUTHOR and article_doc.get("author_id") != user.id:
        raise HTTPException(
            status_code=403,
            detail=ErrorResponse(
                message="Insufficient permissions", code="insufficient_role"
            ).dict(),
        )

    update_data = article_update.dict(exclude_unset=True)
    if "title" in update_data and "slug" not in update_data:
        update_data["slug"] = update_data["title"].lower().replace(" ", "-")
    update_data["updated_at"] = datetime.utcnow()
    await db.articles.update_one({"id": article_id}, {"$set": update_data})
    article_doc.update(update_data)
    return Article(**article_doc)


@protected_router.delete(
    "/articles/{article_id}",
)
async def delete_article(
    article_id: str,
    user: User = Depends(get_current_user),
    _role_check: None = require_roles(UserRole.ADMIN, UserRole.EDITOR),
):
    """Delete an article."""
    result = await db.articles.delete_one({"id": article_id})
    if not getattr(result, "deleted_count", 0):
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(
                message="Article not found", code="article_not_found"
            ).dict(),
        )
    return {"message": "Article deleted"}


@protected_router.get("/categories", response_model=List[Category])
async def get_categories(user: User = Depends(get_current_user)):
    """Get all categories."""
    categories = await db.categories.find().to_list(1000)
    return [Category(**category) for category in categories]


@protected_router.get("/dashboard/stats")
async def get_dashboard_stats(
    user: User = Depends(get_current_user),
    _role_check: None = require_roles(UserRole.ADMIN, UserRole.EDITOR),
):
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


@public_router.get("/config/firebase")
async def get_firebase_config() -> dict:
    """Return Firebase initialization settings."""
    return {
        "apiKey": os.getenv("FIREBASE_API_KEY", ""),
        "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN", ""),
        "projectId": os.getenv("FIREBASE_PROJECT_ID", ""),
        "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET", ""),
        "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID", ""),
        "appId": os.getenv("FIREBASE_APP_ID", ""),
    }


@public_router.get("/health")
async def health_check() -> dict:
    return {"status": "healthy", "timestamp": datetime.utcnow()}


__all__ = ["public_router", "protected_router"]
