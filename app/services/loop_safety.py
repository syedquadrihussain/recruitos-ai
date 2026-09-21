from app.services.search_state import SearchState


# =========================================================
# Loop Safety Limits
# =========================================================

MAX_SEARCH_ATTEMPTS = 6

MAX_NO_PROGRESS_ATTEMPTS = 3


# =========================================================
# Determine Stop Reason
# =========================================================

def get_stop_reason(
    state: SearchState
) -> str:

    # -----------------------------------------------------
    # Maximum search attempts
    # -----------------------------------------------------

    if (
        state["attempt"]
        >= MAX_SEARCH_ATTEMPTS
    ):

        return "MAX_ATTEMPTS"

    # -----------------------------------------------------
    # Repeated no-progress
    # -----------------------------------------------------

    if (
        state["no_progress_count"]
        >= MAX_NO_PROGRESS_ATTEMPTS
    ):

        return "NO_PROGRESS"

    # -----------------------------------------------------
    # All returned candidates are duplicates
    # -----------------------------------------------------

    if (
        state["last_search_candidates"] > 0
        and
        state["last_search_duplicates"]
        >= state["last_search_candidates"]
    ):

        return "DUPLICATE_RESULTS"

    # -----------------------------------------------------
    # No safety boundary reached
    # -----------------------------------------------------

    return ""


# =========================================================
# Should Stop Search
# =========================================================

def should_stop_search(
    state: SearchState
) -> bool:

    stop_reason = get_stop_reason(
        state
    )

    # -----------------------------------------------------
    # No safety condition
    # -----------------------------------------------------

    if not stop_reason:

        return False

    # -----------------------------------------------------
    # Save stop reason
    # -----------------------------------------------------

    state["stop_reason"] = stop_reason

    # -----------------------------------------------------
    # Maximum attempts
    # -----------------------------------------------------

    if stop_reason == "MAX_ATTEMPTS":

        print(
            "\nMaximum search attempts reached."
        )

        print(
            "Stopping loop safely."
        )

        return True

    # -----------------------------------------------------
    # No progress
    # -----------------------------------------------------

    if stop_reason == "NO_PROGRESS":

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

    # -----------------------------------------------------
    # Duplicate results
    # -----------------------------------------------------

    if stop_reason == "DUPLICATE_RESULTS":

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