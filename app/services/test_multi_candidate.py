from app.services.embedding_service import create_embeddings
from app.services.vector_store import (
    add_embeddings,
    search_embeddings,
    load_chunks
)
from app.services.reranker import rerank_candidates
from app.services.candidate_ranker import rank_candidates
from app.services.candidate_store import get_candidate
from app.services.candidate_matcher import check_candidate


# --------------------------------
# Job Description
# --------------------------------

jd_text = """
We are looking for a Python Developer.

Must Have:
Python - 5 years
FastAPI - 3 years

Nice to Have:
RAG
Docker
"""


# --------------------------------
# Candidate 1
# --------------------------------

candidate_1_chunks = [
    "Ahmed is a Python Developer with 6 years of Python experience.",
    "Ahmed has 3 years of FastAPI experience and 2 years of RAG experience.",
    "Ahmed has experience with Docker."
]


# --------------------------------
# Candidate 2
# --------------------------------

candidate_2_chunks = [
    "John is a Java Developer with 7 years of Java experience.",
    "John has 5 years of Spring Boot experience and 3 years of AWS.",
    "John has experience with Docker."
]


# --------------------------------
# Candidate 3
# --------------------------------

candidate_3_chunks = [
    "Sara is a Python Developer with 4 years of Python experience.",
    "Sara has 4 years of Django experience and 5 years of SQL.",
    "Sara has experience with AWS."
]


# --------------------------------
# Create embeddings
# --------------------------------

embeddings_1 = create_embeddings(candidate_1_chunks)

embeddings_2 = create_embeddings(candidate_2_chunks)

embeddings_3 = create_embeddings(candidate_3_chunks)


# --------------------------------
# Store candidates in FAISS
# --------------------------------

add_embeddings(
    embeddings_1,
    candidate_1_chunks,
    "candidate_001",
    "Ahmed.pdf"
)

add_embeddings(
    embeddings_2,
    candidate_2_chunks,
    "candidate_002",
    "John.pdf"
)

add_embeddings(
    embeddings_3,
    candidate_3_chunks,
    "candidate_003",
    "Sara.pdf"
)


# --------------------------------
# Search Query
# --------------------------------

query = "Python FastAPI RAG Developer"

query_embedding = create_embeddings(
    [query]
)[0]


# --------------------------------
# Load stored chunks
# --------------------------------

chunks = load_chunks()


# --------------------------------
# FAISS Search
# --------------------------------

results = search_embeddings(
    query_embedding,
    chunks,
    top_k=5
)


# --------------------------------
# Display FAISS Results
# --------------------------------

print("\nQUERY:")
print(query)

print("\nTOP MATCHING CHUNKS:")

for result in results:

    print("\n-------------------------")

    print("Candidate ID:", result["candidate_id"])

    print("Resume:", result["resume_name"])

    print("Distance:", result["distance"])

    print("Chunk:")
    print(result["chunk"])


# --------------------------------
# Get Unique Candidate IDs
# --------------------------------

candidate_ids = []

for result in results:

    candidate_id = result["candidate_id"]

    if candidate_id not in candidate_ids:

        candidate_ids.append(candidate_id)


print("\n\nCANDIDATES FOUND BY FAISS:")

for candidate_id in candidate_ids:

    print("-", candidate_id)


# --------------------------------
# Get Candidate Profiles
# --------------------------------

candidates = []

for candidate_id in candidate_ids:

    candidate = get_candidate(candidate_id)

    candidates.append(candidate)


# --------------------------------
# Reranking
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

# Sort by reranker score

reranked_candidates.sort(
    key=lambda candidate: candidate["score"],
    reverse=True
)


print("\n\nRERANKED CANDIDATES:")

for rank, candidate in enumerate(
    reranked_candidates,
    start=1
):

    print(
        rank,
        candidate["name"],
        "-",
        candidate["score"],
        "matched skills"
    )


# --------------------------------
# Candidate Screening
# --------------------------------

print("\n\nCANDIDATE SCREENING RESULTS:")

screening_results = []


for candidate in reranked_candidates:

    result = check_candidate(
        candidate,
        jd_text
    )

    screening_results.append(result)

    print("\n-------------------------")

    print("Candidate:", result["name"])

    print("Qualified:", result["qualified"])

    print("Recommendation:", result["recommendation"])

    print("Match Score:", result["match_score"], "%")

    print("Must Have Results:")

    for must_have in result["must_have_results"]:

        print(
            f"- {must_have['skill']}: "
            f"{must_have['status']} "
            f"(Required: {must_have['required']} years, "
            f"Candidate: {must_have['candidate']} years)"
        )

    print("Matched Skills:", result["matched_skills"])

    print("Reasons:")

    for reason in result["reasons"]:

        print("-", reason)


# --------------------------------
# Final Candidate Ranking
# --------------------------------

ranked_candidates = rank_candidates(
    screening_results
)


print("\n\nFINAL CANDIDATE RANKING:")

for rank, candidate in enumerate(
    ranked_candidates,
    start=1
):

    print("\n-------------------------")

    print("Rank:", rank)

    print("Candidate:", candidate["name"])

    print("Qualified:", candidate["qualified"])

    print("Recommendation:", candidate["recommendation"])

    print("Match Score:", candidate["match_score"], "%")

    print(
        "Experience Closeness:",
        candidate["experience_closeness_score"],
        "%"
    )

    print("Matched Skills:", candidate["matched_skills"])

    print("Must Have Results:")

    for must_have in candidate["must_have_results"]:

        print(
            f"- {must_have['skill']}: "
            f"{must_have['status']} "
            f"(Required: {must_have['required']} years, "
            f"Candidate: {must_have['candidate']} years)"
        )

    print("Reasons:")

    for reason in candidate["reasons"]:

        print("-", reason)