from app.services.search_graph import (
    validate_strategy
)

from app.services.search_strategies import (
    SearchStrategy
)


def test_unused_strategy_is_accepted():
    attempted_strategies = [
        SearchStrategy.EXACT_SKILL.value,
        SearchStrategy.RELATED_SKILL.value
    ]

    result = validate_strategy(
        SearchStrategy.ROLE,
        attempted_strategies
    )

    assert result == SearchStrategy.ROLE


def test_attempted_strategy_is_replaced():
    attempted_strategies = [
        SearchStrategy.EXACT_SKILL.value,
        SearchStrategy.RELATED_SKILL.value
    ]

    result = validate_strategy(
        SearchStrategy.RELATED_SKILL,
        attempted_strategies
    )

    assert result != SearchStrategy.RELATED_SKILL

    assert (
        result.value
        not in attempted_strategies
    )


def test_all_strategies_attempted():
    attempted_strategies = [
        strategy.value
        for strategy in SearchStrategy
    ]

    selected_strategy = (
        SearchStrategy.RELATED_SKILL
    )

    result = validate_strategy(
        selected_strategy,
        attempted_strategies
    )

    assert result == selected_strategy