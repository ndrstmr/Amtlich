from datetime import datetime
from typing import List, Optional
import uuid

from pydantic import BaseModel, Field


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
