from dotenv import load_dotenv
import gradio as gr
import re
import os
import subprocess
import json
from youtube_transcript_api import YouTubeTranscriptApi
from googleapiclient.discovery import build
from google.oauth2 import service_account
import google.generativeai as genai

# -------------------
# 🔐 API SETUP
# -------------------
load_dotenv()  # Load .env file

# 1️⃣ Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# 2️⃣ Google Docs & Drive
GOOGLE_CREDS_PATH = "service_key.json"  # downloaded from Google Cloud Console
if os.path.exists(GOOGLE_CREDS_PATH):
    creds = service_account.Credentials.from_service_account_file(
        GOOGLE_CREDS_PATH,
        scopes=[
            "https://www.googleapis.com/auth/documents",
            "https://www.googleapis.com/auth/drive",
        ],
    )
    service = build("docs", "v1", credentials=creds)
    drive_service = build("drive", "v3", credentials=creds)
else:
    service = None
    drive_service = None


# -------------------
# 🎬 EXTRACT VIDEO ID
# -------------------
def extract_video_id(url: str):
    match = re.search(r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})", url)
    return match.group(1) if match else url


# -------------------
# 🧠 GET TRANSCRIPT (robust)
# -------------------
def get_transcript_text(video_id: str) -> str:
    """Fetch YouTube transcript using API or yt-dlp fallback."""
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = transcript_list.find_transcript(["en"])
        fetched = transcript.fetch()
        text = "\n".join([entry.get("text", "") for entry in fetched])
        return text.strip()
    except Exception as e:
        print("YouTubeTranscriptAPI failed:", e)

    # Fallback: yt-dlp
    try:
        cmd = [
            "yt-dlp",
            "--write-auto-sub",
            "--sub-lang",
            "en",
            "--skip-download",
            "--sub-format",
            "json3",
            "--output",
            "%(id)s.%(ext)s",
            f"https://www.youtube.com/watch?v={video_id}",
        ]
        subprocess.run(cmd, check=True)
        sub_file = f"{video_id}.en.json3"

        if os.path.exists(sub_file):
            with open(sub_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            texts = []
            for e in data.get("events", []):
                if "segs" in e:
                    texts.extend(seg.get("utf8", "") for seg in e["segs"] if "utf8" in seg)
                elif "payload" in e:
                    texts.extend(seg.get("text", "") for seg in e["payload"] if "text" in seg)

            os.remove(sub_file)
            return " ".join(texts).strip()
        else:
            raise FileNotFoundError("Subtitle JSON file not found.")
    except Exception as e:
        raise RuntimeError(f"Error fetching transcript via yt-dlp: {e}")

    raise RuntimeError("No transcript available for this video.")


# -------------------
# ✍️ SUMMARIZE USING GEMINI
# -------------------
def summarize_text_with_gemini(text: str) -> str:
    if not text.strip():
        return "Transcript empty or unavailable."

    model = genai.GenerativeModel(model_name="gemini-1.5-flash")

    prompt = (
        "Summarize the following YouTube transcript into clear, structured, and concise notes. "
        "Use bullet points or sections if helpful:\n\n"
        + text[:12000]  # Limit to token-safe range
    )

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Gemini error: {e}"


# -------------------
# 📄 SAVE TO GOOGLE DOCS
# -------------------
def save_to_google_doc(title: str, summary: str) -> str:
    if not service or not drive_service:
        return "⚠️ Google API credentials missing (credentials.json not found)."

    try:
        doc = service.documents().create(body={"title": title}).execute()
        doc_id = doc["documentId"]

        service.documents().batchUpdate(
            documentId=doc_id,
            body={"requests": [{"insertText": {"location": {"index": 1}, "text": summary}}]},
        ).execute()

        drive_service.permissions().create(
            fileId=doc_id, body={"role": "reader", "type": "anyone"}
        ).execute()

        return f"https://docs.google.com/document/d/{doc_id}/edit"
    except Exception as e:
        return f"Google Docs error: {e}"


# -------------------
# 🚀 MAIN PROCESS
# -------------------
def process_video(url, doc_title):
    try:
        video_id = extract_video_id(url)
        transcript_text = get_transcript_text(video_id)
    except Exception as e:
        return f"Transcript error: {e}", "", ""

    summary = summarize_text_with_gemini(transcript_text)
    link = save_to_google_doc(doc_title or "YouTube Summary", summary)
    return "✅ Successfully summarized and saved to Google Docs!", summary, link


# -------------------
# 🎨 GRADIO UI
# -------------------
with gr.Blocks(title="🎥 YouTube → Gemini Summarizer → Google Docs") as app:
    gr.Markdown("## 🎥 YouTube Summarizer powered by Gemini & Google Docs")

    url_input = gr.Textbox(label="YouTube URL or Video ID")
    title_input = gr.Textbox(label="Google Doc Title (optional)")
    run_btn = gr.Button("Summarize & Save to Google Docs")

    status = gr.Textbox(label="Status")
    summary_out = gr.Textbox(label="Final Summary", lines=10)
    doc_link = gr.Textbox(label="Google Doc Link (Public)")

    run_btn.click(fn=process_video, inputs=[url_input, title_input], outputs=[status, summary_out, doc_link])

app.launch()
