from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
from app.services.resume_parser import extract_text_from_pdf


router = APIRouter(
    prefix="/resumes",
    tags=["Resumes"]
)


UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)


@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)):

    allowed_types = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ]

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are allowed"
        )

    file_path = UPLOAD_FOLDER / file.filename

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    extracted_text = ""

    if file.content_type == "application/pdf":
        extracted_text = extract_text_from_pdf(str(file_path))

    return {
        "message": "Resume uploaded successfully",
        "filename": file.filename,
        "content_type": file.content_type,
        "saved_path": str(file_path),
        "extracted_text": extracted_text
    }