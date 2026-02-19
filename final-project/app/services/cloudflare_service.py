import httpx
from fastapi import HTTPException
from app.core.config import settings
from app.schemas.rules import CreateRulesetRequest, CreateRuleRequest


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


async def list_zones():
    headers = get_headers()

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.CLOUDFLARE_BASE_URL}/zones",
            headers=headers
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )

    return response.json()


async def list_waf_rules(zone_id: str):
    headers = get_headers()

    url = f"{settings.CLOUDFLARE_BASE_URL}/zones/{zone_id}/rulesets/phases/http_request_firewall_custom/entrypoint"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )

    return response.json()


async def list_rulesets(zone_id: str):
    headers = get_headers()

    url = f"{settings.CLOUDFLARE_BASE_URL}/zones/{zone_id}/rulesets"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )

    return response.json()


async def get_ruleset_details(zone_id: str, ruleset_id: str):
    headers = get_headers()

    url = f"{settings.CLOUDFLARE_BASE_URL}/zones/{zone_id}/rulesets/{ruleset_id}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )

    return response.json()


async def create_ruleset(zone_id: str, data: CreateRulesetRequest):
    headers = get_headers()

    url = f"{settings.CLOUDFLARE_BASE_URL}/zones/{zone_id}/rulesets"

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


async def delete_ruleset(zone_id: str, ruleset_id: str):
    headers = get_headers()

    url = f"{settings.CLOUDFLARE_BASE_URL}/zones/{zone_id}/rulesets/{ruleset_id}"

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


async def add_rule_to_ruleset(zone_id: str, ruleset_id: str, rule: CreateRuleRequest):
    headers = get_headers()

    base_url = f"{settings.CLOUDFLARE_BASE_URL}/zones/{zone_id}/rulesets/{ruleset_id}"

    async with httpx.AsyncClient() as client:

        # Buscar ruleset atual
        get_response = await client.get(base_url, headers=headers)

        if get_response.status_code != 200:
            raise HTTPException(
                status_code=get_response.status_code,
                detail=get_response.text
            )

        ruleset_data = get_response.json()["result"]
        existing_rules = ruleset_data.get("rules", [])

        # Criar nova regra
        new_rule = {
            "expression": rule.expression,
            "description": rule.description,
            "action": rule.action,
            "enabled": True
        }

        if rule.action == "skip":
            new_rule["action_parameters"] = rule.action_parameters.model_dump()

        # Evitar duplicação
        if any(r["expression"] == rule.expression for r in existing_rules):
            raise HTTPException(
                status_code=400,
                detail="Rule with this expression already exists"
            )

        existing_rules.append(new_rule)

        # Cloudflare exige PUT do ruleset inteiro
        put_response = await client.put(
            base_url,
            headers=headers,
            json={"rules": existing_rules}
        )

    if put_response.status_code != 200:
        raise HTTPException(
            status_code=put_response.status_code,
            detail=put_response.text
        )

    return {
        "message": "Rule added successfully",
        "ruleset_id": ruleset_id
    }


async def delete_rule_from_ruleset(zone_id: str, ruleset_id: str, rule_id: str):
    headers = get_headers()

    base_url = f"{settings.CLOUDFLARE_BASE_URL}/zones/{zone_id}/rulesets/{ruleset_id}"

    async with httpx.AsyncClient() as client:

        get_response = await client.get(base_url, headers=headers)

        if get_response.status_code != 200:
            raise HTTPException(
                status_code=get_response.status_code,
                detail=get_response.text
            )

        ruleset_data = get_response.json()["result"]
        existing_rules = ruleset_data["rules"]

        updated_rules = [
            r for r in existing_rules
            if r["id"] != rule_id
        ]

        if len(updated_rules) == len(existing_rules):
            raise HTTPException(
                status_code=404,
                detail="Rule not found in this ruleset"
            )

        put_response = await client.put(
            base_url,
            headers=headers,
            json={"rules": updated_rules}
        )

    if put_response.status_code != 200:
        raise HTTPException(
            status_code=put_response.status_code,
            detail=put_response.text
        )

    return {
        "message": "Rule removed successfully",
        "ruleset_id": ruleset_id,
        "rule_id": rule_id
    }


async def reorder_rule(zone_id: str, ruleset_id: str, rule_id: str, position: RulePosition):
    headers = get_headers()

    base_url = f"{settings.CLOUDFLARE_BASE_URL}/zones/{zone_id}/rulesets/{ruleset_id}/rules/{rule_id}"

    payload = {
        "position": position.model_dump(exclude_none=True)
    }

    async with httpx.AsyncClient() as client:
        response = await client.patch(url, headers=headers, json=payload)

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )

    return {
        "message": "Rule reordered successfully",
        "rule_id": rule_id
    }
