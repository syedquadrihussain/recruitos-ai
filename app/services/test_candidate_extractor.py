from app.services.candidate_extractor import extract_candidate


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


candidate = extract_candidate(resume_text)


print(candidate)