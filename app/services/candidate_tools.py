from pathlib import Path

from app.services.resume_parser import extract_text_from_pdf
from app.services.candidate_extractor import extract_candidate
from app.services.candidate_matcher import check_candidate


UPLOAD_FOLDER = Path("uploads")


def load_candidates():
    candidates = []

    for pdf_file in UPLOAD_FOLDER.glob("*.pdf"):

        resume_text = extract_text_from_pdf(
            str(pdf_file)
        )

        candidate = extract_candidate(
            resume_text
        )

        if candidate["name"] == "Unknown":
            candidate["name"] = pdf_file.stem

        candidate["_resume_text"] = resume_text
        candidate["_filename"] = pdf_file.name

        candidates.append(candidate)

    return candidates


def search_candidates(skill):

    candidates = load_candidates()

    matching_candidates = []

    for candidate in candidates:

        candidate_skills = [
            candidate_skill.lower()
            for candidate_skill in candidate["skills"]
        ]

        if skill.lower() in candidate_skills:

            matching_candidates.append({
                "name": candidate["name"],
                "skills": candidate["skills"],
                "overall_experience": candidate[
                    "overall_experience"
                ],
                "roles": candidate["roles"],
                "companies": candidate["companies"],
                "filename": candidate["_filename"]
            })

    return matching_candidates


def score_candidate(name, job_description):

    candidates = load_candidates()

    for candidate in candidates:

        if candidate["name"].lower() == name.lower():

            result = check_candidate(
                candidate,
                job_description,
                candidate["_resume_text"]
            )

            return result

    return {
        "error": f"Candidate '{name}' was not found."
    }