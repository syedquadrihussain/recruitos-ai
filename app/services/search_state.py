from typing import TypedDict


class SearchState(TypedDict):

    goal: str
    jd_text: str
    target_count: int

    candidates: list
    qualified_candidates: list

    attempt: int

    current_strategy: str
    current_query: str

    last_search_candidates: int
    last_search_qualified: int
    last_search_duplicates: int

    current_search_results: list
    current_qualified_results: list