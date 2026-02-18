import os
import httpx
from fastapi import FastAPI, HTTPException, Path
from typing import Literal, Optional, List
from pydantic import BaseModel, model_validator

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


class SkipParameters(BaseModel):
    phases: Optional[List[Literal[
        "http_request_firewall_custom",
        "http_request_firewall_managed"
    ]]] = None

    ruleset: Optional[Literal["current"]] = None


class CreateRuleRequest(BaseModel):
    expression: str
    description: str
    action: Literal["block", "skip"] = "block"
    action_parameters: Optional[SkipParameters] = None

    @model_validator(mode="after")
    def validate_skip(cls, values):
        if values.action == "skip":
            if not values.action_parameters:
                raise ValueError("action_parameters is required when action is 'skip'")

            if not (values.action_parameters.phases or values.action_parameters.ruleset):
                raise ValueError("Skip must define either 'phases' or 'ruleset'")

        else:
            if values.action_parameters is not None:
                raise ValueError("action_parameters must not be provided when action is 'block'")

        return values

@app.patch("/cloudflare/rulesets/{zone_id}/{ruleset_id}/rules")
async def patch_add_rule_to_ruleset(
    zone_id: str = Path(..., description="Zone ID da Cloudflare"),
    ruleset_id: str = Path(..., description="Ruleset ID da Cloudflare"),
    rule: CreateRuleRequest = ...
):
    if not CLOUDFLARE_API_TOKEN:
        raise HTTPException(
            status_code=500,
            detail="Cloudflare token not configured"
        )

    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }

    base_url = f"{CLOUDFLARE_BASE_URL}/zones/{zone_id}/rulesets/{ruleset_id}"

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

        # (Opcional) evitar duplicação
        if any(r["expression"] == rule.expression for r in existing_rules):
            raise HTTPException(
                status_code=400,
                detail="Rule with this expression already exists"
            )

        existing_rules.append(new_rule)

        # Atualizar ruleset inteiro (Cloudflare exige PUT)
        put_response = await client.put(
            base_url,
            headers=headers,
            json={
                "rules": existing_rules
            }
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


@app.delete("/cloudflare/rulesets/{zone_id}/{ruleset_id}/rules/{rule_id}")
async def delete_rule_from_ruleset(
    zone_id: str = Path(..., description="Zone ID da Cloudflare"),
    ruleset_id: str = Path(..., description="Ruleset ID da Cloudflare"),
    rule_id: str = Path(..., description="Rule ID da Cloudflare")
):
    if not CLOUDFLARE_API_TOKEN:
        raise HTTPException(
            status_code=500,
            detail="Cloudflare token not configured"
        )

    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }

    base_url = f"{CLOUDFLARE_BASE_URL}/zones/{zone_id}/rulesets/{ruleset_id}"

    async with httpx.AsyncClient() as client:

        get_response = await client.get(base_url, headers=headers)

        if get_response.status_code != 200:
            raise HTTPException(
                status_code=get_response.status_code,
                detail=get_response.text
            )

        ruleset_data = get_response.json()["result"]
        existing_rules = ruleset_data["rules"]
        # Testar amanhã 
        # print('existing_rules', existing_rules)

        updated_rules = [
            rule for rule in existing_rules
            if rule["id"] != rule_id
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











