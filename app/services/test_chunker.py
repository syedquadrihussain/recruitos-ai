from app.services.chunker import create_chunks


def test_create_chunks():

    text = """
    Python Developer with 6 years of experience.

    Strong experience in RAG, LangChain and FastAPI.

    Built production GenAI applications.
    """

    chunks = create_chunks(text, 50)

    assert chunks is not None

    assert isinstance(chunks, list)

    assert len(chunks) > 0

    for chunk in chunks:

        assert isinstance(chunk, str)

        assert chunk.strip() != ""

        assert len(chunk) <= 50