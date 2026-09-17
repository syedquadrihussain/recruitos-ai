from app.services.search_state import SearchState


def observe_search_results(
    state: SearchState,
    search_results: list,
    qualified_results: list
) -> SearchState:

    existing_candidates = {
        candidate["name"]
        for candidate in state["candidates"]
    }

    existing_qualified_candidates = {
        candidate["name"]
        for candidate in state["qualified_candidates"]
    }

    new_candidates = []
    new_qualified_candidates = []

    duplicate_count = 0

    # ---------------------------------------------------------
    # Observe search results
    # ---------------------------------------------------------

    for candidate in search_results:

        candidate_name = candidate["name"]

        if candidate_name in existing_candidates:

            duplicate_count += 1

        else:

            new_candidates.append(candidate)

            existing_candidates.add(
                candidate_name
            )

    # ---------------------------------------------------------
    # Observe qualified results
    # ---------------------------------------------------------

    for candidate in qualified_results:

        candidate_name = candidate["name"]

        if candidate_name not in existing_qualified_candidates:

            new_qualified_candidates.append(candidate)

            existing_qualified_candidates.add(
                candidate_name
            )

    # ---------------------------------------------------------
    # Update accumulated candidates
    # ---------------------------------------------------------

    state["candidates"] = (
        state["candidates"]
        + new_candidates
    )

    state["qualified_candidates"] = (
        state["qualified_candidates"]
        + new_qualified_candidates
    )

    # ---------------------------------------------------------
    # Save current search metrics
    # ---------------------------------------------------------

    state["last_search_candidates"] = (
        len(search_results)
    )

    state["last_search_qualified"] = (
        len(qualified_results)
    )

    state["last_search_duplicates"] = (
        duplicate_count
    )

    # ---------------------------------------------------------
    # Progress tracking
    # ---------------------------------------------------------

    new_qualified_count = (
        len(new_qualified_candidates)
    )

    if new_qualified_count > 0:

        state["no_progress_count"] = 0

        print(
            f"\nProgress detected:"
            f" {new_qualified_count} "
            f"new qualified candidate(s)."
        )

    else:

        state["no_progress_count"] += 1

        print(
            f"\nNo new qualified candidates."
        )

        print(
            f"Consecutive no-progress count: "
            f"{state['no_progress_count']}"
        )

    return state