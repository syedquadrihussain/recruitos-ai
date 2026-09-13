from app.services.candidate_extractor import extract_candidate


def test_extract_candidate():

    # --------------------------------
    # Sample Resume
    # --------------------------------

    resume_text = """
    Name: Ahmed

    Skills:

    Python

    FastAPI

    RAG

    Docker

    Python: 6 years

    FastAPI: 2 years

    RAG: 2 years

    Docker: 1 year
    """

    # --------------------------------
    # Extract Candidate
    # --------------------------------

    candidate = extract_candidate(
        resume_text
    )

    # --------------------------------
    # Verify Candidate
    # --------------------------------

    assert candidate is not None

    # --------------------------------
    # Verify Name
    # --------------------------------

    assert candidate["name"] == "Ahmed"

    # --------------------------------
    # Verify Skills
    # --------------------------------

    assert "Python" in candidate["skills"]
    assert "FastAPI" in candidate["skills"]
    assert "RAG" in candidate["skills"]
    assert "Docker" in candidate["skills"]

    # --------------------------------
    # Verify Experience
    # --------------------------------

    assert candidate["experience"]["Python"] == 6
    assert candidate["experience"]["FastAPI"] == 2
    assert candidate["experience"]["RAG"] == 2
    assert candidate["experience"]["Docker"] == 1