from resume_parser import extract_text_from_pdf

file_path = r"C:\RecruitOS-AI\uploads\Syed Hussain BDM.pdf"

text = extract_text_from_pdf(file_path)

print(text)