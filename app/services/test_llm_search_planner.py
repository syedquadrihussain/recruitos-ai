from unittest.mock import patch

from app.services.llm_search_planner import (
    choose_strategy_with_llm,
    ALLOWED_STRATEGIES
)


def create_test_state():

    return {
        "goal": "Find Python RAG candidates",

        "target_count": 10,

        "candidates": [
            {
                "name": "Ahmed",
                "skills": [
                    "Python",
                    "RAG"
                ]
            }
        ],

        "qualified_candidates": [
            {
                "name": "Ahmed",
                "skills": [
                    "Python",
                    "RAG"
                ]
            }
        ],

        "attempt": 1,

        "current_strategy": "EXACT_SKILL",

        "current_query": (
            "EXACT_SKILL search for "
            "Find Python RAG candidates"
        ),

        "last_search_candidates": 1,

        "last_search_qualified": 1,

        "last_search_duplicates": 0,

        "current_search_results": [],

        "current_qualified_results": []
    }


def test_llm_planner_returns_allowed_strategy():

    state = create_test_state()

    strategy = choose_strategy_with_llm(
        state
    )

    assert strategy.value in ALLOWED_STRATEGIES


def test_allowed_strategies_are_controlled():

    assert ALLOWED_STRATEGIES == [
        "EXACT_SKILL",
        "RELATED_SKILL",
        "ROLE",
        "DOMAIN",
        "SEMANTIC_SEARCH",
        "HYBRID_SEARCH",
        "SOURCE_SEARCH"
    ]


def test_llm_planner_rejects_invalid_strategy():

    state = create_test_state()

    with patch(
        "app.services.llm_search_planner.client.chat.completions.create"
    ) as mock_create:

        mock_create.return_value.choices[0].message.content = (
            "SEARCH_ALL_INTERNET"
        )

        try:

            choose_strategy_with_llm(
                state
            )

            assert False, (
                "Expected ValueError "
                "for invalid strategy"
            )

        except ValueError as error:

            assert "invalid strategy" in str(
                error
            ).lower()