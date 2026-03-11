import io
import os
import uuid
import httpx
import PyPDF2
from typing import List
from pydantic import BaseModel, HttpUrl
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from PyPDF2 import PdfMerger, PdfWriter, PdfReader

app = FastAPI()

ASSETS_DIR = "assets"
DUMMY_PIN = "1234" 
os.makedirs(ASSETS_DIR, exist_ok=True)

class PDFMergeRequest(BaseModel):
    urls: List[HttpUrl]

    class Config:
        json_schema_extra = {
            "example": {
                "urls": [
                    "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
                    "https://www.africau.edu/images/default/sample.pdf"
                ]
            }
        }

@app.get("/assets/{filename}")
async def get_asset(filename: str):
    """
    Serves the merged PDF files from the assets folder.
    The user will be prompted for the dummy PIN (1234) by their PDF viewer.
    """
    file_path = os.path.join(ASSETS_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        file_path, 
        media_type="application/pdf", 
        filename=filename
    )

@app.post(
    "/api/v1/merge-pdfs",
    summary="Merge PDFs with Dummy Encryption",
    description="Download multiple PDFs, merge them, and encrypt with a hardcoded dummy PIN.",
    responses={
        200: {
            "content": {"application/pdf": {}},
            "description": "Returns the merged PDF file (Password: 1234).",
        }
    }
)
async def merge_pdfs(payload: PDFMergeRequest): 
    urls = [str(url) for url in payload.urls]

    if not urls:
        raise HTTPException(status_code=400, detail="No URLs provided")

    merger = PdfMerger()

    async with httpx.AsyncClient(timeout=30) as client:
        for url in urls:
            try:
                response = await client.get(url)

                if response.status_code != 200:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Failed to download file from {url}"
                    )

                content_type = response.headers.get("content-type", "")
                if "application/pdf" not in content_type:
                    raise HTTPException(
                        status_code=400,
                        detail=f"{url} is not a PDF"
                    )

                pdf_bytes = io.BytesIO(response.content)
                merger.append(pdf_bytes)

            except httpx.RequestError as e:
                raise HTTPException(status_code=400, detail=f"Error downloading {url}: {str(e)}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error processing {url}: {str(e)}")

    intermediate_output = io.BytesIO()
    merger.write(intermediate_output)
    merger.close()
    intermediate_output.seek(0)

    writer = PdfWriter()
    reader = PdfReader(intermediate_output)
    
    for page in reader.pages:
        writer.add_page(page)

    writer.encrypt(DUMMY_PIN)

    filename = f"merge_{uuid.uuid4().hex}.pdf"
    file_path = os.path.join(ASSETS_DIR, filename)

    with open(file_path, "wb") as f:
        writer.write(f)

    final_output = io.BytesIO()
    writer.write(final_output)
    final_output.seek(0)

    return StreamingResponse(
        final_output,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "X-File-Path": f"/assets/{filename}"
        }
    )