from app.services.search_observer import (
    observe_search_results
)


def test_observer_tracks_new_candidates_and_duplicates():

    state = {
        "goal": "Find Python RAG candidates",
        "target_count": 5,
        "candidates": [
            {
                "name": "Ahmed"
            }
        ],
        "qualified_candidates": [],
        "attempt": 1,
        "current_strategy": "EXACT_SKILL",
        "current_query": "Python RAG",
        "last_search_candidates": 0,
        "last_search_qualified": 0,
        "last_search_duplicates": 0
    }

    search_results = [
        {
            "name": "Ahmed"
        },
        {
            "name": "Sara"
        },
        {
            "name": "John"
        }
    ]

    qualified_results = [
        {
            "name": "Sara"
        }
    ]

    updated_state = observe_search_results(
        state,
        search_results,
        qualified_results
    )

    assert len(
        updated_state["candidates"]
    ) == 3

    assert len(
        updated_state["qualified_candidates"]
    ) == 1

    assert (
        updated_state["last_search_candidates"]
        == 3
    )

    assert (
        updated_state["last_search_qualified"]
        == 1
    )

    assert (
        updated_state["last_search_duplicates"]
        == 1
    )


def test_observer_does_not_duplicate_qualified_candidates():

    state = {
        "goal": "Find Python RAG candidates",
        "target_count": 5,
        "candidates": [
            {
                "name": "Ahmed"
            }
        ],
        "qualified_candidates": [
            {
                "name": "Ahmed"
            }
        ],
        "attempt": 1,
        "current_strategy": "EXACT_SKILL",
        "current_query": "Python RAG",
        "last_search_candidates": 0,
        "last_search_qualified": 0,
        "last_search_duplicates": 0
    }

    search_results = [
        {
            "name": "Ahmed"
        }
    ]

    qualified_results = [
        {
            "name": "Ahmed"
        }
    ]

    updated_state = observe_search_results(
        state,
        search_results,
        qualified_results
    )

    assert len(
        updated_state["qualified_candidates"]
    ) == 1