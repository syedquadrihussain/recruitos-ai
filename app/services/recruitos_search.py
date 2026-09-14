from app.services.candidate_store import get_candidate
from app.services.embedding_service import create_embeddings
from app.services.vector_store import (
    search_embeddings,
    load_chunks
)
from app.services.reranker import rerank_candidates


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


def _exact_skill_search(skill):

    from app.services.candidate_store import candidate_profiles

    matching_candidates = []

    for candidate_id, candidate in (
        candidate_profiles.items()
    ):

        candidate_skills = [
            candidate_skill.lower()
            for candidate_skill
            in candidate["skills"]
        ]

        if skill.lower() in candidate_skills:

            candidate_copy = candidate.copy()

            candidate_copy["candidate_id"] = (
                candidate_id
            )

            matching_candidates.append(
                candidate_copy
            )

    return matching_candidates


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

    if strategy == "EXACT_SKILL":

        if not required_skills:

            return []

        candidates = _exact_skill_search(
            required_skills[0]
        )

    else:

        strategy_queries = {

            "RELATED_SKILL": (
                f"{query} related technologies"
            ),

            "ROLE": (
                f"{query} developer engineer"
            ),

            "DOMAIN": (
                f"{query} technology domain"
            ),

            "SEMANTIC_SEARCH": (
                f"{query}"
            ),

            "HYBRID_SEARCH": (
                f"{query} "
                f"{' '.join(required_skills)}"
            ),

            "SOURCE_SEARCH": (
                f"{query} candidate resume"
            )
        }

        search_query = strategy_queries.get(
            strategy,
            query
        )

        candidates = _semantic_search(
            search_query,
            top_k=top_k
        )

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