import faiss
import numpy as np
import json


INDEX_PATH = "faiss_index.bin"
CHUNKS_PATH = "chunks.json"


index = faiss.IndexFlatL2(384)

chunks_store = []


def add_embeddings(embeddings, chunks, candidate_id, resume_name):

    vectors = np.array(embeddings).astype("float32")

    index.add(vectors)

    for chunk in chunks:

        chunks_store.append({
            "candidate_id": candidate_id,
            "resume_name": resume_name,
            "chunk": chunk
        })

    faiss.write_index(index, INDEX_PATH)

    with open(CHUNKS_PATH, "w", encoding="utf-8") as file:

        json.dump(
            chunks_store,
            file,
            ensure_ascii=False,
            indent=2
        )


def get_index_size():

    return index.ntotal


def load_index():

    return faiss.read_index(INDEX_PATH)


def load_chunks():

    with open(CHUNKS_PATH, "r", encoding="utf-8") as file:

        return json.load(file)


def search_embeddings(query_embedding, chunks, top_k=2):

    query_vector = np.array(
        [query_embedding]
    ).astype("float32")

    loaded_index = load_index()

    distances, indices = loaded_index.search(
        query_vector,
        top_k
    )

    results = []

    for distance, index_number in zip(
        distances[0],
        indices[0]
    ):

        chunk = chunks[index_number]

        results.append({
            "index": index_number,
            "candidate_id": chunk["candidate_id"],
            "resume_name": chunk["resume_name"],
            "chunk": chunk["chunk"],
            "distance": distance
        })

    return results