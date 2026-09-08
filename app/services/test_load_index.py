from app.services.vector_store import load_index


index = load_index()

print("Vectors loaded from FAISS:", index.ntotal)