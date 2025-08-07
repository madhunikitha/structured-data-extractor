# 📄 DocuVision AI

**DocuVision AI** is an intelligent document processing system that extracts structured data from unstructured documents such as scanned PDFs, handwritten notes, and images. It uses OCR, vector databases, and LLMs to perform field-specific extraction, answer document-related queries, and convert content into clean, downloadable formats.

---

## 🚀 Features

- Upload scanned PDFs or images for processing  
- Perform OCR on typed or handwritten text  
- Ask questions or specify fields using natural language  
- Extract tables and structured information using GPT-3.5  
- Edit extracted content before downloading  
- Export results as CSV, Excel, or JSON  
- Maintain audit logs for traceability and debugging  
- **Fallback with NER Model** – If the API call fails (e.g., due to network issues or API errors), the system falls back to using a local **spaCy NER model** for basic entity extraction.

---

## 📂 Project Structure

structured-data-extractor
│
├── Home.py # Main Streamlit dashboard
├── main.py # Core logic for GPT & retrieval
├── audit_logger.py # Logs interactions
├── doc_input.py # OCR input processing
├── email_handler.py # (Optional) Document input via email
├── audit_log.json # Logs storage
├── req.txt # Python dependencies
├── README.md # Project documentation
│
├── pages/ # Streamlit multipage apps
│ ├── Structured Data Extraction.py
│ ├── NER based extraction.py # Fallback NER-based field extraction (spaCy)
│
├── chroma_db/ # Vector database (for embeddings)
├── myenv/ # Virtual environment (should be .gitignored)
└── pycache/ # Python bytecode cache (should be .gitignored)


---

## ⚙️ Technologies Used

- **Streamlit** – Web UI  
- **EasyOCR / Tesseract** – OCR for text and handwriting  
- **LangChain** – LLM orchestration and chunking  
- **OpenAI GPT-3.5** – Query answering and data extraction  
- **Chroma DB** – Vector storage for semantic retrieval  
- **pandas** – Data manipulation and export  
- **PyMuPDF**, **PIL** – PDF and image processing  
- **dotenv**, **regex**, **json** – Utility and logging
- **spaCy** – Entity extraction (NER)


---

## 🧠 How It Works

1. **Document Upload** – User uploads PDF or image  
2. **OCR Extraction** – Text is extracted using OCR engines  
3. **Chunking & Embedding** – Text is split and embedded into vectors  
4. **LLM-Based Analysis** – GPT-3.5 processes user queries and fields  
5. **Data Extraction** – Structured data or tables are extracted  
6. **Review & Export** – Editable output is shown and downloadable  
7. **Audit Logging** – Logs are saved for tracking queries and results

---

## 📥 Installation

### 1. Clone the Repository

git clone https://github.com/madhunikitha/structured-data-extractor.git
cd structured-data-extractor

### 1. Create and Activate Virtual Environment

python -m venv myenv

source myenv/bin/activate   # On Windows: myenv\Scripts\activate

### 2. Install Requirements

pip install -r requirements.txt

### 3. Set OpenAI API Key

Create a .env file in the project root and add your API key:

OPENAI_API_KEY=your-api-key-here

### 4. Run the App

streamlit run Home.py

## 📌 Use Cases

- **Legal Document Field Extraction**  
  Extract key fields such as party names, dates, clauses, and terms from legal contracts and agreements.

- **Resume or Form Data Extraction**  
  Automatically extract structured information from resumes, application forms, or scanned templates.

- **Invoice Table Parsing and Conversion**  
  Identify and extract tabular data like item lists, prices, and totals from invoices for financial processing.

- **Summarizing or Querying Handwritten Notes**  
  Convert handwritten notes into searchable text and allow natural language queries or summarization.
