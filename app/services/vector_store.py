import json
from pathlib import Path

import faiss
import numpy as np


INDEX_PATH = Path("faiss_index.bin")
CHUNKS_PATH = Path("chunks.json")

EMBEDDING_DIMENSION = 384


def _create_empty_index():
    return faiss.IndexFlatL2(EMBEDDING_DIMENSION)


def _persist_store():
    """Persist the FAISS index and its aligned chunk metadata."""
    faiss.write_index(index, str(INDEX_PATH))

    with open(CHUNKS_PATH, "w", encoding="utf-8") as file:
        json.dump(
            chunks_store,
            file,
            ensure_ascii=False,
            indent=2,
        )


def add_embeddings(
    embeddings,
    chunks,
    candidate_id,
    resume_name,
    resume_id=None,
    version=1,
):
    """Add resume chunks while preserving vector/metadata alignment."""
    if embeddings is None or len(embeddings) == 0:
        return

    if len(embeddings) != len(chunks):
        raise ValueError(
            "Number of embeddings must match number of chunks"
        )

    if not isinstance(version, int) or version < 1:
        raise ValueError("version must be a positive integer")

    vectors = np.asarray(embeddings, dtype="float32")

    if vectors.ndim != 2:
        raise ValueError(
            "Embeddings must be a 2-dimensional array"
        )

    if vectors.shape[1] != EMBEDDING_DIMENSION:
        raise ValueError(
            f"Expected embedding dimension {EMBEDDING_DIMENSION}, "
            f"received {vectors.shape[1]}"
        )

    if not np.isfinite(vectors).all():
        raise ValueError("Embeddings must contain only finite values")

    # Add one vector for each chunk, in the same order.
    index.add(vectors)

    for chunk in chunks:
        chunks_store.append(
            {
                "candidate_id": candidate_id,
                "resume_name": resume_name,
                "chunk": chunk,
                "resume_id": resume_id,
                "version": version,
                "is_active": True,
            }
        )

    _persist_store()


def update_resume_embeddings(
    resume_id,
    embeddings,
    chunks,
    candidate_id,
    resume_name,
):
    """
    Add a new resume version, then deactivate its previous versions.

    Existing versions remain in FAISS so vector indices continue to
    match the corresponding records in chunks.json.
    """
    if not resume_id:
        raise ValueError("resume_id is required")

    if embeddings is None or len(embeddings) == 0:
        raise ValueError("Updated resume must contain embeddings")

    if len(embeddings) != len(chunks):
        raise ValueError(
            "Number of embeddings must match number of chunks"
        )

    existing_records = [
        record
        for record in chunks_store
        if record.get("resume_id") == resume_id
    ]

    if not existing_records:
        raise ValueError(f"Resume not found: {resume_id}")

    next_version = max(
        record.get("version", 1)
        for record in existing_records
    ) + 1

    # Append the new version first.
    add_embeddings(
        embeddings=embeddings,
        chunks=chunks,
        candidate_id=candidate_id,
        resume_name=resume_name,
        resume_id=resume_id,
        version=next_version,
    )

    # Only deactivate earlier versions of this resume.
    for record in chunks_store:
        if (
            record.get("resume_id") == resume_id
            and record.get("version", 1) < next_version
        ):
            record["is_active"] = False

    _persist_store()

    return next_version


def soft_delete_resume(resume_id):
    """Deactivate all stored versions of a resume without removing vectors."""
    if not resume_id:
        raise ValueError("resume_id is required")

    found = False

    for record in chunks_store:
        if record.get("resume_id") == resume_id:
            record["is_active"] = False
            found = True

    if found:
        _persist_store()

    return found


def get_index_size():
    return index.ntotal


def load_index():
    if not INDEX_PATH.exists():
        return _create_empty_index()

    return faiss.read_index(str(INDEX_PATH))


def load_chunks():
    if not CHUNKS_PATH.exists():
        return []

    with open(CHUNKS_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def search_embeddings(
    query_embedding,
    chunks,
    top_k=2,
):
    """
    Search all stored vectors, filter inactive resume versions,
    and return up to top_k active results.

    Legacy records without is_active are treated as active.
    """
    if not chunks or top_k <= 0:
        return []

    loaded_index = load_index()

    if loaded_index.ntotal == 0:
        return []

    if loaded_index.ntotal != len(chunks):
        raise RuntimeError(
            "Vector store inconsistency: "
            f"{loaded_index.ntotal} vectors but "
            f"{len(chunks)} chunk records."
        )

    query_vector = np.asarray(
        [query_embedding],
        dtype="float32",
    )

    if query_vector.ndim != 2:
        raise ValueError(
            "Query embedding must be a 1-dimensional vector"
        )

    if query_vector.shape[1] != EMBEDDING_DIMENSION:
        raise ValueError(
            f"Expected query embedding dimension "
            f"{EMBEDDING_DIMENSION}, "
            f"received {query_vector.shape[1]}"
        )

    if not np.isfinite(query_vector).all():
        raise ValueError(
            "Query embedding must contain only finite values"
        )

    # Search all vectors because inactive records may rank first.
    distances, indices = loaded_index.search(
        query_vector,
        loaded_index.ntotal,
    )

    results = []

    for distance, index_number in zip(
        distances[0],
        indices[0],
    ):
        if index_number < 0:
            continue

        chunk = chunks[index_number]

        # Backward compatibility: old records have no is_active field.
        if chunk.get("is_active", True) is False:
            continue

        results.append(
            {
                "index": int(index_number),
                "candidate_id": chunk["candidate_id"],
                "resume_name": chunk["resume_name"],
                "chunk": chunk["chunk"],
                "distance": float(distance),
            }
        )

        if len(results) >= top_k:
            break

    return results


# Load persisted data after all functions are defined.
index = load_index()
chunks_store = load_chunks()

# Verify saved vectors and chunk metadata remain aligned.
if index.ntotal != len(chunks_store):
    raise RuntimeError(
        "Vector store inconsistency: "
        f"{index.ntotal} vectors but "
        f"{len(chunks_store)} chunk records. "
        "Existing data has not been modified."
    )