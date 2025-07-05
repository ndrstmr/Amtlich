from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import auth as firebase_auth

from .db import db
from ..models import User

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    """Verify Firebase token and get user."""
    try:
        decoded_token = firebase_auth.verify_id_token(credentials.credentials)
        firebase_uid = decoded_token['uid']

        user_doc = await db.users.find_one({"firebase_uid": firebase_uid})
        if not user_doc:
            raise HTTPException(status_code=404, detail="User not found")

        return User(**user_doc)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")
