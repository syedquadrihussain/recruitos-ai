from app.services.jd_parser import parse_jd


def test_parse_jd():

    # --------------------------------
    # Job Description
    # --------------------------------

    jd_text = """
    We are looking for a Python Developer.

    Must Have:

    Python - 5 years

    FastAPI - 3 years

    Nice to Have:

    RAG

    Docker
    """

    # --------------------------------
    # Parse JD
    # --------------------------------

    result = parse_jd(jd_text)

    # --------------------------------
    # Verify Result Structure
    # --------------------------------

    assert result is not None

    assert "must_have" in result
    assert "nice_to_have" in result
    assert "skill_weights" in result

    # --------------------------------
    # Verify Must-Have Skills
    # --------------------------------

    assert "Python" in result["must_have"]
    assert "FastAPI" in result["must_have"]

    assert result["must_have"]["Python"] == 5
    assert result["must_have"]["FastAPI"] == 3

    # --------------------------------
    # Verify Nice-to-Have Skills
    # --------------------------------

    assert "RAG" in result["nice_to_have"]
    assert "Docker" in result["nice_to_have"]

    # --------------------------------
    # Verify Skill Weights
    # --------------------------------

    assert result["skill_weights"]["Python"] == 3
    assert result["skill_weights"]["FastAPI"] == 3

    assert result["skill_weights"]["RAG"] == 1
    assert result["skill_weights"]["Docker"] == 1