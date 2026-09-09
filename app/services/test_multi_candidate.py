from app.services.candidate_store import get_candidate
from app.services.candidate_matcher import check_candidate
from app.services.candidate_ranker import rank_candidates
from app.services.reranker import rerank_candidates
from app.services.vector_store import search_embeddings, load_chunks
from app.services.embedding_service import create_embeddings


# --------------------------------
# Job Description
# --------------------------------

job_description = """
Python Developer

Must Have:

Python 5 years
FastAPI 3 years

Nice to Have:

RAG
Docker
"""


# --------------------------------
# Search Query
# --------------------------------

query = "Python FastAPI RAG Developer"

print("\nQUERY:")
print(query)


# --------------------------------
# Create Query Embedding
# --------------------------------

query_embedding = create_embeddings(
    [query]
)[0]


# --------------------------------
# Load Chunks
# --------------------------------

chunks = load_chunks()


# --------------------------------
# Search FAISS
# --------------------------------

results = search_embeddings(
    query_embedding,
    chunks,
    top_k=5
)


print("\nTOP MATCHING CHUNKS:\n")


for result in results:

    print("-------------------------")

    print(
        "Candidate ID:",
        result["candidate_id"]
    )

    print(
        "Resume:",
        result["resume_name"]
    )

    print(
        "Distance:",
        result["distance"]
    )

    print("Chunk:")
    print(result["chunk"])


# --------------------------------
# Get Unique Candidates
# --------------------------------

candidate_ids = []

for result in results:

    candidate_id = result["candidate_id"]

    if candidate_id not in candidate_ids:

        candidate_ids.append(candidate_id)


print("\nCANDIDATES FOUND BY FAISS:")

for candidate_id in candidate_ids:

    print(
        "-",
        candidate_id
    )


# --------------------------------
# Get Candidate Profiles
# --------------------------------

candidates = []

for candidate_id in candidate_ids:

    candidate = get_candidate(
        candidate_id
    )

    if candidate:

        candidate_copy = candidate.copy()

        candidate_copy["candidate_id"] = candidate_id

        candidates.append(
            candidate_copy
        )


# --------------------------------
# Rerank Candidates
# --------------------------------

required_skills = [
    "Python",
    "FastAPI",
    "RAG",
    "Docker"
]


reranked_candidates = rerank_candidates(
    candidates,
    required_skills
)


reranked_candidates.sort(
    key=lambda candidate: candidate["score"],
    reverse=True
)


print("\nRERANKED CANDIDATES:")

for position, candidate in enumerate(
    reranked_candidates,
    start=1
):

    print(
        position,
        candidate["name"],
        "-",
        candidate["score"],
        "matched skills"
    )


# --------------------------------
# Screen Candidates
# --------------------------------

screening_results = []


for candidate in reranked_candidates:

    result = check_candidate(
        candidate,
        job_description
    )

    result["candidate_id"] = candidate[
        "candidate_id"
    ]

    screening_results.append(
        result
    )


# --------------------------------
# Candidate Screening Results
# --------------------------------

print("\nCANDIDATE SCREENING RESULTS:")


for result in screening_results:

    print("\n-------------------------")

    print(
        "Candidate:",
        result["name"]
    )

    print(
        "Qualified:",
        result["qualified"]
    )

    print(
        "Recommendation:",
        result["recommendation"]
    )

    print(
        "Final Score:",
        result["final_score"],
        "%"
    )

    print("Must Have Results:")

    for skill_result in result[
        "must_have_results"
    ]:

        print(
            "-",
            skill_result["skill"],
            ":",
            skill_result["status"],
            "(Required:",
            skill_result["required"],
            "years, Candidate:",
            skill_result["candidate"],
            "years)"
        )

    print(
        "Matched Skills:",
        result["matched_skills"]
    )

    print("Reasons:")

    for reason in result["reasons"]:

        print(
            "-",
            reason
        )


# --------------------------------
# Final Candidate Ranking
# --------------------------------

final_ranking = rank_candidates(
    screening_results
)


print("\nFINAL CANDIDATE RANKING:")


for position, candidate in enumerate(
    final_ranking,
    start=1
):

    print("\n-------------------------")

    print(
        "Rank:",
        position
    )

    print(
        "Candidate:",
        candidate["name"]
    )

    print(
        "Qualified:",
        candidate["qualified"]
    )

    print(
        "Recommendation:",
        candidate["recommendation"]
    )

    print(
        "Final Score:",
        candidate["final_score"],
        "%"
    )