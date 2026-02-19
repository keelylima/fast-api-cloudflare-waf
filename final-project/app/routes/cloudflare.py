from fastapi import APIRouter, Path, Query
from typing import Literal
from app.schemas.rules import (
    CreateRulesetRequest,
    CreateRuleRequest,
    RulePosition,
    ExportedRule
)
from app.services import cloudflare_service as service

router = APIRouter(
    prefix="/cloudflare",
    tags=["Cloudflare"]
)

@router.get("/zones")
async def list_zones():
    return await service.list_zones()


@router.get("/waf/{zone_id}")
async def list_waf_rules(
    zone_id: str = Path(..., description="Zone ID da Cloudflare")
):
    return await service.list_waf_rules(zone_id)


@router.get("/rulesets/{zone_id}")
async def list_rulesets(
    zone_id: str = Path(..., description="Zone ID da Cloudflare")
):
    return await service.list_rulesets(zone_id)


@router.get("/rulesets/{zone_id}/{ruleset_id}")
async def get_ruleset_details(
    zone_id: str = Path(..., description="Zone ID da Cloudflare"),
    ruleset_id: str = Path(..., description="Ruleset ID da Cloudflare")
):
    return await service.get_ruleset_details(zone_id, ruleset_id)


@router.post("/rulesets/{zone_id}")
async def create_ruleset(
    zone_id: str = Path(..., description="Zone ID da Cloudflare"),
    data: CreateRulesetRequest = ...
):
    return await service.create_ruleset(zone_id, data)


@router.delete("/rulesets/{zone_id}/{ruleset_id}")
async def delete_ruleset(
    zone_id: str = Path(..., description="Zone ID Cloudflare"),
    ruleset_id: str = Path(..., description="Ruleset ID Cloudflare")
):
    return await service.delete_ruleset(zone_id, ruleset_id)


@router.patch("/rulesets/{zone_id}/{ruleset_id}/rules")
async def add_rule_to_ruleset(
    zone_id: str = Path(..., description="Zone ID da Cloudflare"),
    ruleset_id: str = Path(..., description="Ruleset ID da Cloudflare"),
    data: CreateRuleRequest = ...
):
    return await service.add_rule_to_ruleset(zone_id, ruleset_id, data)


@router.delete("/rulesets/{zone_id}/{ruleset_id}/rules/{rule_id}")
async def delete_rule_from_ruleset(
    zone_id: str = Path(..., description="Zone ID da Cloudflare"),
    ruleset_id: str = Path(..., description="Ruleset ID da Cloudflare"),
    rule_id: str = Path(..., description="Rule ID da Cloudflare")
):
    return await service.delete_rule_from_ruleset(
        zone_id,
        ruleset_id,
        rule_id
    )

@router.patch(
    "/rulesets/{zone_id}/{ruleset_id}/rules/{rule_id}/reorder"
)
async def reorder_rule(
    zone_id: str,
    ruleset_id: str,
    rule_id: str,
    position: RulePosition
):
    return await service.reorder_rule(
        zone_id=zone_id,
        ruleset_id=ruleset_id,
        rule_id=rule_id,
        position=position
    )

@router.get(
    "/rules/export/{zone_id}",
    response_model=list[ExportedRule]
)
async def export_rules(
    zone_id: str,
    kind: Literal["zone", "managed", "all"] = Query("zone")
) -> list[ExportedRule]:

    return await service.export_rules_by_zone(
        zone_id=zone_id,
        kind=kind
    )