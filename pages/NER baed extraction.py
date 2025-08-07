import streamlit as st
import pandas as pd
import re
import tempfile
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import docx2txt
import os
import spacy

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# ---------------- PREDEFINED FIELD TO ENTITY MAP ----------------
PREDEFINED_FIELD_ENTITY_MAP = {
    "name": ["PERSON"],
    "organization": ["ORG"],
    "location": ["GPE", "LOC"],
    "date": ["DATE"],
    "time": ["TIME"],
    "money": ["MONEY"],
    "percent": ["PERCENT"],
    "product": ["PRODUCT"],
    "language": ["LANGUAGE"],
    "event": ["EVENT"],
    "nationality": ["NORP"]
}

# ---------------- FILE EXTRACTORS ----------------
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
        return file.read().decode("utf-8")
    except Exception as e:
        return f"[Error extracting TXT text] {e}"

# ---------------- FIELD-BASED NER EXTRACTION ----------------
def extract_with_custom_fields(text, fields):
    doc = nlp(text)
    results = {field: [] for field in fields}

    for ent in doc.ents:
        for field in fields:
            entity_labels = PREDEFINED_FIELD_ENTITY_MAP.get(field.lower(), [])
            if ent.label_ in entity_labels:
                results[field].append(ent.text)

    results = {k: list(set(v)) for k, v in results.items()}
    return results

# ---------------- UI START ----------------
st.set_page_config(page_title="NER Extractor | Predefined Mapping")
st.title("🧠 Structured NER Extractor (Offline, Predefined Field Mapping)")

uploaded_file = st.file_uploader("📄 Upload your document (PDF, DOCX, TXT, Image)", type=["pdf", "docx", "txt", "png", "jpg", "jpeg"])

if uploaded_file:
    file_type = uploaded_file.name.split('.')[-1].lower()
    if file_type == "pdf":
        extracted_text = extract_text_from_pdf(uploaded_file)
    elif file_type == "docx":
        extracted_text = extract_text_from_docx(uploaded_file)
    elif file_type == "txt":
        extracted_text = extract_text_from_txt(uploaded_file)
    elif file_type in ["png", "jpg", "jpeg"]:
        extracted_text = extract_text_from_image(uploaded_file)
    else:
        st.error("Unsupported file type.")
        extracted_text = ""

    if extracted_text and "Error" not in extracted_text:
        st.success("✅ Text extracted successfully!")
        st.text_area("📜 Extracted Text", extracted_text[:2000] + ("..." if len(extracted_text) > 2000 else ""), height=300)

        st.subheader("🔍 Choose Fields to Extract")
        default_fields = "name, organization, location, date"
        field_input = st.text_input("Enter comma-separated fields:", value=default_fields)

        if field_input:
            fields = [f.strip().lower() for f in field_input.split(",") if f.strip()]
            with st.spinner("🔍 Extracting entities using spaCy and predefined mappings..."):
                extracted_data = extract_with_custom_fields(extracted_text, fields)
                df = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in extracted_data.items()]))

            st.subheader("🧾 Extracted Structured Data")
            st.dataframe(df)

            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download CSV", csv, "extracted_data.csv", "text/csv")

        else:
            st.info("Please enter at least one field to extract.")
    else:
        st.error("❌ Failed to extract text from the document.")
