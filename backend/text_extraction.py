import docx
import PyPDF2

def extract_text(file_path: str) -> str:
    """
    Extracts text from PDF, DOCX, or TXT.
    """

    text = ""

    # PDF
    if file_path.lower().endswith(".pdf"):
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + "\n"

    # DOCX
    elif file_path.lower().endswith(".docx"):
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"

    # TXT
    elif file_path.lower().endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

    return text.strip()
