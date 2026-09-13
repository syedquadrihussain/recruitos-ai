from app.services.candidate_store import get_candidate
from app.services.candidate_matcher import check_candidate
from app.services.candidate_ranker import rank_candidates


def test_fallback_screening_and_ranking():

    # --------------------------------
    # Job Description
    # --------------------------------

    job_description = """
    Python Developer

    Must Have:

    Python 10 years
    FastAPI 8 years

    Nice to Have:

    RAG
    Docker
    """

    # --------------------------------
    # Candidate IDs
    # --------------------------------

    candidate_ids = [
        "candidate_001",
        "candidate_002",
        "candidate_003"
    ]

    # --------------------------------
    # Screen Candidates
    # --------------------------------

    screening_results = []

    for candidate_id in candidate_ids:

        candidate = get_candidate(
            candidate_id
        )

        if candidate:

            result = check_candidate(
                candidate,
                job_description
            )

            result["candidate_id"] = candidate_id

            screening_results.append(
                result
            )

    # --------------------------------
    # Validate Screening
    # --------------------------------

    assert isinstance(
        screening_results,
        list
    )

    assert len(screening_results) > 0

    for result in screening_results:

        assert "candidate_id" in result
        assert "name" in result
        assert "qualified" in result
        assert "final_score" in result
        assert "experience_closeness_score" in result
        assert "matched_skills" in result
        assert "reasons" in result

        assert isinstance(
            result["qualified"],
            bool
        )

        assert isinstance(
            result["final_score"],
            (int, float)
        )

        assert 0 <= result["final_score"] <= 100

        assert isinstance(
            result["experience_closeness_score"],
            (int, float)
        )

        assert 0 <= result[
            "experience_closeness_score"
        ] <= 100

        assert isinstance(
            result["matched_skills"],
            list
        )

        assert isinstance(
            result["reasons"],
            list
        )

    # --------------------------------
    # Rank Candidates
    # --------------------------------

    final_results = rank_candidates(
        screening_results
    )

    # --------------------------------
    # Validate Ranking
    # --------------------------------

    assert final_results is not None

    assert isinstance(
        final_results,
        list
    )

    assert len(final_results) == len(
        screening_results
    )

    for candidate in final_results:

        assert "candidate_id" in candidate
        assert "name" in candidate
        assert "qualified" in candidate
        assert "final_score" in candidate
        assert "experience_closeness_score" in candidate
        assert "matched_skills" in candidate
        assert "reasons" in candidate

    # --------------------------------
    # Verify Ranking Order
    # --------------------------------

    scores = [
        candidate["final_score"]
        for candidate in final_results
    ]

    assert scores == sorted(
        scores,
        reverse=True
    )