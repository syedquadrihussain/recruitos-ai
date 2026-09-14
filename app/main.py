import uuid

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from pathlib import Path

from app.services.candidate_extractor import extract_candidate
from app.services.candidate_matcher import check_candidate
from app.services.resume_parser import extract_text_from_pdf

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

    return {
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