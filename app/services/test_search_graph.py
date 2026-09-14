from app.services.search_graph import build_search_graph


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


def test_search_graph_reaches_endpoint():

    search_graph = build_search_graph()

    initial_state = create_initial_state(
        target_count=3
    )

    final_state = search_graph.invoke(
        initial_state
    )

    assert len(
        final_state["qualified_candidates"]
    ) >= 3


def test_search_graph_stops_after_reaching_target():

    search_graph = build_search_graph()

    initial_state = create_initial_state(
        target_count=3
    )

    final_state = search_graph.invoke(
        initial_state
    )

    assert (
        len(final_state["qualified_candidates"])
        >= final_state["target_count"]
    )


def test_search_graph_updates_attempt_count():

    search_graph = build_search_graph()

    initial_state = create_initial_state(
        target_count=3
    )

    final_state = search_graph.invoke(
        initial_state
    )

    assert final_state["attempt"] == 3


def test_search_graph_returns_expected_candidates():

    search_graph = build_search_graph()

    initial_state = create_initial_state(
        target_count=3
    )

    final_state = search_graph.invoke(
        initial_state
    )

    candidate_names = [
        candidate["name"]
        for candidate
        in final_state["qualified_candidates"]
    ]

    assert "Ahmed" in candidate_names
    assert "Sara" in candidate_names
    assert "Priya" in candidate_names