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

@router.get(
    "/zones",
    summary="List Cloudflare Zones",
    description="Returns all zones accessible by the configured Cloudflare API token. Used to retrieve the Zone ID required for further ruleset operations."
    )
async def list_zones():
    return await service.list_zones()


@router.get(
    "/waf/{zone_id}",
    summary="List WAF Rules",
    description="Retrieves WAF rules for the specified zone. Useful for inspecting active managed and custom rules sets."
    )
async def list_waf_rules(
    zone_id: str = Path(..., description="Zone ID da Cloudflare")
):
    return await service.list_waf_rules(zone_id)


@router.get(
    "/rulesets/{zone_id}",
    summary="List Rulesets",
    description="Returns all rulesets configured for a given zone, including phase, source and ruleset identifiers."
    )
async def list_rulesets(
    zone_id: str = Path(..., description="Zone ID da Cloudflare")
):
    return await service.list_rulesets(zone_id)


@router.get(
    "/rulesets/{zone_id}/{ruleset_id}",
    summary="Get Ruleset Details",
    description="Retrieves full details of a specific ruleset, including all configured rules."
    )
async def get_ruleset_details(
    zone_id: str = Path(..., description="Zone ID da Cloudflare"),
    ruleset_id: str = Path(..., description="Ruleset ID da Cloudflare")
):
    return await service.get_ruleset_details(zone_id, ruleset_id)


@router.post(
    "/rulesets/{zone_id}",
    summary="Create Ruleset",
    description="Creates a new custom ruleset in the specified zone. The ruleset will be associated with a specific execution phase."
    )
async def create_ruleset(
    zone_id: str = Path(..., description="Zone ID da Cloudflare"),
    data: CreateRulesetRequest = ...
):
    return await service.create_ruleset(zone_id, data)


@router.delete(
    "/rulesets/{zone_id}/{ruleset_id}",
    summary="Delete Ruleset",
    description="Deletes the specified ruleset from the given zone. This operation permanently removes all associated rules."
    )
async def delete_ruleset(
    zone_id: str = Path(..., description="Zone ID Cloudflare"),
    ruleset_id: str = Path(..., description="Ruleset ID Cloudflare")
):
    return await service.delete_ruleset(zone_id, ruleset_id)


@router.patch(
    "/rulesets/{zone_id}/{ruleset_id}/rules",
    summary="Add Rule to Ruleset",
    description="Adds a new rule to the specified ruleset. The ruleset is fetched, updated and re-submitted to Cloudflare. Supports 'block' and 'skip' actions."
    )
async def add_rule_to_ruleset(
    zone_id: str = Path(..., description="Zone ID da Cloudflare"),
    ruleset_id: str = Path(..., description="Ruleset ID da Cloudflare"),
    data: CreateRuleRequest = ...
):
    return await service.add_rule_to_ruleset(zone_id, ruleset_id, data)


@router.delete(
    "/rulesets/{zone_id}/{ruleset_id}/rules/{rule_id}",
    summary="Delete Rule from Ruleset",
    description="Removes a specific rule from the given ruleset. The ruleset is retrieved, modified and updated in Cloudflare."
    )
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
    "/rulesets/{zone_id}/{ruleset_id}/rules/{rule_id}/reorder",
    summary="Reorder Rule",
    description="Changes the execution order of a rule inside the specified ruleset. Rule order affects evaluation behavior."
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
    response_model=list[ExportedRule],
    summary="Export Rules",
    description="Exports all rules for the specified zone in JSON format. Useful for backup, migration or auditing."
)
async def export_rules(
    zone_id: str,
    kind: Literal["zone", "managed", "all"] = Query("zone")
) -> list[ExportedRule]:

    return await service.export_rules_by_zone(
        zone_id=zone_id,
        kind=kind
    )