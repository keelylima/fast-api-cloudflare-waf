from fastapi import FastAPI
from app.routes.cloudflare import router as cloudflare_router
from app.routes.cloudflare_ip_lists import router as cloudflare_ip_lists

app = FastAPI(
    title="Cloud Security Control API",
    description="Internal Cloudflare governance API for WAF and IP list management.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


app.include_router(cloudflare_router)
app.include_router(cloudflare_ip_lists)