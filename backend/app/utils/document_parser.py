import pdfplumber
import docx

def extract_text(file_path: str) -> str:
    if file_path.lower().endswith('.pdf'):
        return _extract_text_from_pdf(file_path)
    elif file_path.lower().endswith('.docx'):
        return _extract_text_from_docx(file_path)
    elif file_path.lower().endswith('.txt'):
        return _extract_text_from_txt(file_path)
    else:
        return ""

def _extract_text_from_pdf(file_path: str) -> str:
    extracted_text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n"
        return extracted_text
    except Exception as e:
        print(f"PDF Parsing Error in {file_path}: {e}")
        return ""

def _extract_text_from_docx(file_path: str) -> str:
    try:
        doc = docx.Document(file_path)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])
    except Exception as e:
        print(f"DOCX Parsing Error in {file_path}: {e}")
        return ""

def _extract_text_from_txt(file_path: str) -> str:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"TXT Parsing Error in {file_path}: {e}")
        return ""   