from app.services.candidate_extractor import extract_candidate
from app.services.candidate_matcher import check_candidate


def test_java_job_description_against_python_candidate():

    # --------------------------------
    # Sample Resume
    # --------------------------------

    resume_text = """
    Python Developer with 6 years of Python experience.

    FastAPI 2 years.

    RAG 2 years.

    Docker 1 year.

    Built Generative AI applications using Python,
    FastAPI and Retrieval Augmented Generation.
    """

    # --------------------------------
    # Java Job Description
    # --------------------------------

    jd_text = """
    Java Developer

    Must Have:

    Java 5 years
    SAP 3 years

    Nice to Have:

    Docker
    """

    # --------------------------------
    # Extract Candidate
    # --------------------------------

    candidate = extract_candidate(
        resume_text
    )

    assert candidate is not None

    assert candidate["name"] == "Unknown"

    assert "Python" in candidate["skills"]

    assert "FastAPI" in candidate["skills"]

    assert "RAG" in candidate["skills"]

    assert "Docker" in candidate["skills"]

    # --------------------------------
    # Match Candidate Against JD
    # --------------------------------

    result = check_candidate(
        candidate,
        jd_text,
        resume_text
    )

    # --------------------------------
    # Validate Result Structure
    # --------------------------------

    assert result is not None

    assert "name" in result
    assert "qualified" in result
    assert "recommendation" in result
    assert "final_score" in result
    assert "rule_based_score" in result
    assert "semantic_score" in result
    assert "experience_closeness_score" in result
    assert "matched_skills" in result
    assert "reasons" in result

    # --------------------------------
    # Validate Score Ranges
    # --------------------------------

    assert 0 <= result["final_score"] <= 100

    assert 0 <= result["rule_based_score"] <= 100

    assert 0 <= result["semantic_score"] <= 100

    assert 0 <= result[
        "experience_closeness_score"
    ] <= 100

    # --------------------------------
    # Important Business Rule
    # --------------------------------
    # Candidate has Python/FastAPI/RAG/Docker
    # but does not have the required Java/SAP
    # experience.

    assert result["qualified"] is False

    # --------------------------------
    # Validate Result Types
    # --------------------------------

    assert isinstance(
        result["matched_skills"],
        list
    )

    assert isinstance(
        result["reasons"],
        list
    )

    assert len(result["reasons"]) > 0