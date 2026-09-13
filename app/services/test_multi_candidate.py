from app.services.candidate_store import get_candidate
from app.services.candidate_matcher import check_candidate
from app.services.candidate_ranker import rank_candidates
from app.services.reranker import rerank_candidates
from app.services.vector_store import search_embeddings, load_chunks
from app.services.embedding_service import create_embeddings


def test_multi_candidate_pipeline():

    # --------------------------------
    # Job Description
    # --------------------------------

    job_description = """
    Python Developer

    Must Have:

    Python 5 years
    FastAPI 3 years

    Nice to Have:

    RAG
    Docker
    """

    # --------------------------------
    # Search Query
    # --------------------------------

    query = "Python FastAPI RAG Developer"

    assert query.strip() != ""

    # --------------------------------
    # Create Query Embedding
    # --------------------------------

    query_embedding = create_embeddings(
        [query]
    )[0]

    assert query_embedding is not None

    assert len(query_embedding) > 0

    # --------------------------------
    # Load Chunks
    # --------------------------------

    chunks = load_chunks()

    assert chunks is not None

    assert isinstance(
        chunks,
        list
    )

    assert len(chunks) > 0

    # --------------------------------
    # Search FAISS
    # --------------------------------

    results = search_embeddings(
        query_embedding,
        chunks,
        top_k=5
    )

    assert results is not None

    assert isinstance(
        results,
        list
    )

    assert len(results) > 0

    assert len(results) <= 5

    # --------------------------------
    # Validate Retrieved Results
    # --------------------------------

    for result in results:

        assert "candidate_id" in result
        assert "resume_name" in result
        assert "distance" in result
        assert "chunk" in result

        assert isinstance(
            result["candidate_id"],
            str
        )

        assert isinstance(
            result["resume_name"],
            str
        )

        assert isinstance(
            result["chunk"],
            str
        )

    # --------------------------------
    # Get Unique Candidates
    # --------------------------------

    candidate_ids = []

    for result in results:

        candidate_id = result["candidate_id"]

        if candidate_id not in candidate_ids:

            candidate_ids.append(
                candidate_id
            )

    assert len(candidate_ids) > 0

    # --------------------------------
    # Get Candidate Profiles
    # --------------------------------

    candidates = []

    for candidate_id in candidate_ids:

        candidate = get_candidate(
            candidate_id
        )

        if candidate:

            candidate_copy = candidate.copy()

            candidate_copy["candidate_id"] = (
                candidate_id
            )

            candidates.append(
                candidate_copy
            )

    assert len(candidates) > 0

    # --------------------------------
    # Rerank Candidates
    # --------------------------------

    required_skills = [
        "Python",
        "FastAPI",
        "RAG",
        "Docker"
    ]

    reranked_candidates = rerank_candidates(
        candidates,
        required_skills
    )

    assert reranked_candidates is not None

    assert isinstance(
        reranked_candidates,
        list
    )

    assert len(reranked_candidates) > 0

    for candidate in reranked_candidates:

        assert "candidate_id" in candidate
        assert "name" in candidate
        assert "score" in candidate

        assert isinstance(
            candidate["score"],
            (int, float)
        )

    # --------------------------------
    # Verify Reranking Order
    # --------------------------------

    reranked_candidates.sort(
        key=lambda candidate: candidate["score"],
        reverse=True
    )

    rerank_scores = [
        candidate["score"]
        for candidate in reranked_candidates
    ]

    assert rerank_scores == sorted(
        rerank_scores,
        reverse=True
    )

    # --------------------------------
    # Screen Candidates
    # --------------------------------

    screening_results = []

    for candidate in reranked_candidates:

        result = check_candidate(
            candidate,
            job_description
        )

        result["candidate_id"] = (
            candidate["candidate_id"]
        )

        screening_results.append(
            result
        )

    assert len(screening_results) == len(
        reranked_candidates
    )

    # --------------------------------
    # Validate Screening Results
    # --------------------------------

    for result in screening_results:

        assert "candidate_id" in result
        assert "name" in result
        assert "qualified" in result
        assert "recommendation" in result
        assert "final_score" in result
        assert "must_have_results" in result
        assert "matched_skills" in result
        assert "reasons" in result

        assert isinstance(
            result["qualified"],
            bool
        )

        assert isinstance(
            result["recommendation"],
            str
        )

        assert isinstance(
            result["final_score"],
            (int, float)
        )

        assert 0 <= result["final_score"] <= 100

        assert isinstance(
            result["must_have_results"],
            list
        )

        assert isinstance(
            result["matched_skills"],
            list
        )

        assert isinstance(
            result["reasons"],
            list
        )

    # --------------------------------
    # Final Candidate Ranking
    # --------------------------------

    final_ranking = rank_candidates(
        screening_results
    )

    assert final_ranking is not None

    assert isinstance(
        final_ranking,
        list
    )

    assert len(final_ranking) == len(
        screening_results
    )

    # --------------------------------
    # Validate Final Ranking
    # --------------------------------

    final_scores = []

    for position, candidate in enumerate(
        final_ranking,
        start=1
    ):

        assert "candidate_id" in candidate
        assert "name" in candidate
        assert "qualified" in candidate
        assert "recommendation" in candidate
        assert "final_score" in candidate

        assert isinstance(
            candidate["qualified"],
            bool
        )

        assert isinstance(
            candidate["recommendation"],
            str
        )

        assert isinstance(
            candidate["final_score"],
            (int, float)
        )

        assert 0 <= candidate["final_score"] <= 100

        final_scores.append(
            candidate["final_score"]
        )

    # --------------------------------
    # Verify Final Ranking Order
    # --------------------------------

    assert final_scores == sorted(
        final_scores,
        reverse=True
    )