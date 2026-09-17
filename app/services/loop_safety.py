from app.services.search_state import SearchState


MAX_SEARCH_ATTEMPTS = 6

MAX_NO_PROGRESS_ATTEMPTS = 3


def should_stop_search(
    state: SearchState
) -> bool:

    # ---------------------------------------------------------
    # Safety boundary: maximum attempts
    # ---------------------------------------------------------

    if state["attempt"] >= MAX_SEARCH_ATTEMPTS:

        print(
            "\nMaximum search attempts reached."
        )

        print(
            "Stopping loop safely."
        )

        return True

    # ---------------------------------------------------------
    # No-progress safety boundary
    # ---------------------------------------------------------

    if (
        state["no_progress_count"]
        >= MAX_NO_PROGRESS_ATTEMPTS
    ):

        print(
            "\nRepeated no-progress detected."
        )

        print(
            "The search is not discovering "
            "new qualified candidates."
        )

        print(
            "Stopping loop safely."
        )

        return True

    # ---------------------------------------------------------
    # Duplicate-result safety boundary
    # ---------------------------------------------------------

    if (
        state["last_search_candidates"] > 0
        and
        state["last_search_duplicates"]
        >= state["last_search_candidates"]
    ):

        print(
            "\nNo search progress detected."
        )

        print(
            "All returned candidates "
            "were already discovered."
        )

        print(
            "Stopping loop safely."
        )

        return True

    return False