import os
import httpx
from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel

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



@app.get("/cloudflare/rulesets/{zone_id}")
async def list_rulesets(zone_id: str = Path(..., description="Zone ID da Cloudflare")):
    if not CLOUDFLARE_API_TOKEN:
        raise HTTPException(status_code=500, detail="Cloudflare token is not configured")
    
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }

    url = f"{CLOUDFLARE_BASE_URL}/zones/{zone_id}/rulesets"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )
    return response.json()


@app.get("/cloudflare/rulesets/{zone_id}/{ruleset_id}")
async def get_ruleset_details(
    zone_id: str = Path(..., description="Zone ID da Cloudflare"),
    ruleset_id: str = Path(..., description="Ruleset ID da Cloudflare")
):
    if not CLOUDFLARE_API_TOKEN:
        raise HTTPException(status_code=500, detail="Cloudflare token is not configured")

    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }

    url = f"{CLOUDFLARE_BASE_URL}/zones/{zone_id}/rulesets/{ruleset_id}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.text
            )
        return response.json()


class CreateRulesetRequest(BaseModel):
    name: str
    description: str


@app.post("/cloudflare/rulesets/{zone_id}")
async def create_ruleset(
    zone_id: str = Path(..., description="Zone ID da Cloudflare"),
    data: CreateRulesetRequest = ...
):
    if not CLOUDFLARE_API_TOKEN:
        raise HTTPException(status_code=500, detail="Cloudflare token not configured")

    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }

    url = f"{CLOUDFLARE_BASE_URL}/zones/{zone_id}/rulesets"

    payload = {
        "name": data.name,
        "description": data.description,
        "kind": "zone",
        "phase": "http_request_firewall_custom",
        "rules": []
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)

    if response.status_code not in [200, 201]:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )

    return response.json()

@app.delete("/cloudflare/rulesets/{zone_id}/{ruleset_id}")
async def delete_ruleset(
    zone_id: str = Path(..., description="Zone ID Cloudflare"),
    ruleset_id: str = Path(..., description="Ruleset ID Cloudflare")
):
    if not CLOUDFLARE_API_TOKEN:
        raise HTTPException(status_code=500, detail="Cloudflae token configured")

    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }

    url = f"{CLOUDFLARE_BASE_URL}/zones/{zone_id}/rulesets/{ruleset_id}"

    async with httpx.AsyncClient() as client:
        response = await client.delete(url, headers=headers)

        if response.status_code not in [200, 204]:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.text
            )
        return {
            "message": "Ruleset deleted successfully",
            "ruleset_id": ruleset_id
        }









