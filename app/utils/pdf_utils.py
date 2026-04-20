import os
import uuid
import requests
from io import BytesIO
from pypdf import PdfReader, PdfWriter
from app.config.settings import settings
from app.utils.security import generate_headers

def download_pdf(url: str) -> BytesIO:
    headers = generate_headers(method="GET", url=url)

    res = requests.get(
        url,
        headers=headers,
        timeout=15
    )

    print("URL:", url)
    print("Status:", res.status_code)
    print("Response:", res.text[:200])

    if res.status_code != 200:
        raise Exception(f"Failed download: {res.status_code}")

    return BytesIO(res.content)


def merge_pdfs(urls: list[str]) -> BytesIO:
    writer = PdfWriter()

    for url in urls:
        pdf_stream = download_pdf(url)
        reader = PdfReader(pdf_stream)

        for page in reader.pages:
            writer.add_page(page)

    output = BytesIO()
    writer.write(output)
    output.seek(0)

    return output


def add_pin(pdf_stream: BytesIO, pin: str) -> BytesIO:
    reader = PdfReader(pdf_stream)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    writer.encrypt(pin)

    output = BytesIO()
    writer.write(output)
    output.seek(0)

    return output


def save_pdf(pdf_stream: BytesIO) -> str:
    os.makedirs(settings.OUTPUT_DIR, exist_ok=True)

    filename = f"{uuid.uuid4()}.pdf"
    filepath = os.path.join(settings.OUTPUT_DIR, filename)

    with open(filepath, "wb") as f:
        f.write(pdf_stream.read())

    return filepath