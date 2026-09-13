from app.services.vector_store import get_index_size


def test_vector_store():

    index_size = get_index_size()

    assert index_size is not None
    assert isinstance(index_size, int)
    assert index_size >= 0