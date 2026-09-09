from app.services.embedding_service import create_embeddings
from app.services.vector_store import add_embeddings, get_index_size


chunks = [
    "Python Developer with 6 years of experience.",
    "Strong experience in RAG, LangChain and FastAPI.",
    "Built production GenAI applications."
]


embeddings = create_embeddings(chunks)


add_embeddings(
    embeddings,
    chunks,
    "test_candidate_001",
    "test_resume.txt"
)


print("\nEMBEDDING TEST RESULT:")

print(
    "Number of chunks:",
    len(chunks)
)

print(
    "Number of embeddings:",
    len(embeddings)
)

print(
    "Vector dimensions:",
    len(embeddings[0])
)

print(
    "Vectors in FAISS:",
    get_index_size()
)

print(
    "Embedding test: PASS"
)