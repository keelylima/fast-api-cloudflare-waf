import httpx
from fastapi import HTTPException
from app.core.config import settings
from app.schemas.rules import CreateIPListRequest, IPItem

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


async def list_ip_list_items(account_id: str, list_id: str):
    headers = get_headers()

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.CLOUDFLARE_BASE_URL}/accounts/{account_id}/rules/lists/{list_id}/items",
            headers=headers
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.json()
        )

    return response.json().get("result", [])

async def create_ip_list(account_id: str, data: CreateIPListRequest):
    headers = get_headers()

    payload = {
        "name": data.name,
        "kind": "ip",
        "description": data.description
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.CLOUDFLARE_BASE_URL}/accounts/{account_id}/rules/lists",
            headers=headers,
            json=payload
        )

    if response.status_code not in (200, 201):
        raise HTTPException(
            status_code=response.status_code,
            detail=response.json()
        )

    return response.json().get("result")

async def delete_ip_list(account_id: str, list_id: str):
    headers = get_headers()

    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{settings.CLOUDFLARE_BASE_URL}/accounts/{account_id}/rules/lists/{list_id}",
            headers=headers
        )

    if response.status_code not in (200, 204):
        raise HTTPException(
            status_code=response.status_code,
            detail=response.json()
        )

    return {"message": "IP list deleted successfully"}


async def add_ip_to_list(account_id: str, list_id: str, data: IPItem):
    headers = get_headers()

    payload = [
        {
            "ip": str(data.ip),
            "comment": data.comment
        }
    ]

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.CLOUDFLARE_BASE_URL}/accounts/{account_id}/rules/lists/{list_id}/items",
            headers=headers,
            json=payload
        )

    if response.status_code not in (200, 201):
        raise HTTPException(
            status_code=response.status_code,
            detail=response.json()
        )

    return response.json().get("result")