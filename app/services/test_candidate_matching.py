from app.services.candidate_extractor import extract_candidate
from app.services.candidate_matcher import check_candidate


# --------------------------------
# Sample Resume
# --------------------------------

resume_text = """
Python Developer with 6 years of Python experience.

FastAPI 2 years.

RAG 2 years.

Docker 1 year.

Built Generative AI applications using Python,
FastAPI and Retrieval Augmented Generation.
"""


# --------------------------------
# Job Description
# --------------------------------

jd_text = """
Python Developer

Must Have:

Python 5 years
FastAPI 3 years
RAG 2 years

Nice to Have:

Docker
"""


# --------------------------------
# Extract Candidate
# --------------------------------

candidate = extract_candidate(
    resume_text
)


print("\nEXTRACTED CANDIDATE:\n")

print(candidate)


# --------------------------------
# Match Candidate
# --------------------------------

result = check_candidate(
    candidate,
    jd_text,
    resume_text
)


print("\nMATCH RESULT:\n")

print(result)


# --------------------------------
# Important Scores
# --------------------------------

print("\nSCORES:\n")

print(
    "Rule-Based Score:",
    result["rule_based_score"]
)

print(
    "Semantic Score:",
    result["semantic_score"]
)

print(
    "Final Score:",
    result["final_score"]
)

print(
    "Recommendation:",
    result["recommendation"]
)