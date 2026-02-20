from fastapi import APIRouter
from typing import List
from app.services.cloudflare_ip_lists_service import list_ip_lists
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
