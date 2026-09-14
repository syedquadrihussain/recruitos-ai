from unittest.mock import patch

from app.services.search_graph import (
    build_search_graph
)


def create_initial_state(target_count):

    return {
        "goal": "Find Python RAG candidates",

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


def mock_llm_planner(state):

    strategies = [
        "EXACT_SKILL",
        "RELATED_SKILL",
        "ROLE"
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


def run_test_graph():

    with patch(
        "app.services.search_graph.choose_strategy_with_llm",
        side_effect=mock_llm_planner
    ):

        search_graph = build_search_graph()

        initial_state = create_initial_state(
            target_count=3
        )

        return search_graph.invoke(
            initial_state
        )


def test_search_graph_reaches_endpoint():

    final_state = run_test_graph()

    assert len(
        final_state["qualified_candidates"]
    ) >= 3


def test_search_graph_stops_after_reaching_target():

    final_state = run_test_graph()

    assert (
        len(final_state["qualified_candidates"])
        >= final_state["target_count"]
    )


def test_search_graph_updates_attempt_count():

    final_state = run_test_graph()

    assert final_state["attempt"] == 3


def test_search_graph_returns_expected_candidates():

    final_state = run_test_graph()

    candidate_names = [
        candidate["name"]
        for candidate
        in final_state["qualified_candidates"]
    ]

    assert "Ahmed" in candidate_names
    assert "Sara" in candidate_names
    assert "Priya" in candidate_names