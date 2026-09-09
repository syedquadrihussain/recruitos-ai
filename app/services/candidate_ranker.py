def rank_candidates(screening_results):

    qualified_candidates = []
    unqualified_candidates = []

    for result in screening_results:

        if result["qualified"]:
            qualified_candidates.append(result)

        else:
            unqualified_candidates.append(result)

    # Sort qualified candidates by final score
    qualified_candidates.sort(
        key=lambda candidate: candidate["final_score"],
        reverse=True
    )

    # Sort unqualified candidates by final score
    unqualified_candidates.sort(
        key=lambda candidate: candidate["final_score"],
        reverse=True
    )

    if len(qualified_candidates) == 0:

        print("\nNO EXACT MATCH FOUND.")
        print("Showing closest candidates instead.")

        return unqualified_candidates

    return qualified_candidates + unqualified_candidates