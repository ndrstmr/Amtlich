from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import HTTPException

from ..errors import ErrorResponse
from ..models import Article, Category, Page, User, UserRole
from .db import db


class Tool(ABC):
    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    async def execute(self, args: Dict[str, Any], user: User) -> Dict[str, Any]:
        pass


class CreatePageTool(Tool):
    def get_name(self) -> str:
        return "createPage"

    async def execute(self, args: Dict[str, Any], user: User) -> Dict[str, Any]:
        if user.role not in [UserRole.ADMIN, UserRole.EDITOR, UserRole.AUTHOR]:
            raise HTTPException(
                status_code=403,
                detail=ErrorResponse(
                    message="Insufficient permissions", code="insufficient_role"
                ).dict(),
            )

        page_data = {
            "title": args.get("title"),
            "slug": args.get("slug", args.get("title", "").lower().replace(" ", "-")),
            "content": args.get("content", ""),
            "meta_description": args.get("meta_description"),
            "parent_id": args.get("parent_id"),
            "author_id": user.id,
            "status": args.get("status", "draft"),
        }

        page = Page(**page_data)
        await db.pages.insert_one(page.dict())
        return {"page_id": page.id, "message": "Page created successfully"}


class CreateArticleTool(Tool):
    def get_name(self) -> str:
        return "createArticle"

    async def execute(self, args: Dict[str, Any], user: User) -> Dict[str, Any]:
        if user.role not in [UserRole.ADMIN, UserRole.EDITOR, UserRole.AUTHOR]:
            raise HTTPException(
                status_code=403,
                detail=ErrorResponse(
                    message="Insufficient permissions", code="insufficient_role"
                ).dict(),
            )

        article_data = {
            "title": args.get("title"),
            "slug": args.get("slug", args.get("title", "").lower().replace(" ", "-")),
            "content": args.get("content", ""),
            "excerpt": args.get("excerpt"),
            "featured_image": args.get("featured_image"),
            "author_id": user.id,
            "category_id": args.get("category_id"),
            "tags": args.get("tags", []),
            "status": args.get("status", "draft"),
        }

        article = Article(**article_data)
        await db.articles.insert_one(article.dict())
        return {"article_id": article.id, "message": "Article created successfully"}


class UpdatePageTool(Tool):
    def get_name(self) -> str:
        return "updatePage"

    async def execute(self, args: Dict[str, Any], user: User) -> Dict[str, Any]:
        page_id = args.get("page_id")
        if not page_id:
            raise HTTPException(
                status_code=400,
                detail=ErrorResponse(
                    message="page_id is required", code="missing_page_id"
                ).dict(),
            )

        page_doc = await db.pages.find_one({"id": page_id})
        if not page_doc:
            raise HTTPException(
                status_code=404,
                detail=ErrorResponse(
                    message="Page not found", code="page_not_found"
                ).dict(),
            )

        if (
            user.role not in [UserRole.ADMIN, UserRole.EDITOR]
            and page_doc.get("author_id") != user.id
        ):
            raise HTTPException(
                status_code=403,
                detail=ErrorResponse(
                    message="Insufficient permissions", code="insufficient_role"
                ).dict(),
            )

        update_data = {
            k: v for k, v in args.items() if k != "page_id" and v is not None
        }
        update_data["updated_at"] = datetime.utcnow()

        await db.pages.update_one({"id": page_id}, {"$set": update_data})
        return {"message": "Page updated successfully"}


class CreateUserTool(Tool):
    def get_name(self) -> str:
        return "createUser"

    async def execute(self, args: Dict[str, Any], user: User) -> Dict[str, Any]:
        if user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=403,
                detail=ErrorResponse(
                    message="Only admins can create users", code="insufficient_role"
                ).dict(),
            )

        user_data = {
            "firebase_uid": args.get("firebase_uid"),
            "email": args.get("email"),
            "name": args.get("name"),
            "role": args.get("role", "viewer"),
        }

        new_user = User(**user_data)
        await db.users.insert_one(new_user.dict())
        return {"user_id": new_user.id, "message": "User created successfully"}


class ToolRegistry:
    def __init__(self) -> None:
        self.tools: Dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self.tools[tool.get_name()] = tool

    def get_tool(self, name: str) -> Optional[Tool]:
        return self.tools.get(name)

    def list_tools(self) -> List[str]:
        return list(self.tools.keys())


# Initialize registry with default tools
tool_registry = ToolRegistry()
tool_registry.register(CreatePageTool())
tool_registry.register(CreateArticleTool())
tool_registry.register(UpdatePageTool())
tool_registry.register(CreateUserTool())
