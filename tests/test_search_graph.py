from app.services.search_graph import (
    endpoint_check
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


def test_target_reached_stops_loop():
    state = create_state()

    state["stop_reason"] = "TARGET_REACHED"

    result = endpoint_check(state)

    assert result == "stop"


def test_duplicate_results_stops_loop():
    state = create_state()

    state["stop_reason"] = "DUPLICATE_RESULTS"

    result = endpoint_check(state)

    assert result == "stop"


def test_no_progress_stops_loop():
    state = create_state()

    state["stop_reason"] = "NO_PROGRESS"

    result = endpoint_check(state)

    assert result == "stop"


def test_max_attempts_stops_loop():
    state = create_state()

    state["stop_reason"] = "MAX_ATTEMPTS"

    result = endpoint_check(state)

    assert result == "stop"


def test_no_stop_reason_continues_loop():
    state = create_state()

    result = endpoint_check(state)

    assert result == "continue"