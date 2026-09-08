from app.services.candidate_extractor import extract_candidate
from app.services.candidate_matcher import check_candidate


# --------------------------------
# Job Description
# --------------------------------

jd_text = """
We are looking for a Python Developer.

Must have:
Python - 5 years
FastAPI - 3 years

Nice to have:
RAG
Docker
"""


# --------------------------------
# Candidate Resume
# --------------------------------

resume_text = """
Name: Ahmed

Skills:
Python
FastAPI
RAG
Docker

Python: 6 years
FastAPI: 2 years
RAG: 2 years
Docker: 1 year
"""


# --------------------------------
# Step 1: Extract candidate
# --------------------------------

candidate = extract_candidate(resume_text)

print("\nEXTRACTED CANDIDATE:")
print(candidate)


# --------------------------------
# Step 2: Match candidate with JD
# --------------------------------

result = check_candidate(candidate, jd_text)


# --------------------------------
# Step 3: Display result
# --------------------------------

print("\nMATCH RESULT:")
print(result)

print("\n-------------------------")
print("CANDIDATE:", result["name"])
print("QUALIFIED:", result["qualified"])
print("MATCH SCORE:", result["match_score"], "%")
print("MATCHED SKILLS:", result["matched_skills"])

print("\nREASONS:")

for reason in result["reasons"]:
    print("-", reason)