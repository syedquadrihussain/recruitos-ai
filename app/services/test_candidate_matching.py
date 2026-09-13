from app.services.candidate_extractor import extract_candidate
from app.services.candidate_matcher import check_candidate


def test_candidate_matching():

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
    # Job Description
    # --------------------------------

    jd_text = """
    Python Developer

    Must Have:

    Python 5 years
    FastAPI 3 years
    RAG 2 years

    Nice to Have:

    Docker
    """

    # --------------------------------
    # Extract Candidate
    # --------------------------------

    candidate = extract_candidate(
        resume_text
    )

    # --------------------------------
    # Verify Candidate Extraction
    # --------------------------------

    assert candidate is not None

    assert candidate["overall_experience"] == 6

    assert "Python" in candidate["skills"]
    assert "FastAPI" in candidate["skills"]
    assert "RAG" in candidate["skills"]
    assert "Docker" in candidate["skills"]

    assert candidate["experience"]["Python"] == 6
    assert candidate["experience"]["FastAPI"] == 2
    assert candidate["experience"]["RAG"] == 2
    assert candidate["experience"]["Docker"] == 1

    # --------------------------------
    # Match Candidate
    # --------------------------------

    result = check_candidate(
        candidate,
        jd_text,
        resume_text
    )

    # --------------------------------
    # Verify Matching Result
    # --------------------------------

    assert result is not None

    assert "rule_based_score" in result
    assert "semantic_score" in result
    assert "final_score" in result
    assert "recommendation" in result
    assert "qualified" in result

    # --------------------------------
    # Verify Scores
    # --------------------------------

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

    assert 0 <= result["rule_based_score"] <= 100
    assert 0 <= result["semantic_score"] <= 100
    assert 0 <= result["final_score"] <= 100

    # --------------------------------
    # Verify Qualification
    # --------------------------------

    # FastAPI requires 3 years,
    # but the candidate has only 2 years.
    # Therefore the candidate should not qualify.

    assert result["qualified"] is False

    # --------------------------------
    # Verify Recommendation
    # --------------------------------

    assert result["recommendation"] != ""