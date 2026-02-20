import httpx
from fastapi import HTTPException
from app.core.config import settings

def get_headers():
    if not settings.CLOUDFLARE_API_TOKEN:
        raise HTTPException(
            status_code=500,
            detail="Cloudflare token not configured"
        )

    return {
        "Authorization": f"Bearer {settings.CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }

async def list_ip_lists(account_id: str):
    headers = get_headers()

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.CLOUDFLARE_BASE_URL}/accounts/{account_id}/rules/lists",
            headers=headers
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.json()
        )

    return response.json().get("result", [])

