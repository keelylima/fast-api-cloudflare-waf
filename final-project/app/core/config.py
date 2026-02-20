import os

class Settings:
    CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
    CLOUDFLARE_BASE_URL = "https://api.cloudflare.com/client/v4"
settings = Settings()