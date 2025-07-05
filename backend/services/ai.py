import asyncio
import logging
import os
from typing import Any, Dict

import httpx

logger = logging.getLogger(__name__)


class AIServiceError(Exception):
    """Raised when the AI service fails after retries."""


class AIService:
    """Simple service layer for external AI requests with retries and timeouts."""

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        timeout: float = 10.0,
        retries: int = 3,
    ) -> None:
        self.base_url = base_url or os.getenv("AI_BASE_URL", "")
        self.api_key = api_key or os.getenv("AI_API_KEY", "")
        self.timeout = timeout
        self.retries = retries

    async def post(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """POST to the AI service with retries."""
        url = f"{self.base_url}{endpoint}"
        last_exc: Exception | None = None
        for attempt in range(1, self.retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        url,
                        json=payload,
                        headers={"Authorization": f"Bearer {self.api_key}"},
                    )
                    response.raise_for_status()
                    return response.json()
            except Exception as exc:  # pragma: no cover - network failures mocked
                last_exc = exc
                logger.warning(
                    "AI request failed (attempt %s/%s): %s", attempt, self.retries, exc
                )
                if attempt < self.retries:
                    await asyncio.sleep(0.5 * attempt)
        raise AIServiceError(str(last_exc)) from last_exc
