
def input():
    import streamlit as st
    import requests
    from doc_input import extract_text, extract_text_with_filename
    from email_handler import fetch_email_attachments
    

    

    text = ""
    uploaded_file = None
    filename = None

    option = st.radio("Choose input method:", ["Upload File", "Email Fetch"])

    # File Upload Option
    if option == "Upload File":
        uploaded_file = st.file_uploader("Upload file", type=["pdf", "docx", "jpg", "jpeg", "png", "txt"])
        if uploaded_file:
            filename = uploaded_file.name
            text = extract_text(uploaded_file)
            st.text_area("Extracted Text", text, height=300)

    # Email Fetch Option
    elif option == "Email Fetch":
        st.subheader("🔐 Provide Email Credentials (IMAP)")
        email_user = st.text_input("Email", placeholder="your_email@gmail.com", key="email_user")
        email_pass = st.text_input("App Password", type="password", placeholder="your_app_password", key="email_pass")

        if st.button("Fetch Attachments"):
            if not email_user or not email_pass:
                st.warning("⚠️ Please enter both email and app password.")
            else:
                with st.spinner("Fetching and processing emails..."):
                    try:
                        attachments = fetch_email_attachments(
                            "imap.gmail.com",
                            email_user,
                            email_pass,
                            folder="INBOX",
                            max_emails=5
                        )

                        if not attachments:
                            st.error("❌ No attachments found or couldn't fetch emails.")
                        elif "error" in attachments[0]:
                            st.error(f"❌ Error while fetching: {attachments[0]['error']}")
                        else:
                            # Save to session state
                            st.session_state.attachments = attachments

                    except Exception as e:
                        st.error(f"🔥 Unexpected error: {str(e)}")

    # Show dropdown only if attachments exist
        if "attachments" in st.session_state:
            attachments = st.session_state.attachments
            options = [f"{i+1}. {att['filename']}" for i, att in enumerate(attachments)]
            choice = st.selectbox("Select attachment to extract", options, key="attachment_choice")

            index = int(choice.split(".")[0]) - 1
            chosen = attachments[index]

            result = extract_text_with_filename(chosen["temp_path"], chosen["filename"])
            text=result["text"]
            if "error" in result:
                st.error(f"❌ Error during extraction: {result['error']}")
            else:
                st.text_area("📄 Extracted Text", result["text"], height=300)




   
    return(text)

    # =======================
    # Post Extraction Section
    # =======================

