import os

class Settings:
    CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
    CLOUDFLARE_BASE_URL = "https://api.cloudflare.com/client/v4"
    CLOUDFLARE_ACCOUNT_ID = "a7301d3490ae2a2ab73adcdb149a62f1"

settings = Settings()