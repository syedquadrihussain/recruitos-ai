from pathlib import Path

from app.services.resume_parser import extract_text_from_pdf


def test_resume_parser():

    file_path = "uploads/Syed Hussain BDM.pdf"

    # --------------------------------
    # Verify Resume Exists
    # --------------------------------

    assert Path(file_path).exists()

    # --------------------------------
    # Extract Resume Text
    # --------------------------------

    text = extract_text_from_pdf(
        file_path
    )

    # --------------------------------
    # Validate Extracted Text
    # --------------------------------

    assert text is not None
    assert isinstance(text, str)
    assert text.strip() != ""

    # --------------------------------
    # Validate Extracted Content
    # --------------------------------

    assert len(text) > 100

    assert "Summary" in text
    assert "Professional Experience" in text
    assert "Education" in text