from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth as firebase_auth

from .models import User
from .services.db import db

security = HTTPBearer()


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
            raise HTTPException(status_code=404, detail="User not found")

        user = User(**user_doc)
        request.state.user = user
        return user
    except Exception as e:  # pragma: no cover - network / firebase failures
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")


def current_user(request: Request) -> User:
    """Retrieve the authenticated user from the request state."""
    user = getattr(request.state, "user", None)
    if user is None:
        raise HTTPException(status_code=401, detail="User not authenticated")
    return user
