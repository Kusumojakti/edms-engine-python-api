from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    BASE_URL = os.getenv("EDMS_BASE_URL")
    ENDPOINT = os.getenv("EDMS_ENDPOINT")
    API_KEY = os.getenv("API_KEY")

    APP_ID = os.getenv("APP_ID")
    CHANNEL_ID = os.getenv("CHANNEL_ID")

    SIGNATURE_MODE = os.getenv("SIGNATURE_MODE")
    STATIC_SIGNATURE = os.getenv("STATIC_SIGNATURE")
    SECRET_KEY = os.getenv("SECRET_KEY")

    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./assets")

settings = Settings()