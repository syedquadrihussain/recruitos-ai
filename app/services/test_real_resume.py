from pathlib import Path

from app.services.resume_parser import extract_text_from_pdf
from app.services.candidate_extractor import extract_candidate
from app.services.candidate_matcher import check_candidate


def test_real_resume_screening():

    resume_path = "uploads/Syed Hussain BDM.pdf"

    jd_text = """
    Python Developer

    Must Have:

    Python - 5 years
    FastAPI - 3 years
    RAG - 2 years

    Nice to Have:

    Docker
    AWS
    """

    # --------------------------------
    # Step 1: Verify Resume Exists
    # --------------------------------

    assert Path(resume_path).exists()

    # --------------------------------
    # Step 2: Extract Text From PDF
    # --------------------------------

    resume_text = extract_text_from_pdf(
        resume_path
    )

    assert resume_text is not None
    assert isinstance(resume_text, str)
    assert resume_text.strip() != ""

    # --------------------------------
    # Step 3: Extract Candidate
    # --------------------------------

    candidate = extract_candidate(
        resume_text
    )

    assert candidate is not None
    assert isinstance(candidate, dict)

    assert "name" in candidate
    assert "overall_experience" in candidate
    assert "skills" in candidate
    assert "roles" in candidate
    assert "companies" in candidate
    assert "experience" in candidate

    assert isinstance(candidate["name"], str)
    assert candidate["name"].strip() != ""
    assert isinstance(candidate["skills"], list)
    assert len(candidate["skills"]) > 0
    assert isinstance(candidate["experience"], dict)

    # --------------------------------
    # Step 4: Match Candidate Against JD
    # --------------------------------

    result = check_candidate(
        candidate,
        jd_text,
        resume_text
    )

    assert result is not None
    assert isinstance(result, dict)

    # --------------------------------
    # Step 5: Validate Screening Result
    # --------------------------------

    required_fields = [
        "name",
        "qualified",
        "recommendation",
        "rule_based_score",
        "semantic_score",
        "final_score",
        "experience_closeness_score",
        "matched_skills",
        "reasons"
    ]

    for field in required_fields:
        assert field in result

    assert isinstance(result["name"], str)
    assert isinstance(result["qualified"], bool)

    assert isinstance(
        result["recommendation"],
        str
    )

    assert isinstance(
        result["rule_based_score"],
        (int, float)
    )

    assert isinstance(
        result["semantic_score"],
        (int, float)
    )

    assert isinstance(
        result["final_score"],
        (int, float)
    )

    assert isinstance(
        result["experience_closeness_score"],
        (int, float)
    )

    assert 0 <= result["rule_based_score"] <= 100
    assert 0 <= result["semantic_score"] <= 100
    assert 0 <= result["final_score"] <= 100
    assert 0 <= result["experience_closeness_score"] <= 100

    assert isinstance(
        result["matched_skills"],
        list
    )

    assert isinstance(
        result["reasons"],
        list
    )

    assert len(result["reasons"]) > 0