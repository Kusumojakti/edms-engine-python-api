import hashlib
from datetime import datetime
from app.config.settings import settings

def generate_headers(no_aggr: str = ""):
    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S %z")

    if settings.SIGNATURE_MODE == "static":
        signature = settings.STATIC_SIGNATURE
    else:
        raw = f"{no_aggr}{timestamp}{settings.SECRET_KEY}"
        signature = hashlib.sha256(raw.encode()).hexdigest()

    return {
        "X-Timestamp": timestamp,
        "X-Signature": signature,
        "X-App-Id": settings.APP_ID,
        "Channel-Id": settings.CHANNEL_ID,
        "APIKey": settings.API_KEY  
    }