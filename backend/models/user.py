from enum import Enum
from datetime import datetime
from typing import Optional
import uuid

from pydantic import BaseModel, Field


class UserRole(str, Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    AUTHOR = "author"
    VIEWER = "viewer"


class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    firebase_uid: str
    email: str
    name: str
    role: UserRole
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
