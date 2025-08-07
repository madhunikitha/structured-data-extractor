attachments = fetch_email_attachments(server, username, password)

if attachments and "error" not in attachments[0]:
    print("Unread email attachments:")
    for i, att in enumerate(attachments):
        print(f"{i+1}. {att['filename']} (ID: {att['id']})")

    user_choice = int(input("Select the attachment number to extract text: ")) - 1
    chosen_path = attachments[user_choice]["temp_path"]

    result = extract_text_from_tempfile(chosen_path)
    print("\nExtracted Text:\n")
    print(result["text"])
else:
    print("No attachments or an error occurred.")
