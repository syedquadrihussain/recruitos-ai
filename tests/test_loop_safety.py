from app.services.loop_safety import (
    get_stop_reason,
    should_stop_search,
    MAX_SEARCH_ATTEMPTS,
    MAX_NO_PROGRESS_ATTEMPTS
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


def test_no_safety_condition():
    state = create_state()

    assert get_stop_reason(state) == ""
    assert should_stop_search(state) is False


def test_max_attempts():
    state = create_state()

    state["attempt"] = MAX_SEARCH_ATTEMPTS

    assert get_stop_reason(state) == "MAX_ATTEMPTS"
    assert should_stop_search(state) is True
    assert state["stop_reason"] == "MAX_ATTEMPTS"


def test_no_progress():
    state = create_state()

    state["no_progress_count"] = (
        MAX_NO_PROGRESS_ATTEMPTS
    )

    assert get_stop_reason(state) == "NO_PROGRESS"
    assert should_stop_search(state) is True
    assert state["stop_reason"] == "NO_PROGRESS"


def test_duplicate_results():
    state = create_state()

    state["last_search_candidates"] = 6
    state["last_search_duplicates"] = 6

    assert get_stop_reason(state) == "DUPLICATE_RESULTS"
    assert should_stop_search(state) is True
    assert state["stop_reason"] == "DUPLICATE_RESULTS"


def test_partial_duplicates_do_not_stop():
    state = create_state()

    state["last_search_candidates"] = 6
    state["last_search_duplicates"] = 3

    assert get_stop_reason(state) == ""
    assert should_stop_search(state) is False