import uuid

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from pathlib import Path

from app.services.candidate_extractor import extract_candidate
from app.services.candidate_matcher import check_candidate
from app.services.resume_parser import extract_text_from_pdf
from app.services.candidate_store import (
    add_candidate,
    generate_candidate_id
)
from app.services.resume_ingestion import process_resume
from app.services.vector_store import load_chunks

from app.routers import resumes
from app.routers import agent


app = FastAPI()

MAX_UPLOAD_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB


@app.get("/")
def home():
    return {"message": "RecruitOS AI is running"}


class User(BaseModel):
    name: str
    email: str


class ScreeningRequest(BaseModel):
    resume_text: str
    job_description: str


@app.post("/screen")
def screen_candidate(request: ScreeningRequest):

    candidate = extract_candidate(
        request.resume_text
    )

    result = check_candidate(
        candidate,
        request.job_description,
        request.resume_text
    )

    return result


@app.post("/screen-resume")
async def screen_resume(
    file: UploadFile = File(...),
    job_description: str = Form(...),
    resume_id: str | None = Form(default=None)
):

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )

    file_bytes = await file.read()

    if len(file_bytes) > MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail="File too large. Max size is 5 MB."
        )

    upload_folder = Path("uploads")
    upload_folder.mkdir(exist_ok=True)

    # Use a generated filename instead of the user-supplied one,
    # so a malicious filename (e.g. containing "../") can't write
    # outside the uploads folder.
    safe_filename = f"{uuid.uuid4().hex}.pdf"
    file_path = upload_folder / safe_filename

    with open(file_path, "wb") as buffer:
        buffer.write(file_bytes)

    resume_text = extract_text_from_pdf(
        str(file_path)
    )

    if not resume_text.strip():
        raise HTTPException(
            status_code=400,
            detail="Could not extract text from the resume"
        )

    candidate = extract_candidate(
        resume_text
    )

    result = check_candidate(
        candidate,
        job_description,
        resume_text
    )

    # Reuse the existing resume identity only when explicitly supplied.
    # New uploads receive a resume_id so they can be updated later.
    effective_resume_id = resume_id or uuid.uuid4().hex

    existing_records = [
        record for record in load_chunks()
        if record.get("resume_id") == effective_resume_id
    ]

    if existing_records:
        candidate_id = existing_records[0].get("candidate_id")
        if not candidate_id:
            raise HTTPException(
                status_code=409,
                detail="Existing resume has no candidate ID; update cannot proceed safely."
            )
    else:
        candidate_id = generate_candidate_id()

    # Store the resume before publishing its candidate profile.
    # If ingestion fails, avoid leaving a profile without resume data.
    process_resume(
        str(file_path),
        candidate_id,
        file.filename,
        resume_id=effective_resume_id
    )

    add_candidate(
        candidate_id,
        candidate
    )

    return {
        "candidate_id": candidate_id,
        "resume_id": effective_resume_id,
        "filename": file.filename,
        "candidate": candidate,
        "screening_result": result
    }


@app.post("/users")
def create_user(user: User):
    return {
        "message": "User created successfully",
        "user": user
    }


app.include_router(resumes.router)
app.include_router(agent.router)