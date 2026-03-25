from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.schemas.request_schema import MergeRequest
from app.services.pdf_services import process_merge
from app.services.exceptions import PDFMergeException

router = APIRouter()


@router.post("/api/v1/merge-pdf")
def merge_pdf(request: MergeRequest):
    try:
        filepath, pdf_stream = process_merge(
            request.no_aggr,
            request.pin
        )

        return StreamingResponse(
            pdf_stream,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=merged.pdf",
                "X-File-Path": filepath
            }
        )

    except PDFMergeException as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        print("ERROR:", str(e)) 
        raise HTTPException(status_code=500, detail=str(e))