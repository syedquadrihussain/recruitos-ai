from app.services.search_planner import choose_search_strategy


def test_first_search_uses_exact_skill():

    state = {
        "goal": "Find Python RAG candidates",
        "target_count": 20,
        "candidates": [],
        "qualified_candidates": [],
        "attempt": 0,
        "current_strategy": "",
        "current_query": "",
        "last_search_candidates": 0,
        "last_search_qualified": 0,
        "last_search_duplicates": 0
    }

    strategy = choose_search_strategy(
        state
    )

    assert strategy.value == "EXACT_SKILL"


def test_planner_moves_from_exact_to_related():

    state = {
        "goal": "Find Python RAG candidates",
        "target_count": 20,
        "candidates": [],
        "qualified_candidates": [
            {"name": "Ahmed"},
            {"name": "Sara"}
        ],
        "attempt": 1,
        "current_strategy": "EXACT_SKILL",
        "current_query": "Python RAG",
        "last_search_candidates": 4,
        "last_search_qualified": 2,
        "last_search_duplicates": 2
    }

    strategy = choose_search_strategy(
        state
    )

    assert strategy.value == "RELATED_SKILL"


def test_planner_moves_to_semantic_search():

    state = {
        "goal": "Find Python RAG candidates",
        "target_count": 20,
        "candidates": [],
        "qualified_candidates": [
            {"name": "Ahmed"}
        ],
        "attempt": 4,
        "current_strategy": "DOMAIN",
        "current_query": "Generative AI",
        "last_search_candidates": 3,
        "last_search_qualified": 1,
        "last_search_duplicates": 2
    }

    strategy = choose_search_strategy(
        state
    )

    assert strategy.value == "SEMANTIC_SEARCH"