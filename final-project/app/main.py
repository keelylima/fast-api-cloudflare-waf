from fastapi import FastAPI
from app.routes.cloudflare import router as cloudflare_router
from app.routes.cloudflare_ip_lists import router as cloudflare_ip_lists

app = FastAPI()

app.include_router(cloudflare_router)
app.include_router(cloudflare_ip_lists)