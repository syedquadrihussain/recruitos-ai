from app.services.resume_ingestion import process_resume
from app.services.vector_store import get_index_size


file_path = "uploads/Syed Hussain BDM.pdf"


chunks = process_resume(
    file_path,
    "test_candidate_001",
    "Syed Hussain BDM.pdf"
)


print("\nRESUME INGESTION TEST RESULT:")

print(
    "Number of chunks:",
    len(chunks)
)

print("\nFirst chunk:")

print(chunks[0])

print(
    "\nVectors in FAISS:",
    get_index_size()
)

print(
    "\nResume ingestion test: PASS"
)