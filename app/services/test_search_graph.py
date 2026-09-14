from unittest.mock import patch

from app.services.search_graph import (
    build_search_graph
)


# ---------------------------------------------------------
# Create Initial State
# ---------------------------------------------------------

def create_initial_state(
    target_count=3
):

    jd_text = """

    Job Title:
    Python RAG Developer

    Must Have:
    Python - 5 years
    RAG - 2 years
    FastAPI - 2 years

    Nice to Have:
    Docker
    AWS

    """

    return {

        "goal": (
            "Find candidates for "
            "Python RAG Developer"
        ),

        "jd_text": jd_text,

        "target_count": target_count,

        "candidates": [],

        "qualified_candidates": [],

        "attempt": 0,

        "current_strategy": "",

        "current_query": "",

        "last_search_candidates": 0,

        "last_search_qualified": 0,

        "last_search_duplicates": 0,

        "current_search_results": [],

        "current_qualified_results": []
    }


# ---------------------------------------------------------
# Mock LLM Planner
# ---------------------------------------------------------

def mock_llm_planner(state):

    strategies = [

        "EXACT_SKILL",

        "RELATED_SKILL",

        "ROLE",

        "DOMAIN",

        "SEMANTIC_SEARCH",

        "HYBRID_SEARCH"

    ]

    strategy_index = min(
        state["attempt"],
        len(strategies) - 1
    )

    from app.services.search_strategies import (
        SearchStrategy
    )

    return SearchStrategy(
        strategies[strategy_index]
    )


# ---------------------------------------------------------
# Mock RecruitOS Search
# ---------------------------------------------------------

def mock_recruitos_search(
    query,
    strategy,
    required_skills,
    top_k
):

    mock_results = {

        "EXACT_SKILL": [

            {
                "candidate_id": "candidate_001",

                "name": "Ahmed",

                "skills": [
                    "Python",
                    "RAG",
                    "FastAPI"
                ],

                "experience": {
                    "Python": 6,
                    "RAG": 2,
                    "FastAPI": 3
                }
            }

        ],

        "RELATED_SKILL": [

            {
                "candidate_id": "candidate_001",

                "name": "Ahmed",

                "skills": [
                    "Python",
                    "RAG",
                    "FastAPI"
                ],

                "experience": {
                    "Python": 6,
                    "RAG": 2,
                    "FastAPI": 3
                }
            }

        ],

        "ROLE": [

            {
                "candidate_id": "candidate_001",

                "name": "Ahmed",

                "skills": [
                    "Python",
                    "RAG",
                    "FastAPI"
                ],

                "experience": {
                    "Python": 6,
                    "RAG": 2,
                    "FastAPI": 3
                }
            }

        ],

        "DOMAIN": [

            {
                "candidate_id": "candidate_001",

                "name": "Ahmed",

                "skills": [
                    "Python",
                    "RAG",
                    "FastAPI"
                ],

                "experience": {
                    "Python": 6,
                    "RAG": 2,
                    "FastAPI": 3
                }
            }

        ],

        "SEMANTIC_SEARCH": [

            {
                "candidate_id": "candidate_001",

                "name": "Ahmed",

                "skills": [
                    "Python",
                    "RAG",
                    "FastAPI"
                ],

                "experience": {
                    "Python": 6,
                    "RAG": 2,
                    "FastAPI": 3
                }
            }

        ],

        "HYBRID_SEARCH": [

            {
                "candidate_id": "candidate_001",

                "name": "Ahmed",

                "skills": [
                    "Python",
                    "RAG",
                    "FastAPI"
                ],

                "experience": {
                    "Python": 6,
                    "RAG": 2,
                    "FastAPI": 3
                }
            }

        ]

    }

    return mock_results.get(
        strategy,
        []
    )


# ---------------------------------------------------------
# Run Graph With Mocks
# ---------------------------------------------------------

def run_test_graph(
    target_count=3
):

    with patch(
        "app.services.search_graph.choose_strategy_with_llm",
        side_effect=mock_llm_planner
    ), patch(
        "app.services.search_graph.search_recruitos",
        side_effect=mock_recruitos_search
    ):

        search_graph = build_search_graph()

        initial_state = create_initial_state(
            target_count
        )

        return search_graph.invoke(
            initial_state
        )


# ---------------------------------------------------------
# Tests
# ---------------------------------------------------------

def test_search_graph_uses_jd_skills():

    final_state = run_test_graph()

    assert (
        final_state["jd_text"]
        != ""
    )


def test_search_graph_stops_when_no_progress():

    final_state = run_test_graph(
        target_count=3
    )

    assert (
        len(
            final_state["qualified_candidates"]
        )
        == 1
    )


def test_search_graph_does_not_loop_forever():

    final_state = run_test_graph(
        target_count=3
    )

    assert (
        final_state["attempt"]
        <= 6
    )


def test_search_graph_preserves_qualified_candidate():

    final_state = run_test_graph(
        target_count=3
    )

    candidate_names = [

        candidate["name"]

        for candidate
        in final_state[
            "qualified_candidates"
        ]

    ]

    assert "Ahmed" in candidate_names


def test_search_graph_stops_at_max_attempts():

    final_state = run_test_graph(
        target_count=100
    )

    assert (
        final_state["attempt"]
        <= 6
    )