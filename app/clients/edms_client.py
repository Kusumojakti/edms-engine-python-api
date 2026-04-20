import requests
from app.config.settings import settings
from app.utils.security import generate_headers
from app.services.exceptions import (
    NoAggrNotFoundException,
    PDFMergeException
)

class EDMSClientError(Exception):
    pass

def fetch_documents(no_reg: str):
    url = f"{settings.BASE_URL}{settings.ENDPOINT}"
    headers = generate_headers(
        method="GET",
        url=url,
        params={"noAggr": no_reg},
    )

    try:
        print("URL:", url)
        print("Params:", {"noAggr": no_reg})
        print("Headers:", headers)
        
        response = requests.get(
            url,
            params={"noAggr": no_reg},
            headers=headers,
            timeout=15
        )
        
        print("Response headers:", response.headers)
        print("Response status:", response.status_code)
        print("Response body:", response.text[:200]) 

        if response.status_code != 200:
            raise PDFMergeException(
                "Failed to retrieve documents from EDMS"
            )

        data = response.json()

        if data.get("status") != "T":
            raise NoAggrNotFoundException(
                f"No data found for noReg: {no_reg}"
            )

        documents = data.get("data", {}).get("documents", [])

        if not documents:
            raise NoAggrNotFoundException(
                f"No document found for noReg: {no_reg}"
            )

        return documents

    except requests.Timeout:
        raise PDFMergeException("EDMS request timeout")

    except requests.RequestException:
        raise PDFMergeException("Failed to connect to EDMS")