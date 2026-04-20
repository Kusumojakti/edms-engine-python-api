from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.schemas.request_schema import MergeRequest
from app.services.pdf_services import process_merge
from app.services.exceptions import PDFMergeException

router = APIRouter()


def build_filename(no_reg: str) -> str:
    return f"merge_{no_reg}.pdf"


@router.post("/api/v1/merge-pdf")
def merge_pdf(request: MergeRequest):
    try:
        pdf_stream = process_merge(
            request.no_reg,
            request.pin
        )

        filename = build_filename(request.no_reg)

        return StreamingResponse(
            pdf_stream,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )

    except PDFMergeException as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        print("ERROR:", str(e)) 
        raise HTTPException(status_code=500, detail=str(e))
