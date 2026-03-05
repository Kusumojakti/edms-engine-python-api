import io
import os
import uuid
import PyPDF2
from dotenv import load_dotenv
from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from typing import List
from PyPDF2 import PdfMerger
import httpx

load_dotenv()

ASSETS_DIR = os.getenv("ASSETS_DIR")
os.makedirs(ASSETS_DIR, exist_ok=True)

app = FastAPI()

app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")

@app.post("/api/v1/merge-pdfs")
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
                    raise HTTPException(status_code=400, detail=f"Failed to download file from {url}")
                
                content_type = response.headers.get("content-type", "")
                if "application/pdf" not in content_type:
                    raise HTTPException(status_code=400, detail=f"URL {url} does not point to a PDF")
                
                pdf_bytes = io.BytesIO(response.content)
                pdf_reader = PyPDF2.PdfReader(pdf_bytes)
                merger.append(pdf_reader)

            except httpx.RequestError as e:
                raise HTTPException(status_code=400, detail=f"Error downloading {url}: {str(e)}")
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Error processing {url}: {str(e)}")

    filename = f"merged_{uuid.uuid4().hex}.pdf"
    output_path = os.path.join(ASSETS_DIR, filename)

    with open(output_path, "wb") as f:
        merger.write(f)
    merger.close()

    return JSONResponse(
        status_code=200,
        content={
            "message": "PDFs merged successfully",
            "filename": filename,
            "url": f"/assets/{filename}",
        }
    )

# @app.post("/api/v1/merge-pdfs")
# async def merge_pdfs(files: List[UploadFile] = File(...)):
#     if not files:
#         raise HTTPException(status_code=400, detail="No files uploaded")

#     merger = PdfMerger()

#     for file in files:
#         if file.content_type != "application/pdf":
#             raise HTTPException(status_code=400, detail=f"File {file.filename} is not a PDF")
        
#         try:
#             pdf_reader = PyPDF2.PdfReader(io.BytesIO(await file.read()))
#             merger.append(pdf_reader)
#         except Exception as e:
#             raise HTTPException(status_code=400, detail=f"Error processing file {file.filename}: {str(e)}")

#     filename = f"merged_{uuid.uuid4().hex}.pdf"
#     output_path = os.path.join(ASSETS_DIR, filename)

#     with open(output_path, "wb") as f:
#         merger.write(f)
#     merger.close()

#     file_url = f"/assets/{filename}"

#     return JSONResponse(
#         status_code=200,
#         content={
#             "message": "PDFs merged successfully",
#             "filename": filename,
#             "url": file_url,           
#         }
#     )