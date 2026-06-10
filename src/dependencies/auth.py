from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from src.core.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def require_api_key(
    api_key: str = Depends(api_key_header),
) -> None:
    expected_api_key = settings.security.api_key
    if not expected_api_key or expected_api_key == "YOUR_API_KEY":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server API key is not configured",
        )

    if not api_key or api_key != expected_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
