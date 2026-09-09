from app.services.resume_parser import extract_text_from_pdf


file_path = "uploads/Syed Hussain BDM.pdf"


text = extract_text_from_pdf(
    file_path
)


print("\nRESUME PARSER TEST RESULT:")

print(
    "Extracted characters:",
    len(text)
)

print("\nFirst 1000 characters:\n")

print(text[:1000])


if text.strip():

    print("\nResume parser test: PASS")

else:

    print("\nResume parser test: FAIL")