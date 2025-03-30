import pdfplumber

with pdfplumber.open("uploads/sample.pdf") as pdf:
    first_page = pdf.pages[0]
    print(first_page.extract_text())