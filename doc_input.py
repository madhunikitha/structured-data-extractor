import os
import tempfile
import streamlit as st
from PIL import Image
from dotenv import load_dotenv

import pytesseract
import fitz  # PyMuPDF
import docx2txt



# ========== Configuration ==========
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Windows path
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    st.error("⚠️ OpenAI API key not found in environment.")
    st.stop()

# ========== Extraction Functions ==========
import mimetypes
def extract_text1(file_storage):
    filename = file_storage.filename
    file_type, _ = mimetypes.guess_type(filename)

    if not file_type:
        raise ValueError("Cannot determine file type")

    if file_type in ["image/jpeg", "image/png", "image/jpg"]:
        return extract_text_from_image(file_storage)
    
    elif file_type == "application/pdf":
        return extract_text_from_pdf(file_storage)
    elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return extract_text_from_docx(file_storage)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")

def extract_text_with_filename(file_path, filename):
    file_type, _ = mimetypes.guess_type(filename)
    file_type = file_type or "application/octet-stream"

    with open(file_path, "rb") as file:
        if file_type in ["image/jpeg", "image/png", "image/jpg"]:
            return {"text": extract_text_from_image(file)}
        elif file_type == "application/pdf":
            return {"text": extract_text_from_pdf(file)}
        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return {"text": extract_text_from_docx(file)}
        else:
            return {"error": f"Unsupported file type: {file_type}"}

import mimetypes
import os

def extract_text(file, filename=None):
    # Try getting file type from filename
    if filename is None and hasattr(file, "name"):
        filename = file.name  # e.g., 'document.pdf'

    file_type, _ = mimetypes.guess_type(filename or "")

    if not file_type:
        raise ValueError("Cannot determine file type: missing content_type and filename")

    if file_type in ["image/jpeg", "image/png", "image/jpg"]:
        return extract_text_from_image(file)
    elif file_type == "text/plain":
        return extract_text_from_txt(file)
    elif file_type == "application/pdf":
        return extract_text_from_pdf(file)
    elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return extract_text_from_docx(file)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")


def extract_text_from_image(file):
    try:
        image = Image.open(file).convert('RGB')
        return pytesseract.image_to_string(image)
    except Exception as e:
        return f"[Error extracting image text] {e}"

def extract_text_from_pdf(file):
    pdf_text = ""
    try:
        with fitz.open(stream=file.read(), filetype="pdf") as doc:
            for page in doc:
                text = page.get_text()
                if text.strip():
                    pdf_text += text
                else:
                    pix = page.get_pixmap(dpi=300)
                    image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    pdf_text += pytesseract.image_to_string(image)
    except Exception as e:
        return f"[Error extracting PDF text] {e}"
    return pdf_text

def extract_text_from_docx(file):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            tmp.write(file.read())
            tmp_path = tmp.name
        text = docx2txt.process(tmp_path)
        os.unlink(tmp_path)
        return text
    except Exception as e:
        return f"[Error extracting DOCX text] {e}"
def extract_text_from_txt(file):
    try:
        return file.read().decode("utf-8")  # or "latin-1" if encoding issue
    except Exception as e:
        return f"[Error extracting TXT text] {e}"





