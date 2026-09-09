from app.services.resume_parser import extract_text_from_pdf
from app.services.candidate_extractor import extract_candidate
from app.services.candidate_matcher import check_candidate


resume_path = "uploads/Syed Hussain BDM.pdf"


jd_text = """
Python Developer

Must Have:

Python - 5 years
FastAPI - 3 years
RAG - 2 years

Nice to Have:

Docker
AWS
"""


# Step 1: Extract text from the PDF

resume_text = extract_text_from_pdf(
    resume_path
)

print("\nRESUME TEXT:")

print(resume_text)


# Step 2: Extract candidate information

candidate = extract_candidate(
    resume_text
)

print("\nEXTRACTED CANDIDATE:")

print(candidate)


# Step 3: Match candidate against the JD

result = check_candidate(
    candidate,
    jd_text,
    resume_text
)


# Step 4: Display important results

print("\nREAL RESUME SCREENING RESULT:")

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
    "FINAL SCORE:",
    result["final_score"],
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

print("\nREAL RESUME TEST: PASS")