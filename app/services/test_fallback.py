from app.services.candidate_store import get_candidate
from app.services.candidate_matcher import check_candidate
from app.services.candidate_ranker import rank_candidates


# --------------------------------
# Difficult Job Description
# --------------------------------

jd_text = """
We are looking for a Senior Python Developer.

Must Have:
Python - 10 years
FastAPI - 8 years

Nice to Have:
RAG
Docker
"""


# --------------------------------
# Candidates
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

    candidate = get_candidate(candidate_id)

    result = check_candidate(
        candidate,
        jd_text
    )

    screening_results.append(result)


# --------------------------------
# Rank Candidates
# --------------------------------

ranked_candidates = rank_candidates(
    screening_results
)


# --------------------------------
# Display Results
# --------------------------------

print("\n\nFINAL FALLBACK RESULTS:")

for rank, candidate in enumerate(
    ranked_candidates,
    start=1
):

    print("\n-------------------------")

    print("Rank:", rank)

    print("Candidate:", candidate["name"])

    print("Qualified:", candidate["qualified"])

    print("Match Score:", candidate["match_score"], "%")

    print(
    "Experience Closeness:",
    candidate["experience_closeness_score"],
    "%"
    )

    print("Matched Skills:", candidate["matched_skills"])

    print("Reasons:")

    for reason in candidate["reasons"]:

        print("-", reason)