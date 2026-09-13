import numpy as np

from app.services.embedding_service import create_embeddings
from app.services.vector_store import search_embeddings, load_chunks


def test_retrieval():

    query = "US IT recruitment experience"

    # --------------------------------
    # Create Query Embedding
    # --------------------------------

    query_embedding = create_embeddings(
        [query]
    )[0]

    assert query_embedding is not None
    assert len(query_embedding) > 0

    # --------------------------------
    # Load Vector Store Chunks
    # --------------------------------

    chunks = load_chunks()

    assert chunks is not None
    assert isinstance(chunks, list)
    assert len(chunks) > 0

    # --------------------------------
    # Search Vector Store
    # --------------------------------

    results = search_embeddings(
        query_embedding,
        chunks,
        top_k=2
    )

    # --------------------------------
    # Validate Retrieval Results
    # --------------------------------

    assert results is not None
    assert isinstance(results, list)
    assert len(results) > 0
    assert len(results) <= 2

    for result in results:

        assert isinstance(result, dict)

        assert "index" in result
        assert "candidate_id" in result
        assert "resume_name" in result
        assert "chunk" in result
        assert "distance" in result

        assert isinstance(
            result["candidate_id"],
            str
        )

        assert isinstance(
            result["resume_name"],
            str
        )

        assert isinstance(
            result["chunk"],
            str
        )

        assert result["chunk"].strip() != ""

        assert isinstance(
            result["distance"],
            (int, float, np.floating)
        )