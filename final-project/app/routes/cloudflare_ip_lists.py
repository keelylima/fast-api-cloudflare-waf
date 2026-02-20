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


@router.get("/", response_model=List[IPListResponse])
def get_ip_lists():
    return list_ip_lists()
