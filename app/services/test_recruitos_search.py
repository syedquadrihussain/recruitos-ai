from unittest.mock import patch

from app.services.recruitos_search import (
    search_recruitos
)


def test_exact_skill_search():

    results = search_recruitos(
        query="Python candidates",
        strategy="EXACT_SKILL",
        required_skills=["Python"]
    )

    assert isinstance(
        results,
        list
    )

    assert len(results) > 0

    for candidate in results:

        assert "candidate_id" in candidate
        assert "name" in candidate
        assert "skills" in candidate

        assert "Python" in candidate["skills"]


def test_semantic_search():

    mock_candidates = [
        {
            "candidate_id": "candidate_001",
            "name": "Ahmed",
            "overall_experience": 6,
            "skills": [
                "Python",
                "FastAPI",
                "RAG",
                "Docker"
            ],
            "experience": {
                "Python": 6,
                "FastAPI": 3,
                "RAG": 2,
                "Docker": 1
            }
        }
    ]

    with patch(
        "app.services.recruitos_search._semantic_search",
        return_value=mock_candidates
    ):

        results = search_recruitos(
            query="Python RAG Developer",
            strategy="SEMANTIC_SEARCH",
            required_skills=[
                "Python",
                "RAG"
            ]
        )

    assert isinstance(
        results,
        list
    )

    assert len(results) == 1

    assert results[0]["name"] == "Ahmed"

    assert "score" in results[0]


def test_hybrid_search():

    mock_candidates = [
        {
            "candidate_id": "candidate_001",
            "name": "Ahmed",
            "overall_experience": 6,
            "skills": [
                "Python",
                "FastAPI",
                "RAG",
                "Docker"
            ],
            "experience": {
                "Python": 6,
                "FastAPI": 3,
                "RAG": 2,
                "Docker": 1
            }
        }
    ]

    with patch(
        "app.services.recruitos_search._semantic_search",
        return_value=mock_candidates
    ):

        results = search_recruitos(
            query="Python FastAPI RAG Developer",
            strategy="HYBRID_SEARCH",
            required_skills=[
                "Python",
                "FastAPI",
                "RAG"
            ]
        )

    assert len(results) == 1

    assert results[0]["name"] == "Ahmed"

    assert results[0]["score"] == 3


def test_empty_query_returns_empty_results():

    results = search_recruitos(
        query="",
        strategy="SEMANTIC_SEARCH"
    )

    assert results == []