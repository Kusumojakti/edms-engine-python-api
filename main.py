import io
import uuid
import PyPDF2
import httpx

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
from PyPDF2 import PdfMerger

app = FastAPI()


@app.post(
    "/api/v1/merge-pdfs",
    summary="Merge PDF files from URLs",
    description="Download multiple PDFs from URLs and merge them into one file"
)
async def merge_pdfs(request: Request):

    body = await request.json()
    urls = body.get("urls", [])

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
                reader = PyPDF2.PdfReader(pdf_bytes)
                merger.append(reader)

            except httpx.RequestError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Error downloading {url}: {str(e)}"
                )

            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error processing {url}: {str(e)}"
                )

    output = io.BytesIO()
    merger.write(output)
    merger.close()

    output.seek(0)

    filename = f"merged_{uuid.uuid4().hex}.pdf"

    return StreamingResponse(
        output,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )