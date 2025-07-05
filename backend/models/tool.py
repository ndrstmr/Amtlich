from typing import Any, Dict, Optional

from pydantic import BaseModel


class ToolCall(BaseModel):
    tool: str
    args: Dict[str, Any]


class ToolResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
