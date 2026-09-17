from typing import TypedDict


class SearchState(TypedDict):

    # =====================================================
    # Recruiter goal and Job Description
    # =====================================================

    goal: str
    jd_text: str
    target_count: int

    # =====================================================
    # Candidate results
    # =====================================================

    candidates: list
    qualified_candidates: list

    # =====================================================
    # Search loop tracking
    # =====================================================

    attempt: int

    current_strategy: str
    attempted_strategies: list

    current_query: str

    # =====================================================
    # Last search metrics
    # =====================================================

    last_search_candidates: int
    last_search_qualified: int
    last_search_duplicates: int

    # =====================================================
    # Loop progress tracking
    # =====================================================

    no_progress_count: int

    # =====================================================
    # Current search results
    # =====================================================

    current_search_results: list
    current_qualified_results: list

    # =====================================================
    # JD qualification information
    # =====================================================

    required_skills: list
    required_skill_experience: dict