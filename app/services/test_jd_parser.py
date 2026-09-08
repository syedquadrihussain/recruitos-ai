from app.services.jd_parser import parse_jd


jd_text = """
We are looking for a Python Developer.

Must Have:
Python - 5 years
FastAPI - 3 years

Nice to Have:
RAG
Docker
"""


result = parse_jd(jd_text)

print("\nPARSED JD:")
print(result)

print("\nMUST HAVE:")
print(result["must_have"])

print("\nNICE TO HAVE:")
print(result["nice_to_have"])

print("\nSKILL WEIGHTS:")
print(result["skill_weights"])