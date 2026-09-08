from app.services.resume_parser import extract_text_from_pdf
from app.services.chunker import create_chunks
from app.services.embedding_service import create_embeddings
from app.services.vector_store import add_embeddings


def process_resume(file_path, candidate_id, resume_name):

    text = extract_text_from_pdf(file_path)

    chunks = create_chunks(text)

    embeddings = create_embeddings(chunks)

    add_embeddings(
        embeddings,
        chunks,
        candidate_id,
        resume_name
    )

    return chunks