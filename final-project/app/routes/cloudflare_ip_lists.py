from fastapi import APIRouter
from typing import List
from app.services.cloudflare_ip_lists_service import list_ip_lists, list_ip_list_items
from app.schemas.rules import (
    IPListResponse,
)

router = APIRouter(
    prefix="/cloudflare/ip-lists",
    tags=["Cloudflare - IP Lists"]
)


@router.get("/{account_id}/ip-lists")
async def get_ip_lists(account_id: str):
    return await list_ip_lists(account_id)

@router.get("/{account_id}/ip-lists/{list_id}/items")
async def get_ip_list_items(account_id: str, list_id: str):
    return await list_ip_list_items(account_id, list_id)