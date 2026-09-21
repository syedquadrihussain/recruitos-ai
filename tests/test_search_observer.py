from app.services.search_observer import (
    observe_search_results
)


def create_state():
    return {
        "goal": "Find qualified Python FastAPI RAG developers",
        "jd_text": "",
        "target_count": 5,
        "candidates": [],
        "qualified_candidates": [],
        "attempt": 0,
        "current_strategy": "",
        "attempted_strategies": [],
        "current_query": "",
        "last_search_candidates": 0,
        "last_search_qualified": 0,
        "last_search_duplicates": 0,
        "no_progress_count": 0,
        "current_search_results": [],
        "current_qualified_results": [],
        "required_skills": [],
        "required_skill_experience": {},
        "total_searches": 0,
        "total_duplicates": 0,
        "total_qualified": 0,
        "stop_reason": ""
    }


def test_new_candidates_are_added():
    state = create_state()

    search_results = [
        {"name": "Ahmed"},
        {"name": "David"}
    ]

    qualified_results = [
        {"name": "Ahmed"}
    ]

    result = observe_search_results(
        state,
        search_results,
        qualified_results
    )

    assert len(result["candidates"]) == 2
    assert len(result["qualified_candidates"]) == 1
    assert result["qualified_candidates"][0]["name"] == "Ahmed"


def test_duplicate_candidates_are_not_added():
    state = create_state()

    state["candidates"] = [
        {"name": "Ahmed"}
    ]

    search_results = [
        {"name": "Ahmed"},
        {"name": "David"}
    ]

    qualified_results = [
        {"name": "David"}
    ]

    result = observe_search_results(
        state,
        search_results,
        qualified_results
    )

    assert len(result["candidates"]) == 2
    assert result["candidates"][1]["name"] == "David"
    assert result["last_search_duplicates"] == 1


def test_qualified_candidates_are_not_duplicated():
    state = create_state()

    state["qualified_candidates"] = [
        {"name": "Ahmed"}
    ]

    search_results = [
        {"name": "Ahmed"},
        {"name": "David"}
    ]

    qualified_results = [
        {"name": "Ahmed"},
        {"name": "David"}
    ]

    result = observe_search_results(
        state,
        search_results,
        qualified_results
    )

    assert len(result["qualified_candidates"]) == 2
    assert result["qualified_candidates"][1]["name"] == "David"


def test_progress_resets_no_progress_counter():
    state = create_state()

    state["no_progress_count"] = 2

    search_results = [
        {"name": "Ahmed"}
    ]

    qualified_results = [
        {"name": "Ahmed"}
    ]

    result = observe_search_results(
        state,
        search_results,
        qualified_results
    )

    assert result["no_progress_count"] == 0


def test_no_progress_increments_counter():
    state = create_state()

    state["no_progress_count"] = 1

    search_results = [
        {"name": "Ahmed"}
    ]

    qualified_results = []

    result = observe_search_results(
        state,
        search_results,
        qualified_results
    )

    assert result["no_progress_count"] == 2


def test_loop_metrics_are_updated():
    state = create_state()

    search_results = [
        {"name": "Ahmed"},
        {"name": "David"}
    ]

    qualified_results = [
        {"name": "Ahmed"},
        {"name": "David"}
    ]

    result = observe_search_results(
        state,
        search_results,
        qualified_results
    )

    assert result["total_searches"] == 1
    assert result["total_duplicates"] == 0
    assert result["total_qualified"] == 2
    assert result["last_search_candidates"] == 2
    assert result["last_search_qualified"] == 2