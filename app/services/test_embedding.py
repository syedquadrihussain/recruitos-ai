from app.services.embedding_service import create_embeddings
from app.services.vector_store import add_embeddings, get_index_size


def test_create_and_store_embeddings():

    chunks = [
        "Python Developer with 6 years of experience.",
        "Strong experience in RAG, LangChain and FastAPI.",
        "Built production GenAI applications."
    ]

    embeddings = create_embeddings(chunks)

    assert embeddings is not None
    assert len(embeddings) == len(chunks)
    assert len(embeddings) > 0
    assert len(embeddings[0]) > 0

    vector_dimensions = len(embeddings[0])

    assert all(
        len(embedding) == vector_dimensions
        for embedding in embeddings
    )

    initial_index_size = get_index_size()

    add_embeddings(
        embeddings,
        chunks,
        "candidate_001",
        "test_resume.txt"
    )

    final_index_size = get_index_size()

    assert final_index_size == (
        initial_index_size + len(chunks)
    )