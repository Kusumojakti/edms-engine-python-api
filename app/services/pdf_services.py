from app.clients.edms_client import fetch_documents
from app.utils.pdf_utils import merge_pdfs, add_pin, save_pdf
from app.services.exceptions import (
    InvalidPINException,
    InvalidDocumentCombination
)


def validate_pin(pin: str):
    if not pin or len(pin) < 4:
        raise InvalidPINException("PIN must be at least 4 characters")


def process_merge(no_reg: str, pin: str):
    validate_pin(pin)

    documents = fetch_documents(no_reg)

    ps, ppjf, edelivery = [], [], []

    for doc in documents:
        category = doc.get("documentCategory")
        url = doc.get("physicalPath")

        if not url:
            continue

        if category == "PS":
            ps.append(url)
        elif category == "PPJF":
            ppjf.append(url)
        elif category == "Dokumen Kontrak E-Delivery":
            edelivery.append(url)

    if edelivery:
        merged = merge_pdfs(edelivery)

    elif ps and ppjf:
        merged = merge_pdfs(ps + ppjf)

    else:
        raise InvalidDocumentCombination(
            "Invalid combination: need PS+PPJF or E-Delivery"
        )

    secured = add_pin(merged, pin)
    secured.seek(0)
    return secured