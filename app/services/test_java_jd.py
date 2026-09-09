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
# Java Job Description
# --------------------------------

jd_text = """
Java Developer

Must Have:

Java 5 years
SAP 3 years

Nice to Have:

Docker
"""


# --------------------------------
# Extract Candidate
# --------------------------------

candidate = extract_candidate(
    resume_text
)


print("\nEXTRACTED CANDIDATE:")

print(candidate)


# --------------------------------
# Match Candidate
# --------------------------------

result = check_candidate(
    candidate,
    jd_text,
    resume_text
)


print("\nMATCH RESULT:")

print(result)


# --------------------------------
# Important Results
# --------------------------------

print("\n-------------------------")

print(
    "CANDIDATE:",
    result["name"]
)

print(
    "QUALIFIED:",
    result["qualified"]
)

print(
    "RECOMMENDATION:",
    result["recommendation"]
)

print(
    "FINAL SCORE:",
    result["final_score"],
    "%"
)

print(
    "RULE-BASED SCORE:",
    result["rule_based_score"],
    "%"
)

print(
    "SEMANTIC SCORE:",
    result["semantic_score"],
    "%"
)

print(
    "EXPERIENCE CLOSENESS:",
    result["experience_closeness_score"],
    "%"
)

print(
    "MATCHED SKILLS:",
    result["matched_skills"]
)

print("\nREASONS:")

for reason in result["reasons"]:

    print(
        "-",
        reason
    )