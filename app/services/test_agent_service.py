from app.services.agent_service import run_agent


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


request = f"""
Find candidates suitable for this job.

Job Description:

{job_description}
"""


result = run_agent(request)


print("\nFinal Answer:")
print(result)