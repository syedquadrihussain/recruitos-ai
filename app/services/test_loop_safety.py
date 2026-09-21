from app.services.loop_safety import (
    should_stop_search,
    MAX_SEARCH_ATTEMPTS
)


def create_state():

    return {

        "goal": "Find Python RAG candidates",

        "target_count": 3,

        "candidates": [],

        "qualified_candidates": [],

        "attempt": 1,

        "current_strategy": "ROLE",

        "attempted_strategies": [],

        "current_query": "",

        "last_search_candidates": 1,

        "last_search_qualified": 1,

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


def test_no_progress_stops_search():

    state = create_state()

    state["last_search_candidates"] = 1
    state["last_search_duplicates"] = 1

    assert should_stop_search(state) is True


def test_new_candidate_allows_search_to_continue():

    state = create_state()

    state["last_search_candidates"] = 1
    state["last_search_duplicates"] = 0

    assert should_stop_search(state) is False


def test_max_attempts_stops_search():

    state = create_state()

    state["attempt"] = MAX_SEARCH_ATTEMPTS

    assert should_stop_search(state) is True