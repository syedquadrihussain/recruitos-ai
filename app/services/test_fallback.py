from app.services.candidate_store import get_candidate
from app.services.candidate_matcher import check_candidate
from app.services.candidate_ranker import rank_candidates


# --------------------------------
# Job Description
# --------------------------------

job_description = """
Python Developer

Must Have:

Python 10 years
FastAPI 8 years

Nice to Have:

RAG
Docker
"""


# --------------------------------
# Candidate IDs
# --------------------------------

candidate_ids = [
    "candidate_001",
    "candidate_002",
    "candidate_003"
]


# --------------------------------
# Screen Candidates
# --------------------------------

screening_results = []


for candidate_id in candidate_ids:

    candidate = get_candidate(
        candidate_id
    )

    if candidate:

        result = check_candidate(
            candidate,
            job_description
        )

        result["candidate_id"] = candidate_id

        screening_results.append(
            result
        )


# --------------------------------
# Rank Candidates
# --------------------------------

final_results = rank_candidates(
    screening_results
)


# --------------------------------
# Display Results
# --------------------------------

print("\nFINAL FALLBACK RESULTS:")


for position, candidate in enumerate(
    final_results,
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
        "Final Score:",
        candidate["final_score"],
        "%"
    )

    print(
        "Experience Closeness:",
        candidate["experience_closeness_score"],
        "%"
    )

    print(
        "Matched Skills:",
        candidate["matched_skills"]
    )

    print("Reasons:")

    for reason in candidate["reasons"]:

        print(
            "-",
            reason
        )