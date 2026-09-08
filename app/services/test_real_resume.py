from app.services.resume_parser import extract_text_from_pdf
from app.services.candidate_extractor import extract_candidate
from app.services.candidate_matcher import check_candidate


resume_path = r"C:\RecruitOS-AI\uploads\Syed Hussain BDM.pdf"


# Step 1: Extract text from the PDF
resume_text = extract_text_from_pdf(resume_path)

print("\nRESUME TEXT:")
print(resume_text)


# Step 2: Extract candidate information
candidate = extract_candidate(resume_text)

print("\nEXTRACTED CANDIDATE:")
print(candidate)


# Step 3: Match candidate against the JD
result = check_candidate(candidate)

print("\nMATCH RESULT:")
print(result)


# Step 4: Display important results
print("\n-------------------------")
print("CANDIDATE:", result["name"])
print("QUALIFIED:", result["qualified"])
print("MATCH SCORE:", result["match_score"], "%")
print("MATCHED SKILLS:", result["matched_skills"])

print("\nREASONS:")

for reason in result["reasons"]:
    print("-", reason)