from unittest.mock import patch

from app.services.search_graph import (
    build_search_graph
)

from app.services.search_strategies import (
    SearchStrategy
)


# =========================================================
# Mock LLM Planner
# =========================================================

def mock_llm_planner(
    state
):

    attempted_strategies = state.get(
        "attempted_strategies",
        []
    )

    # -----------------------------------------------------
    # First search
    # -----------------------------------------------------

    if not attempted_strategies:

        return SearchStrategy.EXACT_SKILL

    # -----------------------------------------------------
    # Second search
    # -----------------------------------------------------

    if (
        SearchStrategy.RELATED_SKILL.value
        not in attempted_strategies
    ):

        return SearchStrategy.RELATED_SKILL

    # -----------------------------------------------------
    # Third search
    # -----------------------------------------------------

    if (
        SearchStrategy.ROLE.value
        not in attempted_strategies
    ):

        return SearchStrategy.ROLE

    # -----------------------------------------------------
    # Default
    # -----------------------------------------------------

    return SearchStrategy.DOMAIN


# =========================================================
# Mock RecruitOS Search
# =========================================================

def mock_recruitos_search(
    query,
    strategy,
    required_skills
):

    # -----------------------------------------------------
    # EXACT_SKILL search
    # -----------------------------------------------------

    if strategy == SearchStrategy.EXACT_SKILL.value:

        return [
            {
                "name": "Ahmed",
                "skills": [
                    "Python",
                    "RAG",
                    "FastAPI"
                ],
                "experience": {
                    "Python": 6,
                    "RAG": 3,
                    "FastAPI": 3
                }
            }
        ]

    # -----------------------------------------------------
    # RELATED_SKILL search
    # -----------------------------------------------------

    if strategy == SearchStrategy.RELATED_SKILL.value:

        return [
            {
                "name": "Sara",
                "skills": [
                    "Python",
                    "FastAPI"
                ],
                "experience": {
                    "Python": 5,
                    "FastAPI": 2
                }
            }
        ]

    # -----------------------------------------------------
    # ROLE search
    # -----------------------------------------------------

    if strategy == SearchStrategy.ROLE.value:

        return [
            {
                "name": "John",
                "skills": [
                    "Python"
                ],
                "experience": {
                    "Python": 6
                }
            }
        ]

    # -----------------------------------------------------
    # DOMAIN search
    # -----------------------------------------------------

    return []


# =========================================================
# Create Initial State
# =========================================================

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

        # -------------------------------------------------
        # Recruiter goal and JD
        # -------------------------------------------------

        "goal": (
            "Find candidates for "
            "Python RAG Developer"
        ),

        "jd_text": jd_text,

        "target_count": target_count,

        # -------------------------------------------------
        # Candidate results
        # -------------------------------------------------

        "candidates": [],

        "qualified_candidates": [],

        # -------------------------------------------------
        # Search loop tracking
        # -------------------------------------------------

        "attempt": 0,

        "current_strategy": "",

        "attempted_strategies": [],

        "current_query": "",

        # -------------------------------------------------
        # Last search metrics
        # -------------------------------------------------

        "last_search_candidates": 0,

        "last_search_qualified": 0,

        "last_search_duplicates": 0,

        # -------------------------------------------------
        # Loop progress tracking
        # -------------------------------------------------

        "no_progress_count": 0,

        # -------------------------------------------------
        # Current search results
        # -------------------------------------------------

        "current_search_results": [],

        "current_qualified_results": [],

        # -------------------------------------------------
        # JD qualification information
        # -------------------------------------------------

        "required_skills": [],

        "required_skill_experience": {},

        # -------------------------------------------------
        # Loop observability
        # -------------------------------------------------

        "total_searches": 0,

        "total_duplicates": 0,

        "total_qualified": 0,

        # -------------------------------------------------
        # Loop termination information
        # -------------------------------------------------

        "stop_reason": ""
    }


# =========================================================
# Run Search Graph
# =========================================================

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


# =========================================================
# Test: Search Graph Uses JD Skills
# =========================================================

def test_search_graph_uses_jd_skills():

    result = run_test_graph(
        target_count=1
    )

    assert result["required_skills"]

    assert "Python" in result["required_skills"]

    assert "RAG" in result["required_skills"]

    assert "FastAPI" in result["required_skills"]


# =========================================================
# Test: Search Graph Finds Qualified Candidate
# =========================================================

def test_search_graph_preserves_qualified_candidate():

    result = run_test_graph(
        target_count=1
    )

    qualified_candidates = (
        result["qualified_candidates"]
    )

    assert len(
        qualified_candidates
    ) >= 1

    names = [
        candidate["name"]
        for candidate in qualified_candidates
    ]

    assert "Ahmed" in names


# =========================================================
# Test: Search Graph Stops When No Progress
# =========================================================

def test_search_graph_stops_when_no_progress():

    result = run_test_graph(
        target_count=10
    )

    assert result["stop_reason"] in [
        "NO_PROGRESS",
        "MAX_ATTEMPTS",
        "DUPLICATE_RESULTS"
    ]


# =========================================================
# Test: Search Graph Does Not Loop Forever
# =========================================================

def test_search_graph_does_not_loop_forever():

    result = run_test_graph(
        target_count=10
    )

    assert result["attempt"] <= 6


# =========================================================
# Test: Search Graph Stops At Maximum Attempts
# =========================================================

def test_search_graph_stops_at_max_attempts():

    result = run_test_graph(
        target_count=10
    )

    assert result["attempt"] <= 6


# =========================================================
# Test: Search Graph Tracks Search Attempts
# =========================================================

def test_search_graph_tracks_search_attempts():

    result = run_test_graph(
        target_count=1
    )

    assert result["total_searches"] >= 1

    assert result["attempt"] >= 1


# =========================================================
# Test: Search Graph Tracks Attempted Strategies
# =========================================================

def test_search_graph_tracks_attempted_strategies():

    result = run_test_graph(
        target_count=1
    )

    assert len(
        result["attempted_strategies"]
    ) >= 1


# =========================================================
# Test: Search Graph Produces Qualified Candidate
# =========================================================

def test_search_graph_produces_qualified_candidate():

    result = run_test_graph(
        target_count=1
    )

    assert len(
        result["qualified_candidates"]
    ) >= 1

    candidate = (
        result["qualified_candidates"][0]
    )

    assert candidate["name"] == "Ahmed"


# =========================================================
# Test: Search Graph Records Stop Reason
# =========================================================

def test_search_graph_records_stop_reason():

    result = run_test_graph(
        target_count=10
    )

    assert result["stop_reason"] != ""