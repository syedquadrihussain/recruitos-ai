import numpy as np

from app.services.embedding_service import create_embeddings
from app.services.chunker import create_chunks


def calculate_semantic_score(
    resume_text,
    job_description,
    chunk_size=500,
    chunk_overlap=50
):

    if not resume_text or not resume_text.strip():
        return {
            "semantic_score": 0.0,
            "matched_chunks": []
        }

    if not job_description or not job_description.strip():
        return {
            "semantic_score": 0.0,
            "matched_chunks": []
        }

    resume_chunks = create_chunks(
        resume_text,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

    if not resume_chunks:
        return {
            "semantic_score": 0.0,
            "matched_chunks": []
        }

    texts = [job_description] + resume_chunks

    embeddings = create_embeddings(texts)

    jd_embedding = embeddings[0]
    resume_embeddings = embeddings[1:]

    jd_norm = np.linalg.norm(jd_embedding)

    similarities = []

    for resume_embedding in resume_embeddings:

        resume_norm = np.linalg.norm(resume_embedding)

        if jd_norm == 0 or resume_norm == 0:
            similarity = 0.0
        else:
            similarity = np.dot(
                jd_embedding,
                resume_embedding
            ) / (
                jd_norm * resume_norm
            )

        similarities.append(float(similarity))

    best_indices = np.argsort(
        similarities
    )[::-1][:3]

    best_chunks = [
        {
            "chunk": resume_chunks[index],
            "similarity": round(
                similarities[index],
                4
            )
        }
        for index in best_indices
    ]

    best_similarity = similarities[best_indices[0]]

    semantic_score = max(
        0,
        min(
            100,
            ((best_similarity + 1) / 2) * 100
        )
    )

    return {
        "semantic_score": round(
            semantic_score,
            1
        ),
        "matched_chunks": best_chunks
    }