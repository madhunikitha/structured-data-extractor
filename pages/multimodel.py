import os
import fitz  # PyMuPDF
import pytesseract
import streamlit as st
from PIL import Image
import tempfile
from dotenv import load_dotenv
from openai import OpenAI

# Setup
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
load_dotenv()
client = OpenAI()

st.set_page_config(page_title="Multi-Modal Analyzer")
st.title("Multi-Modal Document Analyzer")

# Convert PDF pages to images
def render_pdf_pages_as_images(file_path):
    images = []
    doc = fitz.open(file_path)
    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=300)
        img_path = f"page_{i+1}.png"
        pix.save(img_path)
        images.append(Image.open(img_path))
    return images

# OCR each image
import numpy as np
import easyocr

reader = easyocr.Reader(['en'])

def perform_ocr_on_image(image):
    image = image.convert("RGB")
    result = reader.readtext(np.array(image), detail=0)
    return "\n".join(result)


# GPT: Analyze or answer queries
def analyze_text_with_gpt(full_text, user_question):
    prompt = f"""You are an expert document analyst. Analyze the following extracted document text and answer the user query.\n\nDocument:\n{full_text}\n\nQuestion:\n{user_question}"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000,
    )
    return response.choices[0].message.content

# File Upload
uploaded_file = st.file_uploader("📤 Upload a PDF Document", type=["pdf"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_pdf_path = tmp_file.name

    st.info("🖼️ Extracting images from PDF...")
    page_images = render_pdf_pages_as_images(tmp_pdf_path)

    full_extracted_text = ""
    for i, img in enumerate(page_images):
        st.image(img, caption=f"Page {i+1}", use_column_width=True)
        ocr_text = perform_ocr_on_image(img)
        full_extracted_text += f"\n--- Page {i+1} ---\n" + ocr_text

    # Show all extracted OCR text
    st.text_area("📝 Full OCR Extracted Text", full_extracted_text, height=300)

    # User input for querying
    query = st.text_input("❓ Ask something about the document (e.g., 'What is the research budget percentage?')")

    if st.button("🔍 Ask GPT-3.5"):
        if query.strip():
            with st.spinner("Thinking..."):
                try:
                    result = analyze_text_with_gpt(full_extracted_text, query)
                    st.success(result)
                except Exception as e:
                    st.error(f"❌ GPT Error: {str(e)}")
        else:
            st.warning("⚠️ Please enter a question.")
