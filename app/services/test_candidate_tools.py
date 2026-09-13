from app.services.candidate_tools import score_candidate


job_description = """
Must Have:
Business Development Manager - 4 years
IT Recruitment
Client Relationship Management
Lead Generation
Contract Negotiation

Nice to Have:
ATS
VMS
SAP
"""


result = score_candidate(
    "Syed Hussain BDM",
    job_description
)

print(result)