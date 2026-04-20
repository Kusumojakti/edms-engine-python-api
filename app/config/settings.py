from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    BASE_URL = os.getenv("EDMS_BASE_URL")
    ENDPOINT = os.getenv("EDMS_ENDPOINT")
    API_KEY = os.getenv("API_KEY")
    CANONICAL_PATH = os.getenv("CANONICAL_PATH")

    APP_ID = os.getenv("APP_ID")
    CHANNEL_ID = os.getenv("CHANNEL_ID")

    SIGNATURE_MODE = os.getenv("SIGNATURE_MODE")
    STATIC_SIGNATURE = os.getenv("STATIC_SIGNATURE")
    SECRET_KEY = os.getenv("SECRET_KEY")
    PRIVATE_KEY_PATH = os.getenv("PRIVATE_KEY_PATH")
    SIGNATURE_TZ_OFFSET_HOURS = int(os.getenv("SIGNATURE_TZ_OFFSET_HOURS", "7"))

    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./assets")


settings = Settings()