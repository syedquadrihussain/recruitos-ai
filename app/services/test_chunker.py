from app.services.chunker import create_chunks

text = """
Python Developer with 6 years of experience.
Strong experience in RAG, LangChain and FastAPI.
Built production GenAI applications.
"""

chunks = create_chunks(text, 50)

for i, chunk in enumerate(chunks):
    print(f"\n--- Chunk {i + 1} ---")
    print(chunk)