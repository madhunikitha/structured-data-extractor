import streamlit as st
import pandas as pd
import json
import os
import re
import io
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.schema import Document
from main import input
from audit_logger import log_to_json

openai_api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="Smart Doc Analyzer")
st.title("Smart Document Analyzer")

# STEP 1: Get extracted text
extracted_text = input()

if extracted_text and "Error" not in extracted_text:
    st.subheader("Ask a Question")
    query = st.text_input("Enter your query about the document:")

    st.subheader("Specify Output Fields")
    field_instruction = st.text_input("E.g., name, skills, certifications")

    format_option = st.selectbox("⬇️ Select Output Format", ["CSV", "Excel", "JSON"])
    start = st.button("Run Extraction")

    if start and query and field_instruction:
        with st.spinner("💬 Thinking..."):
            try:
                splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
                chunks = splitter.split_text(extracted_text)
                docs = [Document(page_content=chunk) for chunk in chunks]

                embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
                db_name="chroma_db"
    
                if os.path.exists(db_name):
                    "checks if the databse with the name specified already exists in the current directory"
                    Chroma(persist_directory=db_name ,
                        embedding_function = embeddings).delete_collection()

                vectordb = Chroma.from_documents(
                    documents=docs,
                    embedding=embeddings,
                    persist_directory=db_name
                )
                
                retriever = vectordb.as_retriever(search_kwargs={"k": 20})
                llm = ChatOpenAI(model="gpt-3.5-turbo", api_key=openai_api_key, temperature=0)

                field_list = [f.strip().capitalize() for f in re.split(r",|and", field_instruction)]
                formatted_fields = ', '.join(field_list)

                full_query = (
                    f"{query}\n\n"
                    f"Please extract all entries from the text. For each entry, return only the following fields: {formatted_fields}. "
                    f"Format output clearly by prefixing each field with its name followed by a colon (e.g., Name: John Doe). "
                    f"Separate each entry clearly with newlines."
                )

                qa_chain = RetrievalQA.from_chain_type(
                    llm=llm,
                    retriever=retriever,
                    chain_type="map_reduce",
                    return_source_documents=True
                )
                st.session_state["qa_chain"] = qa_chain


                result = qa_chain({"query": full_query})
                answer = result["result"]

                # Parse to DataFrame
                entries = []
                current = {field: "" for field in field_list}
                lines = answer.strip().splitlines()
                log_to_json(
    query=query,
    field_instruction=field_instruction,
    prompt=full_query,
    llm_output=answer
)

                for line in lines:
                    match = re.match(r"^([\w\s]+):\s*(.*)", line)
                    if match:
                        key, value = match.groups()
                        key = key.strip().capitalize()
                        value = value.strip()
                        if key in current:
                            if key == field_list[0] and any(current.values()):
                                entries.append(current)
                                current = {f: "" for f in field_list}
                            current[key] = value

                if any(current.values()):
                    entries.append(current)

                df = pd.DataFrame(entries)
                st.session_state["original_df"] = df
                

            except Exception as e:
                st.error(f"❌ Error during extraction: {e}")
            


# STEP 2: Show Editor if Data Available
    # STEP 2: Show Editor if Data Available
    if "original_df" in st.session_state:
        st.subheader("✏️ Correct Extracted Data")
        edited_df = st.data_editor(st.session_state["original_df"], num_rows="dynamic")

        st.subheader("💬 Give Feedback to Improve the Extraction")
        user_feedback = st.text_area("📝 Enter your feedback (e.g., 'Some skills are missing' or 'Extract more details about education')")

        if st.button("♻️ Re-Generate Based on Feedback"):
            if user_feedback.strip():
                try:
                    field_list = edited_df.columns.tolist()
                    formatted_fields = ', '.join(field_list)

                    feedback_query = (
                        f"Based on the following feedback: '{user_feedback}', please regenerate the output.\n"
                        f"Use the original document content and extract only these fields: {formatted_fields}. "
                        f"Format output clearly by prefixing each field with its name followed by a colon (e.g., Name: John Doe). "
                        f"Separate each entry clearly with newlines."
                    )

                    with st.spinner("🔄 Re-generating based on feedback..."):
                        qa_chain = st.session_state.get("qa_chain")

                        feedback_result = qa_chain({"query": feedback_query})
                        feedback_answer = feedback_result["result"]

                        # Re-parse the LLM result
                        new_entries = []
                        current = {field: "" for field in field_list}
                        lines = feedback_answer.strip().splitlines()

                        for line in lines:
                            match = re.match(r"^([\w\s]+):\s*(.*)", line)
                            if match:
                                key, value = match.groups()
                                key = key.strip().capitalize()
                                value = value.strip()
                                if key in current:
                                    if key == field_list[0] and any(current.values()):
                                        new_entries.append(current)
                                        current = {f: "" for f in field_list}
                                    current[key] = value

                        if any(current.values()):
                            new_entries.append(current)

                        updated_df = pd.DataFrame(new_entries)
                        st.session_state["original_df"] = updated_df
                        st.success("✅ Output updated based on your feedback.")
                        edited_df=updated_df
                        st.dataframe(edited_df)

                except Exception as e:
                    st.error(f"❌ Error processing feedback: {e}")
            else:
                st.warning("⚠️ Please enter some feedback before clicking re-generate.")


                # Optionally send back to LLM or just allow download
        if format_option == "CSV":
                    csv = edited_df.to_csv(index=False).encode("utf-8")
                    st.download_button("📥 Download CSV", csv, file_name="corrected_output.csv", mime="text/csv")

        elif format_option == "Excel":
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        edited_df.to_excel(writer, index=False, sheet_name='Sheet1')
                    output.seek(0)
                    st.download_button(
                        label="📥 Download Excel",
                        data=output,
                        file_name="corrected_output.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

        elif format_option == "JSON":
                    json_data = edited_df.to_dict(orient="records")
                    st.download_button(
                        "📥 Download JSON",
                        json.dumps(json_data, indent=4),
                        file_name="corrected_output.json",
                        mime="application/json"
                    )

           

    
