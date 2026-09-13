from pathlib import Path

from app.services.resume_ingestion import process_resume
from app.services.vector_store import get_index_size


def test_resume_ingestion():

    file_path = "uploads/Syed Hussain BDM.pdf"

    assert Path(file_path).exists()

    initial_index_size = get_index_size()

    chunks = process_resume(
        file_path,
        "candidate_001",
        "Syed Hussain BDM.pdf"
    )

    assert chunks is not None
    assert isinstance(chunks, list)
    assert len(chunks) > 0

    for chunk in chunks:
        assert isinstance(chunk, str)
        assert chunk.strip() != ""

    final_index_size = get_index_size()

    assert final_index_size > initial_index_size
    assert final_index_size >= (
        initial_index_size + len(chunks)
    )