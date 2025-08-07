import os
import re
import io
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.schema import Document
from io import StringIO
from main import input
# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")


# UI for user input
st.set_page_config(page_title="DocuVision AI | Tabular Data Extraction")
st.title("DocuVision AI: Tabular Data Extraction ")


extracted_text = input()  # Replace with dynamic file input integration

# Check if extraction succeeded
if extracted_text and "Error" not in extracted_text:
    

    st.subheader("Ask a Question")
    query = st.text_input("Enter your query about the document:")

    st.subheader("Specify Output Fields")
    field_instruction = st.text_input("E.g., name, skills, certifications")

    start = st.button("🔎 Run Extraction")

    if start and query and field_instruction:
        with st.spinner("💬 Processing..."):
            try:
                # Split text into chunks
                splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
                chunks = splitter.split_text(extracted_text)
                docs = [Document(page_content=chunk) for chunk in chunks]

                # Generate embeddings and create vector DB
                embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
                vectordb = Chroma.from_documents(docs, embedding=embeddings)
                retriever = vectordb.as_retriever(search_kwargs={"k": 5})

                # Load LLM
                llm = ChatOpenAI(model="gpt-3.5-turbo", api_key=openai_api_key, temperature=0)

                # Format field instructions
                field_list = [f.strip().capitalize() for f in re.split(r",|and", field_instruction)]
                formatted_fields = ', '.join(field_list)

                # Create complete query
                full_query = (
                    f"{query}\n\n"
                    f"Extract the tabular data and all possible entries from the text. For each entry, return only the following fields: "
                    f"{formatted_fields}. Format the output as clean and complete CSV rows. "
                    f"Include all detected rows, and do not skip empty values. No markdown, only plain text table."
                )

                # Run RAG chain
                qa_chain = RetrievalQA.from_chain_type(
                    llm=llm,
                    retriever=retriever,
                    chain_type="map_reduce",
                    return_source_documents=True
                )

                result = qa_chain({"query": full_query})
                answer = result["result"]

                # Display and convert to CSV
                st.success("✅ Extraction Complete. Preview Below:")
                st.code(answer, language="text")

                df = pd.read_csv(StringIO(answer))
                csv_data = df.to_csv(index=False).encode("utf-8")

                st.download_button(
                    label="📥 Download CSV",
                    data=csv_data,
                    file_name="output.csv",
                    mime="text/csv"
                )
                

            except Exception as e:
                st.error(f"❌ Error during processing: {e}")

