import numpy as np
import pytest

from app.services import vector_store


@pytest.fixture
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setattr(
        vector_store,
        "INDEX_PATH",
        tmp_path / "faiss_index.bin",
    )
    monkeypatch.setattr(
        vector_store,
        "CHUNKS_PATH",
        tmp_path / "chunks.json",
    )
    monkeypatch.setattr(
        vector_store,
        "index",
        vector_store._create_empty_index(),
    )
    monkeypatch.setattr(
        vector_store,
        "chunks_store",
        [],
    )

    return vector_store


def embedding(value):
    vector = np.zeros(384, dtype="float32")
    vector[0] = value
    return vector


def test_vector_store():
    index_size = vector_store.get_index_size()

    assert index_size is not None
    assert isinstance(index_size, int)
    assert index_size >= 0


def test_resume_update_creates_new_version_and_deactivates_old(
    isolated_store,
):
    store = isolated_store

    store.add_embeddings(
        [embedding(1.0)],
        ["Original resume content"],
        "candidate_001",
        "resume.pdf",
        resume_id="resume-001",
        version=1,
    )

    store.update_resume_embeddings(
        resume_id="resume-001",
        embeddings=[embedding(0.9)],
        chunks=["Updated resume content"],
        candidate_id="candidate_001",
        resume_name="resume.pdf",
    )

    records = store.load_chunks()

    assert len(records) == 2
    assert records[0]["version"] == 1
    assert records[0]["is_active"] is False
    assert records[1]["version"] == 2
    assert records[1]["is_active"] is True


def test_soft_delete_excludes_resume_from_search(isolated_store):
    store = isolated_store

    store.add_embeddings(
        [embedding(1.0)],
        ["Resume content"],
        "candidate_001",
        "resume.pdf",
        resume_id="resume-001",
        version=1,
    )

    store.soft_delete_resume("resume-001")

    results = store.search_embeddings(
        embedding(1.0),
        store.load_chunks(),
        top_k=5,
    )

    assert results == []


def test_search_does_not_return_superseded_resume_version(
    isolated_store,
):
    store = isolated_store

    store.add_embeddings(
        [embedding(1.0)],
        ["Old resume content"],
        "candidate_001",
        "resume.pdf",
        resume_id="resume-001",
        version=1,
    )

    store.update_resume_embeddings(
        resume_id="resume-001",
        embeddings=[embedding(0.9)],
        chunks=["New resume content"],
        candidate_id="candidate_001",
        resume_name="resume.pdf",
    )

    results = store.search_embeddings(
        embedding(1.0),
        store.load_chunks(),
        top_k=5,
    )

    assert results
    assert all(
        result["chunk"] != "Old resume content"
        for result in results
    )
    assert any(
        result["chunk"] == "New resume content"
        for result in results
    )