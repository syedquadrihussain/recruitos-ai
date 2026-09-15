from app.services.candidate_store import (
    candidate_profiles,
    get_candidate
)

from app.services.embedding_service import (
    create_embeddings
)

from app.services.vector_store import (
    search_embeddings,
    load_chunks
)

from app.services.reranker import (
    rerank_candidates
)


def _get_candidate_profiles(candidate_ids):

    candidates = []

    for candidate_id in candidate_ids:

        candidate = get_candidate(
            candidate_id
        )

        if candidate:

            candidate_copy = candidate.copy()

            candidate_copy["candidate_id"] = (
                candidate_id
            )

            candidates.append(
                candidate_copy
            )

    return candidates


def _unique_candidate_ids(results):

    candidate_ids = []

    for result in results:

        candidate_id = result["candidate_id"]

        if candidate_id not in candidate_ids:

            candidate_ids.append(
                candidate_id
            )

    return candidate_ids


def _semantic_search(query, top_k=5):

    query_embedding = create_embeddings(
        [query]
    )[0]

    chunks = load_chunks()

    results = search_embeddings(
        query_embedding,
        chunks,
        top_k=top_k
    )

    candidate_ids = _unique_candidate_ids(
        results
    )

    return _get_candidate_profiles(
        candidate_ids
    )


def _skill_search(
    skills,
    include_all=False
):

    matching_candidates = []

    for candidate_id, candidate in (
        candidate_profiles.items()
    ):

        candidate_skills = {
            skill.lower()
            for skill in candidate["skills"]
        }

        requested_skills = {
            skill.lower()
            for skill in skills
        }

        if include_all:

            if requested_skills.issubset(
                candidate_skills
            ):

                candidate_copy = candidate.copy()

                candidate_copy["candidate_id"] = (
                    candidate_id
                )

                matching_candidates.append(
                    candidate_copy
                )

        else:

            if requested_skills.intersection(
                candidate_skills
            ):

                candidate_copy = candidate.copy()

                candidate_copy["candidate_id"] = (
                    candidate_id
                )

                matching_candidates.append(
                    candidate_copy
                )

    return matching_candidates


def _role_search(
    query,
    required_skills
):

    semantic_candidates = _semantic_search(
        f"{query} developer engineer",
        top_k=5
    )

    skill_candidates = _skill_search(
        required_skills,
        include_all=False
    )

    candidates = (
        semantic_candidates
        + skill_candidates
    )

    unique_candidates = {}

    for candidate in candidates:

        unique_candidates[
            candidate["candidate_id"]
        ] = candidate

    return list(
        unique_candidates.values()
    )


def _domain_search(
    query,
    required_skills
):

    domain_candidates = _semantic_search(
        f"{query} technology domain",
        top_k=5
    )

    skill_candidates = _skill_search(
        required_skills,
        include_all=False
    )

    candidates = (
        domain_candidates
        + skill_candidates
    )

    unique_candidates = {}

    for candidate in candidates:

        unique_candidates[
            candidate["candidate_id"]
        ] = candidate

    return list(
        unique_candidates.values()
    )


def _hybrid_search(
    query,
    required_skills
):

    semantic_candidates = _semantic_search(
        query,
        top_k=5
    )

    skill_candidates = _skill_search(
        required_skills,
        include_all=False
    )

    candidates = (
        semantic_candidates
        + skill_candidates
    )

    unique_candidates = {}

    for candidate in candidates:

        unique_candidates[
            candidate["candidate_id"]
        ] = candidate

    return list(
        unique_candidates.values()
    )


def _source_search(
    query
):

    return _semantic_search(
        f"{query} candidate resume profile",
        top_k=5
    )


def search_recruitos(
    query,
    strategy,
    required_skills=None,
    top_k=5
):

    if not query.strip():

        return []

    if required_skills is None:

        required_skills = []

    strategy = strategy.upper()

    # -----------------------------------------
    # 1. EXACT SKILL SEARCH
    # -----------------------------------------

    if strategy == "EXACT_SKILL":

        if not required_skills:

            return []

        candidates = _skill_search(
            [required_skills[0]],
            include_all=False
        )

    # -----------------------------------------
    # 2. RELATED SKILL SEARCH
    # -----------------------------------------

    elif strategy == "RELATED_SKILL":

        candidates = _skill_search(
            required_skills,
            include_all=False
        )

    # -----------------------------------------
    # 3. ROLE SEARCH
    # -----------------------------------------

    elif strategy == "ROLE":

        candidates = _role_search(
            query,
            required_skills
        )

    # -----------------------------------------
    # 4. DOMAIN SEARCH
    # -----------------------------------------

    elif strategy == "DOMAIN":

        candidates = _domain_search(
            query,
            required_skills
        )

    # -----------------------------------------
    # 5. SEMANTIC SEARCH
    # -----------------------------------------

    elif strategy == "SEMANTIC_SEARCH":

        candidates = _semantic_search(
            query,
            top_k=top_k
        )

    # -----------------------------------------
    # 6. HYBRID SEARCH
    # -----------------------------------------

    elif strategy == "HYBRID_SEARCH":

        candidates = _hybrid_search(
            query,
            required_skills
        )

    # -----------------------------------------
    # 7. SOURCE SEARCH
    # -----------------------------------------

    elif strategy == "SOURCE_SEARCH":

        candidates = _source_search(
            query
        )

    # -----------------------------------------
    # Unknown strategy
    # -----------------------------------------

    else:

        candidates = _semantic_search(
            query,
            top_k=top_k
        )

    # -----------------------------------------
    # RERANK
    # -----------------------------------------

    if required_skills:

        candidates = rerank_candidates(
            candidates,
            required_skills
        )

        candidates.sort(
            key=lambda candidate: candidate["score"],
            reverse=True
        )

    return candidates