from fastapi import APIRouter
from typing import List
from app.services.cloudflare_ip_lists_service import list_ip_lists, list_ip_list_items, create_ip_list, delete_ip_list, add_ip_to_list, find_ip_list_usage, delete_ip_from_list
from app.schemas.rules import (
    IPListResponse,
    CreateIPListRequest,
    IPItem,
    IPListUsageResponse
)

router = APIRouter(
    prefix="/cloudflare/ip-lists",
    tags=["Cloudflare - IP Lists"]
)


@router.get(
    "/{account_id}/ip-lists",
    summary="List IP Lists",
    description="Returns all IP lists available in the specified Cloudflare account."
    )
async def get_ip_lists(account_id: str):
    return await list_ip_lists(account_id)

@router.get(
    "/{account_id}/ip-lists/{list_id}/items",
    summary="List IP List Items",
    description="Returns all IP items inside the specified IP list."
    )
async def get_ip_list_items(account_id: str, list_id: str):
    return await list_ip_list_items(account_id, list_id)

@router.post(
    "/{account_id}/ip-lists",
    summary="Create IP List",
    description="Creates a new Cloudflare IP list in the specified account."
    )
async def create_ip_list_route(
    account_id: str,
    body: CreateIPListRequest
):
    return await create_ip_list(account_id, body)

@router.delete(
    "/{account_id}/ip-lists/{list_id}",
    summary="Delete IP List",
    description="Deletes the specified IP list from the Cloudflare account."
    )
async def delete_ip_list_route(account_id: str, list_id: str):
    return await delete_ip_list(account_id, list_id)

@router.post(
    "/{account_id}/ip-lists/{list_id}/items",
    summary="Add IP to List",
    description="Adds one or more IP addresses to the specified Cloudflare IP list."
    )
async def add_ip_route(
    account_id: str,
    list_id: str,
    body: List[IPItem]
):
    return await add_ip_to_list(account_id, list_id, body)


@router.get(
    "/{account_id}/ip-lists/{list_id}/usage",
    response_model=IPListUsageResponse,
    summary="Get IP List Usage",
    description="Returns all WAF rules where the specified IP list is referenced."
)
async def get_ip_list_usage(account_id: str, list_id: str):
    # Returns all zone-level WAF rules where the IP list is referenced.
    return await find_ip_list_usage(account_id, list_id)

@router.delete(
    "/{account_id}/ip-lists/{list_id}/items/{item_id}",
    summary="Delete IP from List",
    description="Deletes a specific IP item from the list using its unique item_id. The item_id can be obtained from the List IP List Items endpoint."
)
async def delete_ip_item(
    account_id: str,
    list_id: str,
    item_id: str
):
    return await delete_ip_from_list(account_id, list_id, item_id)

