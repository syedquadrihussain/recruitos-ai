from app.services.search_state import SearchState


MAX_SEARCH_ATTEMPTS = 6


def should_stop_search(
    state: SearchState
) -> bool:

    # Safety boundary:
    # Never allow the agent to search forever.

    if state["attempt"] >= MAX_SEARCH_ATTEMPTS:

        print(
            "\nMaximum search attempts reached."
        )

        print(
            "Stopping loop safely."
        )

        return True

    # No-progress condition:
    # If every candidate returned by the latest
    # search was already seen, the search is not
    # discovering anything new.

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