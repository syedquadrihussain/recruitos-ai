from app.services.search_strategies import SearchStrategy
from app.services.search_state import SearchState


def choose_search_strategy(
    state: SearchState
) -> SearchStrategy:

    attempt = state["attempt"]

    current_strategy = state["current_strategy"]

    qualified_count = len(
        state["qualified_candidates"]
    )

    target_count = state["target_count"]

    if qualified_count >= target_count:

        return SearchStrategy.EXACT_SKILL

    if attempt == 0:

        return SearchStrategy.EXACT_SKILL

    if current_strategy == SearchStrategy.EXACT_SKILL.value:

        return SearchStrategy.RELATED_SKILL

    if current_strategy == SearchStrategy.RELATED_SKILL.value:

        return SearchStrategy.ROLE

    if current_strategy == SearchStrategy.ROLE.value:

        return SearchStrategy.DOMAIN

    if current_strategy == SearchStrategy.DOMAIN.value:

        return SearchStrategy.SEMANTIC_SEARCH

    if current_strategy == SearchStrategy.SEMANTIC_SEARCH.value:

        return SearchStrategy.HYBRID_SEARCH

    if current_strategy == SearchStrategy.HYBRID_SEARCH.value:

        return SearchStrategy.SOURCE_SEARCH

    return SearchStrategy.SOURCE_SEARCH