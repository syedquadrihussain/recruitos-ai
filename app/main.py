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
    job_description: str = Form(...)
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

    # Persist this candidate so the search/retrieval system
    # (recruitos_search.py) can actually find them later, instead
    # of only ever searching the fixed sample candidates.
    candidate_id = generate_candidate_id()

    add_candidate(
        candidate_id,
        candidate
    )

    # Chunk + embed the resume text and store it in the vector
    # index, so semantic/hybrid search strategies can find this
    # candidate too, not just exact skill matches.
    process_resume(
        str(file_path),
        candidate_id,
        file.filename
    )

    return {
        "candidate_id": candidate_id,
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