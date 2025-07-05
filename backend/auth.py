import logging

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth as firebase_auth

from .errors import ErrorResponse
from .models import User, UserRole
from .services.db import db

security = HTTPBearer()
logger = logging.getLogger(__name__)


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    """Verify Firebase token, store and return the current user."""
    try:
        decoded_token = firebase_auth.verify_id_token(credentials.credentials)
        firebase_uid = decoded_token["uid"]

        user_doc = await db.users.find_one({"firebase_uid": firebase_uid})
        if not user_doc:
            raise HTTPException(
                status_code=404,
                detail=ErrorResponse(
                    message="User not found", code="user_not_found"
                ).dict(),
            )

        user = User(**user_doc)
        request.state.user = user
        return user
    except Exception as e:  # pragma: no cover - network / firebase failures
        logger.exception("Authentication failed")
        raise HTTPException(
            status_code=401,
            detail=ErrorResponse(
                message=f"Authentication failed: {str(e)}", code="auth_failed"
            ).dict(),
        )


def current_user(request: Request) -> User:
    """Retrieve the authenticated user from the request state."""
    user = getattr(request.state, "user", None)
    if user is None:
        raise HTTPException(
            status_code=401,
            detail=ErrorResponse(
                message="User not authenticated", code="not_authenticated"
            ).dict(),
        )
    return user


def require_roles(*roles: UserRole):
    """Dependency to ensure the user has one of the required roles."""

    async def _role_checker(request: Request) -> None:
        user = current_user(request)
        if user.role not in roles:
            raise HTTPException(
                status_code=403,
                detail=ErrorResponse(
                    message="Insufficient permissions", code="insufficient_role"
                ).dict(),
            )

    return Depends(_role_checker)
