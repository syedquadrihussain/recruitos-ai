from pathlib import Path

from app.services.resume_parser import extract_text_from_pdf
from app.services.chunker import create_chunks
from app.services.embedding_service import create_embeddings
from app.services.vector_store import (
    add_embeddings,
    load_chunks,
    update_resume_embeddings,
)


def process_resume(
    file_path,
    candidate_id,
    resume_name,
    resume_id=None,
):
    """
    Process a PDF resume and store its chunks and embeddings.

    Backward compatible:
        process_resume(file_path, candidate_id, resume_name)

    Version-aware:
        process_resume(
            file_path,
            candidate_id,
            resume_name,
            resume_id="resume-001",
        )

    If resume_id already exists, create a new version.
    Otherwise, create the first version.
    """

    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(
            f"Resume file not found: {path}"
        )

    text = extract_text_from_pdf(str(path))

    if not text or not text.strip():
        raise ValueError(
            "The resume contains no extractable text."
        )

    chunks = create_chunks(text)

    if not chunks:
        raise ValueError(
            "No chunks were generated from the resume."
        )

    embeddings = create_embeddings(chunks)

    if embeddings is None or len(embeddings) != len(chunks):
        raise ValueError(
            "Embedding generation failed or returned "
            "a different number of embeddings than chunks."
        )

    if resume_id is None:
        # Preserve the existing behavior for callers that
        # do not supply a resume ID.
        add_embeddings(
            embeddings,
            chunks,
            candidate_id,
            resume_name,
        )
    else:
        existing_resume = any(
            record.get("resume_id") == resume_id
            for record in load_chunks()
        )

        if existing_resume:
            update_resume_embeddings(
                resume_id=resume_id,
                embeddings=embeddings,
                chunks=chunks,
                candidate_id=candidate_id,
                resume_name=resume_name,
            )
        else:
            add_embeddings(
                embeddings,
                chunks,
                candidate_id,
                resume_name,
                resume_id=resume_id,
                version=1,
            )

    return chunks