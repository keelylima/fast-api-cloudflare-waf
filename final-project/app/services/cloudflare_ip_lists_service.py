import httpx
from fastapi import HTTPException
from app.core.config import settings
from app.services.cloudflare_service import get_headers


async def list_ip_lists():
    headers = get_headers()

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.CLOUDFLARE_BASE_URL}/accounts/{settings.CLOUDFLARE_ACCOUNT_ID}/rules/lists",
            headers=headers
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.json()
        )

    return response.json().get("result", [])
