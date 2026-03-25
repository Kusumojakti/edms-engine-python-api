import requests
from app.config.settings import settings
from app.utils.security import generate_headers
from app.services.exceptions import (
    NoAggrNotFoundException,
    PDFMergeException
)

class EDMSClientError(Exception):
    pass

def fetch_documents(no_aggr: str):
    url = f"{settings.BASE_URL}{settings.ENDPOINT}"
    headers = generate_headers(no_aggr)

    try:
        response = requests.get(
            url,
            params={"noAggr": no_aggr},
            headers=headers,
            timeout=15
        )

        if response.status_code != 200:
            raise PDFMergeException(
                "Failed to retrieve documents from EDMS"
            )

        data = response.json()

        if data.get("status") != "T":
            raise NoAggrNotFoundException(
                f"No data found for noAggr: {no_aggr}"
            )

        documents = data.get("data", {}).get("documents", [])

        if not documents:
            raise NoAggrNotFoundException(
                f"No document found for noAggr: {no_aggr}"
            )

        return documents

    except requests.Timeout:
        raise PDFMergeException("EDMS request timeout")

    except requests.RequestException:
        raise PDFMergeException("Failed to connect to EDMS")