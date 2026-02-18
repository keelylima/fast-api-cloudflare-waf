from fastapi import FastAPI
from app.routers.cloudflare import router as cloudflare_router

app = FastAPI()

app.include_router(cloudflare_router)