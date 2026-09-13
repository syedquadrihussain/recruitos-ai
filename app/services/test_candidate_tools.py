from app.services.candidate_tools import score_candidate


def test_score_candidate():
    job_description = """
    Must Have:
    Business Development Manager - 4 years
    IT Recruitment
    Client Relationship Management
    Lead Generation
    Contract Negotiation

    Nice to Have:
    ATS
    VMS
    SAP
    """

    result = score_candidate(
        "Syed Hussain BDM",
        job_description
    )

    # Make sure a result was returned
    assert result is not None

    # Make sure the correct candidate was evaluated
    assert result["name"] == "Syed Hussain BDM"

    # Candidate should qualify for this JD
    assert result["qualified"] is True

    # The scoring engine should return a score
    assert isinstance(
        result["final_score"],
        (int, float)
    )

    # Score should be within the expected range
    assert 0 <= result["final_score"] <= 100

    # Recommendation should be present
    assert result["recommendation"] != ""