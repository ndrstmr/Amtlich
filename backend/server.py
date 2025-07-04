from fastapi import FastAPI, APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
from abc import ABC, abstractmethod
import json
from enum import Enum
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Firebase Admin SDK initialization
try:
    firebase_service_account = json.loads(os.environ.get('FIREBASE_SERVICE_ACCOUNT', '{}'))
    if firebase_service_account:
        cred = credentials.Certificate(firebase_service_account)
        firebase_admin.initialize_app(cred)
        print("Firebase Admin SDK initialized successfully")
    else:
        print("Firebase credentials not found - using placeholder mode")
except Exception as e:
    print(f"Firebase initialization failed: {e}")

# Create the main app
app = FastAPI(title="MCP-CMS", description="Model Context Protocol based Content Management System")
api_router = APIRouter(prefix="/api")

# Security
security = HTTPBearer()

# User Roles
class UserRole(str, Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    AUTHOR = "author"
    VIEWER = "viewer"

# Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    firebase_uid: str
    email: str
    name: str
    role: UserRole
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

class Page(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    slug: str
    content: str
    meta_description: Optional[str] = None
    parent_id: Optional[str] = None
    author_id: str
    status: str = "draft"  # draft, published, archived
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    published_at: Optional[datetime] = None

class Article(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    slug: str
    content: str
    excerpt: Optional[str] = None
    featured_image: Optional[str] = None
    author_id: str
    category_id: Optional[str] = None
    tags: List[str] = []
    status: str = "draft"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    published_at: Optional[datetime] = None

class Category(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    slug: str
    description: Optional[str] = None
    parent_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class MediaFile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    url: str
    uploaded_by: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

# MCP Tool Call Models
class ToolCall(BaseModel):
    tool: str
    args: Dict[str, Any]

class ToolResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Verify Firebase token and get user"""
    try:
        # Verify Firebase token
        decoded_token = firebase_auth.verify_id_token(credentials.credentials)
        firebase_uid = decoded_token['uid']
        
        # Get user from database
        user_doc = await db.users.find_one({"firebase_uid": firebase_uid})
        if not user_doc:
            raise HTTPException(status_code=404, detail="User not found")
        
        return User(**user_doc)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")

# MCP Tool Interface
class Tool(ABC):
    @abstractmethod
    def get_name(self) -> str:
        pass
    
    @abstractmethod
    async def execute(self, args: Dict[str, Any], user: User) -> Dict[str, Any]:
        pass

# MCP Tools Implementation
class CreatePageTool(Tool):
    def get_name(self) -> str:
        return "createPage"
    
    async def execute(self, args: Dict[str, Any], user: User) -> Dict[str, Any]:
        # Check permissions
        if user.role not in [UserRole.ADMIN, UserRole.EDITOR, UserRole.AUTHOR]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        page_data = {
            "title": args.get("title"),
            "slug": args.get("slug", args.get("title", "").lower().replace(" ", "-")),
            "content": args.get("content", ""),
            "meta_description": args.get("meta_description"),
            "parent_id": args.get("parent_id"),
            "author_id": user.id,
            "status": args.get("status", "draft")
        }
        
        page = Page(**page_data)
        await db.pages.insert_one(page.dict())
        return {"page_id": page.id, "message": "Page created successfully"}

class CreateArticleTool(Tool):
    def get_name(self) -> str:
        return "createArticle"
    
    async def execute(self, args: Dict[str, Any], user: User) -> Dict[str, Any]:
        if user.role not in [UserRole.ADMIN, UserRole.EDITOR, UserRole.AUTHOR]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        article_data = {
            "title": args.get("title"),
            "slug": args.get("slug", args.get("title", "").lower().replace(" ", "-")),
            "content": args.get("content", ""),
            "excerpt": args.get("excerpt"),
            "featured_image": args.get("featured_image"),
            "author_id": user.id,
            "category_id": args.get("category_id"),
            "tags": args.get("tags", []),
            "status": args.get("status", "draft")
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
            raise HTTPException(status_code=400, detail="page_id is required")
        
        # Check if page exists and user has permission
        page_doc = await db.pages.find_one({"id": page_id})
        if not page_doc:
            raise HTTPException(status_code=404, detail="Page not found")
        
        if user.role not in [UserRole.ADMIN, UserRole.EDITOR] and page_doc.get("author_id") != user.id:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        update_data = {k: v for k, v in args.items() if k != "page_id" and v is not None}
        update_data["updated_at"] = datetime.utcnow()
        
        await db.pages.update_one({"id": page_id}, {"$set": update_data})
        return {"message": "Page updated successfully"}

class CreateUserTool(Tool):
    def get_name(self) -> str:
        return "createUser"
    
    async def execute(self, args: Dict[str, Any], user: User) -> Dict[str, Any]:
        if user.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Only admins can create users")
        
        user_data = {
            "firebase_uid": args.get("firebase_uid"),
            "email": args.get("email"),
            "name": args.get("name"),
            "role": args.get("role", "viewer")
        }
        
        new_user = User(**user_data)
        await db.users.insert_one(new_user.dict())
        return {"user_id": new_user.id, "message": "User created successfully"}

# Tool Registry
class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
    
    def register(self, tool: Tool):
        self.tools[tool.get_name()] = tool
    
    def get_tool(self, name: str) -> Optional[Tool]:
        return self.tools.get(name)
    
    def list_tools(self) -> List[str]:
        return list(self.tools.keys())

# Initialize tool registry
tool_registry = ToolRegistry()
tool_registry.register(CreatePageTool())
tool_registry.register(CreateArticleTool())
tool_registry.register(UpdatePageTool())
tool_registry.register(CreateUserTool())

# MCP Endpoints
@api_router.post("/mcp/dispatch", response_model=ToolResponse)
async def dispatch_tool(tool_call: ToolCall, user: User = Depends(get_current_user)):
    """Main MCP endpoint for tool dispatching"""
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

@api_router.get("/mcp/tools")
async def list_tools(user: User = Depends(get_current_user)):
    """List available MCP tools"""
    return {"tools": tool_registry.list_tools()}

# Authentication endpoints
@api_router.post("/auth/register")
async def register_user(firebase_uid: str, email: str, name: str, role: str = "viewer"):
    """Register a new user after Firebase authentication"""
    try:
        # Check if user already exists
        existing_user = await db.users.find_one({"firebase_uid": firebase_uid})
        if existing_user:
            return {"message": "User already exists", "user_id": existing_user["id"]}
        
        user_data = {
            "firebase_uid": firebase_uid,
            "email": email,
            "name": name,
            "role": role
        }
        
        user = User(**user_data)
        await db.users.insert_one(user.dict())
        return {"message": "User registered successfully", "user_id": user.id}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@api_router.get("/auth/me")
async def get_current_user_info(user: User = Depends(get_current_user)):
    """Get current user information"""
    return user

# Content Management endpoints
@api_router.get("/pages", response_model=List[Page])
async def get_pages(user: User = Depends(get_current_user)):
    """Get all pages"""
    pages = await db.pages.find().to_list(1000)
    return [Page(**page) for page in pages]

@api_router.get("/pages/{page_id}", response_model=Page)
async def get_page(page_id: str, user: User = Depends(get_current_user)):
    """Get a specific page"""
    page = await db.pages.find_one({"id": page_id})
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return Page(**page)

@api_router.get("/articles", response_model=List[Article])
async def get_articles(user: User = Depends(get_current_user)):
    """Get all articles"""
    articles = await db.articles.find().to_list(1000)
    return [Article(**article) for article in articles]

@api_router.get("/articles/{article_id}", response_model=Article)
async def get_article(article_id: str, user: User = Depends(get_current_user)):
    """Get a specific article"""
    article = await db.articles.find_one({"id": article_id})
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return Article(**article)

@api_router.get("/categories", response_model=List[Category])
async def get_categories(user: User = Depends(get_current_user)):
    """Get all categories"""
    categories = await db.categories.find().to_list(1000)
    return [Category(**category) for category in categories]

# Dashboard endpoints
@api_router.get("/dashboard/stats")
async def get_dashboard_stats(user: User = Depends(get_current_user)):
    """Get dashboard statistics"""
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

# Include the router in the main app
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
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}