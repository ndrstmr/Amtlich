import logging
import os
import json
from pathlib import Path

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import firebase_admin
from firebase_admin import credentials


ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

mongo_url = os.environ["MONGO_URL"]
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ["DB_NAME"]]

logger = logging.getLogger(__name__)


async def ensure_indexes() -> None:
    """Create required MongoDB indexes if supported."""
    try:
        users = getattr(db, "users", None)
        if users and hasattr(users, "create_index"):
            await users.create_index("firebase_uid", unique=True)
            await users.create_index("id", unique=True)
            logger.info("MongoDB indexes ensured")
    except Exception as e:  # pragma: no cover - index creation best effort
        logger.exception("Failed to create indexes: %s", e)


def init_firebase() -> None:
    """Initialize Firebase Admin SDK if credentials are provided."""
    try:
        firebase_service_account = json.loads(
            os.environ.get("FIREBASE_SERVICE_ACCOUNT", "{}")
        )
        if firebase_service_account:
            cred = credentials.Certificate(firebase_service_account)
            firebase_admin.initialize_app(cred)
            logger.info("Firebase Admin SDK initialized successfully")
        else:
            logger.info("Firebase credentials not found - using placeholder mode")
    except Exception as e:
        logger.exception("Firebase initialization failed: %s", e)
