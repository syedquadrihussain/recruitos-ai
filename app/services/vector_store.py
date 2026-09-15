import json
from pathlib import Path

import faiss
import numpy as np


INDEX_PATH = Path("faiss_index.bin")
CHUNKS_PATH = Path("chunks.json")

EMBEDDING_DIMENSION = 384


def _create_empty_index():
    return faiss.IndexFlatL2(
        EMBEDDING_DIMENSION
    )


index = _create_empty_index()
chunks_store = []


def add_embeddings(
    embeddings,
    chunks,
    candidate_id,
    resume_name
):

    if embeddings is None or len(embeddings) == 0:
        return

    if len(embeddings) != len(chunks):
        raise ValueError(
            "Number of embeddings must match number of chunks"
        )

    vectors = np.array(
        embeddings,
        dtype="float32"
    )

    if vectors.ndim != 2:
        raise ValueError(
            "Embeddings must be a 2-dimensional array"
        )

    if vectors.shape[1] != EMBEDDING_DIMENSION:
        raise ValueError(
            f"Expected embedding dimension "
            f"{EMBEDDING_DIMENSION}, "
            f"received {vectors.shape[1]}"
        )

    index.add(vectors)

    for chunk in chunks:
        chunks_store.append(
            {
                "candidate_id": candidate_id,
                "resume_name": resume_name,
                "chunk": chunk
            }
        )

    faiss.write_index(
        index,
        str(INDEX_PATH)
    )

    with open(
        CHUNKS_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            chunks_store,
            file,
            ensure_ascii=False,
            indent=2
        )


def get_index_size():
    return index.ntotal


def load_index():

    if not INDEX_PATH.exists():
        return _create_empty_index()

    return faiss.read_index(
        str(INDEX_PATH)
    )


def load_chunks():

    if not CHUNKS_PATH.exists():
        return []

    with open(
        CHUNKS_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def search_embeddings(
    query_embedding,
    chunks,
    top_k=2
):

    if not chunks:
        return []

    loaded_index = load_index()

    if loaded_index.ntotal == 0:
        return []

    query_vector = np.array(
        [query_embedding],
        dtype="float32"
    )

    if query_vector.shape[1] != EMBEDDING_DIMENSION:
        raise ValueError(
            f"Expected query embedding dimension "
            f"{EMBEDDING_DIMENSION}, "
            f"received {query_vector.shape[1]}"
        )

    safe_top_k = min(
        top_k,
        loaded_index.ntotal,
        len(chunks)
    )

    if safe_top_k <= 0:
        return []

    distances, indices = loaded_index.search(
        query_vector,
        safe_top_k
    )

    results = []

    for distance, index_number in zip(
        distances[0],
        indices[0]
    ):

        if index_number < 0:
            continue

        chunk = chunks[index_number]

        results.append(
            {
                "index": int(index_number),
                "candidate_id": chunk["candidate_id"],
                "resume_name": chunk["resume_name"],
                "chunk": chunk["chunk"],
                "distance": float(distance)
            }
        )

    return results