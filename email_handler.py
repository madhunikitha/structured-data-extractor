# email_handler.py
import imaplib
import email
import tempfile
import os
import uuid
# add to a new or existing handler file (like email_handler.py)
from doc_input import extract_text_with_filename


def fetch_email_attachments(imap_server, email_user, email_pass, folder="INBOX", max_emails=5):
    try:
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(email_user, email_pass)
        mail.select(folder)

        _, messages = mail.search(None, 'UNSEEN')
        emails = messages[0].split()[-max_emails:]
        attachments_info = []

        for msg_id in emails:
            _, data = mail.fetch(msg_id, '(RFC822)')
            raw_email = data[0][1]
            message = email.message_from_bytes(raw_email)

            for part in message.walk():
                content_disposition = part.get("Content-Disposition", "")
                if "attachment" in content_disposition:
                    filename = part.get_filename()
                    file_data = part.get_payload(decode=True)

                    if filename:
                        unique_id = str(uuid.uuid4())  # generate a unique ID
                        temp_path = os.path.join(tempfile.gettempdir(), f"{unique_id}_{filename}")
                        with open(temp_path, "wb") as f:
                            f.write(file_data)

                        attachments_info.append({
                            "id": unique_id,
                            "filename": filename,
                            "temp_path": temp_path
                        })

        mail.logout()
        return attachments_info

    except Exception as e:
        return [{"error": str(e)}]
    

    
