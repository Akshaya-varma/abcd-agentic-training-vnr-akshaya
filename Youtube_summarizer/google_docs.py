# google_docs.py
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
import logging

logger = logging.getLogger(__name__)

def append_summary_to_gdoc(summary_text: str, doc_id: str, service_account_path: str, impersonate_user: str = None):
    """
    Append summary_text to an existing Google Doc (given its doc_id).
    """
    if not os.path.exists(service_account_path):
        raise RuntimeError(f"Service account JSON file not found: {service_account_path}")

    scopes = [
        "https://www.googleapis.com/auth/documents",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = service_account.Credentials.from_service_account_file(service_account_path, scopes=scopes)
    if impersonate_user:
        creds = creds.with_subject(impersonate_user)

    docs = build("docs", "v1", credentials=creds)

    # Prepare text to append
    formatted_text = f"\n\n---\n **New YouTube Summary Added**\n\n{summary_text}\n"
    requests = [
        {
            "insertText": {
                "location": {"index": 1},
                "text": formatted_text
            }
        }
    ]

    docs.documents().batchUpdate(documentId=doc_id, body={"requests": requests}).execute()
    return f"https://docs.google.com/document/d/{doc_id}/edit"

