import os
import httpx
from fastapi import FastAPI, HTTPException, Path

app = FastAPI()

CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
CLOUDFLARE_BASE_URL = "https://api.cloudflare.com/client/v4"


@app.get("/cloudflare/zones")
async def list_zones():

    if not CLOUDFLARE_API_TOKEN:
        raise HTTPException(status_code=500, detail="Cloudflare token not configured")

    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{CLOUDFLARE_BASE_URL}/zones",
            headers=headers
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )

    return response.json()

@app.get("/cloudflare/waf/{zone_id}")
async def list_waf_rules(zone_id: str = Path(..., description="Zone ID da Cloudflare")):

    if not CLOUDFLARE_API_TOKEN:
        raise HTTPException(status_code=500, detail="Cloudflare token not configured")

    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }

    url = f"{CLOUDFLARE_BASE_URL}/zones/{zone_id}/rulesets/phases/http_request_firewall_custom/entrypoint"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )

    return response.json()