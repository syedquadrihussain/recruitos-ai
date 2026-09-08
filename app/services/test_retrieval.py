from app.services.embedding_service import create_embeddings
from app.services.vector_store import search_embeddings, load_chunks


query = "US IT recruitment experience"

query_embedding = create_embeddings([query])[0]

chunks = load_chunks()

results = search_embeddings(query_embedding, chunks, top_k=2)


print("Query:", query)

print("\nTop matching chunks:")

for result in results:

    print("\nChunk:")
    print(result["chunk"])

    print("Distance:", result["distance"])