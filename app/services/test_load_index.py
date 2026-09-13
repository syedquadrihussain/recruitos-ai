from app.services.vector_store import load_index


def test_load_index():

    index = load_index()

    assert index is not None

    assert hasattr(
        index,
        "ntotal"
    )

    assert isinstance(
        index.ntotal,
        int
    )

    assert index.ntotal >= 0