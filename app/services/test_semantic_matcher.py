from app.services.semantic_matcher import calculate_semantic_score


resume_text = """
Ahmed is a Python Developer with 6 years of experience.

He has 3 years of FastAPI experience and 2 years
of RAG experience.

He has built Generative AI applications using Python,
FastAPI and retrieval augmented generation.
"""


job_description = """
Looking for a Python Developer with experience
building Generative AI and RAG applications.

Strong FastAPI experience is required.
"""


result = calculate_semantic_score(
    resume_text,
    job_description
)


print("\nSEMANTIC MATCH RESULT:\n")

print(
    "Semantic Score:",
    result["semantic_score"]
)

print("\nTOP MATCHING RESUME CHUNKS:\n")

for match in result["matched_chunks"]:

    print(
        "Similarity:",
        match["similarity"]
    )

    print(
        "Chunk:",
        match["chunk"]
    )

    print("-" * 60)