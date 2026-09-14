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

    new_candidates = []
    duplicate_count = 0

    for candidate in search_results:

        candidate_name = candidate["name"]

        if candidate_name in existing_candidates:

            duplicate_count += 1

        else:

            new_candidates.append(candidate)

            existing_candidates.add(
                candidate_name
            )

    updated_candidates = (
        state["candidates"]
        + new_candidates
    )

    updated_qualified_candidates = (
        state["qualified_candidates"]
        + [
            candidate
            for candidate in qualified_results
            if candidate["name"]
            not in {
                existing["name"]
                for existing
                in state["qualified_candidates"]
            }
        ]
    )

    state["candidates"] = updated_candidates

    state["qualified_candidates"] = (
        updated_qualified_candidates
    )

    state["last_search_candidates"] = (
        len(search_results)
    )

    state["last_search_qualified"] = (
        len(qualified_results)
    )

    state["last_search_duplicates"] = (
        duplicate_count
    )

    return state