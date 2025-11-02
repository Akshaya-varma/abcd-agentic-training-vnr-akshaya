# summarizer.py
import os
import logging
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

def fetch_transcript(youtube_url: str) -> str:
    """
    Fetch transcript text from a YouTube video using YouTubeTranscriptApi or yt-dlp.
    """
    try:
        video_id = youtube_url.split("v=")[-1].split("&")[0]
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text = " ".join([t["text"] for t in transcript])
        return text
    except Exception as e:
        logger.warning(f"youtube-transcript-api failed; falling back to yt-dlp: {e}")

        # fallback: use yt-dlp to fetch subtitles
        import tempfile
        tmp_dir = tempfile.mkdtemp()
        tmp_file = os.path.join(tmp_dir, "%(id)s.en.vtt")

        ydl_opts = {
            "skip_download": True,
            "writeautomaticsub": True,
            "subtitleslangs": ["en"],
            "outtmpl": tmp_file,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=True)
                vtt_path = os.path.join(tmp_dir, f"{info['id']}.en.vtt")
                with open(vtt_path, "r", encoding="utf-8") as f:
                    return f.read()
        except Exception as e2:
            logger.error(f"yt-dlp subtitles fetch failed: {e2}")
            raise RuntimeError("Could not fetch transcript.")

def summarize_transcript(transcript_text: str, model: str = "gemini-2.5-flash") -> str:
    """
    Summarize the given transcript using Gemini model.
    """
    if not transcript_text.strip():
        raise ValueError("Transcript is empty.")

    prompt = f"""
You are a concise summarizer. Summarize the following YouTube transcript into key points:
{transcript_text}
"""
    try:
        model = genai.GenerativeModel(model)
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"Gemini summarization failed: {e}")
        raise RuntimeError(f"Summarization failed: {e}")
