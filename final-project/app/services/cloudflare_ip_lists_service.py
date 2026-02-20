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
            "ip": str(item.ip),
            "comment": item.comment
        }
        for item in data
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

async def find_ip_list_usage(account_id: str, list_id: str):
    headers = get_headers()

    async with httpx.AsyncClient() as client:

        # Buscar lista
        list_url = f"{settings.CLOUDFLARE_BASE_URL}/accounts/{account_id}/rules/lists/{list_id}"
        list_response = await client.get(list_url, headers=headers)

        if list_response.status_code != 200:
            raise HTTPException(
                status_code=list_response.status_code,
                detail=list_response.text
            )

        list_data = list_response.json()["result"]
        list_name = list_data["name"]

        # Otimização inteligente
        if list_data.get("num_referencing_filters", 0) == 0:
            return {
                "list_id": list_id,
                "list_name": list_name,
                "references_found": 0,
                "usages": []
            }

        # Buscar zones
        zones_url = f"{settings.CLOUDFLARE_BASE_URL}/zones"
        zones_response = await client.get(zones_url, headers=headers)

        if zones_response.status_code != 200:
            raise HTTPException(
                status_code=zones_response.status_code,
                detail=zones_response.text
            )

        zones = zones_response.json()["result"]
        usage_results = []

        # Iterar zones e olhar apenas a phase específica
        for zone in zones:
            zone_id = zone["id"]
            zone_name = zone["name"]

            ruleset_url = (
                f"{settings.CLOUDFLARE_BASE_URL}"
                f"/zones/{zone_id}/rulesets/phases/http_request_firewall_custom/entrypoint"
            )

            ruleset_response = await client.get(ruleset_url, headers=headers)

            if ruleset_response.status_code != 200:
                continue

            ruleset = ruleset_response.json()["result"]

            for rule in ruleset.get("rules", []):
                expression = rule.get("expression", "")

                if f"${list_name}" in expression:
                    usage_results.append({
                        "zone_id": zone_id,
                        "zone_name": zone_name,
                        "rule_id": rule.get("id"),
                        "description": rule.get("description"),
                        "action": rule.get("action"),
                        "enabled": rule.get("enabled"),
                        "expression": expression
                    })

        return {
            "list_id": list_id,
            "list_name": list_name,
            "references_found": len(usage_results),
            "usages": usage_results
        }
