from app.services.semantic_matcher import calculate_semantic_score


def test_calculate_semantic_score():

    # --------------------------------
    # Resume
    # --------------------------------

    resume_text = """
    Ahmed is a Python Developer with 6 years of experience.

    He has 3 years of FastAPI experience and 2 years
    of RAG experience.

    He has built Generative AI applications using Python,
    FastAPI and retrieval augmented generation.
    """

    # --------------------------------
    # Job Description
    # --------------------------------

    job_description = """
    Looking for a Python Developer with experience
    building Generative AI and RAG applications.

    Strong FastAPI experience is required.
    """

    # --------------------------------
    # Calculate Semantic Score
    # --------------------------------

    result = calculate_semantic_score(
        resume_text,
        job_description
    )

    # --------------------------------
    # Verify Result Structure
    # --------------------------------

    assert result is not None

    assert "semantic_score" in result
    assert "matched_chunks" in result

    # --------------------------------
    # Verify Semantic Score
    # --------------------------------

    assert isinstance(
        result["semantic_score"],
        (int, float)
    )

    assert 0 <= result["semantic_score"] <= 100

    # --------------------------------
    # Verify Matched Chunks
    # --------------------------------

    assert isinstance(
        result["matched_chunks"],
        list
    )

    assert len(result["matched_chunks"]) > 0

    # --------------------------------
    # Verify Chunk Structure
    # --------------------------------

    for match in result["matched_chunks"]:

        assert "similarity" in match
        assert "chunk" in match

        assert isinstance(
            match["similarity"],
            (int, float)
        )

        assert isinstance(
            match["chunk"],
            str
        )

        assert match["chunk"] != ""