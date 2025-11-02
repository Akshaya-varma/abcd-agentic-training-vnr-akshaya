import os
import json
import gradio as gr
from summarizer import fetch_transcript, summarize_transcript
from google_docs import append_summary_to_gdoc
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === CONFIGURATION ===
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
DOC_ID = os.environ.get("DOC_ID", "1yCYZm6GfyN7m83zPLJqTzUL-6M0VtUAKG_UW2hCL2Ls")
IMPERSONATE_USER = os.environ.get("IMPERSONATE_USER")  # optional

# === HANDLE SERVICE ACCOUNT JSON ===
SERVICE_ACCOUNT_JSON = os.environ.get("SERVICE_ACCOUNT_JSON")  # store JSON as secret
SERVICE_ACCOUNT_PATH = "/tmp/service_key.json"

if SERVICE_ACCOUNT_JSON:
    with open(SERVICE_ACCOUNT_PATH, "w", encoding="utf-8") as f:
        f.write(SERVICE_ACCOUNT_JSON)
else:
    raise RuntimeError("SERVICE_ACCOUNT_JSON secret not found — please add it in Hugging Face Space settings.")

# === CORE LOGIC ===
def validate_youtube_url(url: str):
    return bool(url and ("youtube.com" in url or "youtu.be" in url))

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def safe_fetch_transcript(youtube_url: str):
    return fetch_transcript(youtube_url)

def run_pipeline(youtube_url: str, doc_title: str, create_doc: bool):
    if not validate_youtube_url(youtube_url):
        return "Invalid YouTube URL.", "", ""

    try:
        transcript = safe_fetch_transcript(youtube_url)
        if not transcript.strip():
            return "Transcript could not be fetched.", "", ""
    except Exception as e:
        logger.exception("Transcript fetch failed")
        return f"Transcript fetch failed: {e}", "", ""

    try:
        summary = summarize_transcript(transcript, model=GEMINI_MODEL)
    except Exception as e:
        logger.exception("Summarization failed")
        return f"Summarization failed: {e}", "", ""

    doc_url = ""
    if create_doc:
        try:
            doc_url = append_summary_to_gdoc(
                summary,
                DOC_ID,
                service_account_path=SERVICE_ACCOUNT_PATH,
                impersonate_user=IMPERSONATE_USER,
            )
        except Exception as e:
            logger.exception("Google Docs write failed")
            return f"Summary created but failed to write Google Doc: {e}", summary, ""

    return "Success ", summary, doc_url


# === GRADIO UI ===
with gr.Blocks() as demo:
    gr.Markdown("#  YouTube → Gemini Summarizer + Google Docs ")

    with gr.Row():
        url_input = gr.Textbox(label="YouTube URL", placeholder="https://www.youtube.com/watch?v=...")
    doc_title = gr.Textbox(label="Google Doc Title (for section heading)", value="YouTube Summary")
    create_doc = gr.Checkbox(label="Append to Google Doc?", value=True)
    run_btn = gr.Button("Summarize")
    status = gr.Textbox(label="Status", interactive=False)
    summary_out = gr.Textbox(label="Summary (preview)", lines=10)
    gdoc_link = gr.Textbox(label="Google Doc URL (if added)", interactive=False)

    def on_click(youtube_url, doc_title, create_doc):
        return run_pipeline(youtube_url, doc_title, create_doc)

    run_btn.click(fn=on_click, inputs=[url_input, doc_title, create_doc], outputs=[status, summary_out, gdoc_link])

if __name__ == "__main__":
    demo.launch(share=True)
