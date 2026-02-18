from fastapi import FastAPI
from app.routes.cloudflare import router as cloudflare_router

app = FastAPI()

app.include_router(cloudflare_router)