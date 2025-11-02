# YouTube Summarizer + Google Docs Agent

> Transform long YouTube videos into concise AI summaries — automatically saved to Google Docs.  

---

##  Overview

The **YouTube Summarizer + Google Docs Agent** automatically converts long YouTube videos into concise, AI-generated summaries and stores them directly in **Google Docs**.  

It integrates transcript extraction, AI summarization, and Google Docs automation — all in one pipeline.

### Core Features
-  AI-powered video summarization (Google Gemini)
-  Automatic transcript fetching from YouTube
-  Google Docs updation
-  Optional local summary storage
-  Error fallback with yt-dlp

---

## **High-Level Architecture**

            ┌───────────────────────┐
            │   YouTube URL Input   │
            └──────────┬────────────┘
                       │
           ┌───────────▼────────────┐
           │ Transcript Fetcher     │
           │ (YouTube / yt-dlp)     │
           └───────────┬────────────┘
                       │
           ┌───────────▼────────────┐
           │ Gemini AI Summarizer   │
           │ (Text → Summary)       │
           └───────────┬────────────┘
                       │
           ┌───────────▼────────────┐
           │ Google Docs Integration│
           │ (Update Doc)           │
           └───────────┬────────────┘
                       │
           ┌───────────▼────────────┐
           │ Return Doc Link /      │
           │ Save Local Copy        │
           └────────────────────────┘



---

##  Key Functionalities

| Feature                     | Description                                                   |
| ---------------------------- | ------------------------------------------------------------- |
| `/summarize <YouTube_URL>`   | Fetches transcript, summarizes via Gemini AI, saves to Docs   |
| `auto_title`                 | Generates document title from video metadata                  |
| `custom_doc_name`            | Allows user-defined Google Doc titles                         |
| `transcript_fallback`        | Uses yt-dlp if YouTube API fails                              |
| `summary_storage`            | Optionally saves locally (`summaries/` folder)                |
| `doc_link_return`            | Returns Google Docs link after upload                         |

---

##  Workflow

### **1. Summarization Pipeline**
User → Provide YouTube URL
↓
Extract Video ID
↓
Fetch Transcript (YouTube / yt-dlp)
↓
Summarize using Gemini AI
↓
Update Google Doc
↓
Return Document Link 



### **2. Error Handling**
Transcript fetch fails
↓
Fallback to yt-dlp subtitles
↓
If still fails → show error:
⚠️ "Transcript unavailable for this video."



---

##  Database Design (Optional)

| Column       | Type         | Description                           |
| ------------- | ------------ | ------------------------------------- |
| id            | INTEGER (PK) | Auto-increment primary key            |
| video_id      | TEXT         | YouTube video identifier              |
| title         | TEXT         | Video or document title               |
| summary       | TEXT         | AI-generated summary text             |
| doc_link      | TEXT         | Google Docs link                      |
| timestamp     | DATETIME     | Automatically set to current time     |

---

##  Low-Level Design (LLD)

| Component              | Responsibility                                    |
| ---------------------- | ------------------------------------------------- |
| `fetch_transcript()`   | Retrieves transcript via YouTube APIs             |
| `summarize_with_ai()`  | Uses Gemini model to generate concise summary     |
| `create_google_doc()`  | Creates or updates document in Google Docs        |
| `save_local_copy()`    | Saves summary locally (optional)                  |
| `summarize_video()`    | Orchestrates fetch → summarize → save             |
| `handle_fallbacks()`   | Switches between APIs if transcript fetch fails   |

---

##  Integrations

### APIs Used
1. **YouTube Transcript API / yt-dlp**
   - Extracts subtitle/transcript text.
   - Supports fallback and multilingual captions.

2. **Google Gemini AI**
   - Model: `gemini-2.5-flash`
   - Summarizes transcripts into structured notes.

3. **Google Docs API**
   - Creates and updates documents programmatically.
   - Requires OAuth2 authentication.

---

##  Environment Variables

| Variable             | Description                                 |
| -------------------- | ------------------------------------------- |
| `GOOGLE_API_KEY`     | Google Gemini API Key                       |
| `GOOGLE_DOCS_TOKEN`  | OAuth2 token for Google Docs API             |
| `YOUTUBE_API_KEY`    | Optional key for YouTube Data API           |
| `OUTPUT_DOC_TITLE`   | Custom document title (optional)             |
| `LOCAL_SAVE`         | Boolean flag to save summaries locally      |

---

##  Tech Stack

| Layer           | Technology                                |
| ---------------- | ------------------------------------------ |
| Backend Engine   | Python 3.10+                              |
| AI Model         | Google Gemini (via `google-generativeai`) |
| APIs             | YouTube, Google Docs                      |
| Auth             | OAuth2 / dotenv                           |
| Storage          | Local / SQLite / Google Docs              |
| Libraries Used   | `youtube-transcript-api`, `yt-dlp`, `google-auth`, `google-api-python-client`, `requests`, `dotenv` |

---


##  Execution Steps

1. **Install dependencies**
   pip install youtube-transcript-api yt-dlp google-generativeai google-api-python-client google-auth-httplib2 google-auth-oauthlib python-dotenv requests
2. **Set environment variables**

GOOGLE_API_KEY=<your_gemini_api_key>
GOOGLE_DOCS_TOKEN=<your_oauth_token>

3. **Run the application**

python app.py
4. **Provide a YouTube URL**

https://www.youtube.com/watch?v=VIDEO_ID
## Example Output
**Input**

https://www.youtube.com/watch?v=PpH_mi923_A
**Output**

✅ Successfully summarized and saved to Google Docs!
 Document: "AI Policy Explained — Summary"

Summary:
• Global policymakers are focusing on AI safety and regulation.  
• Multiple nations are drafting AI ethics frameworks.  
• Tech leaders emphasize responsible innovation.  
• OpenAI and Google promote transparency and alignment.  
• Collaboration is key for the next phase of AI development.


## **Process Flow (Detailed)**

         ┌──────────────────────────┐
         │  User Inputs YouTube URL  │
         └─────────────┬─────────────┘
                       │
       ┌───────────────▼───────────────┐
       │  Extract Transcript (yt-dlp)  │
       │  → Fetch captions/subtitles   │
       └───────────────┬───────────────┘
                       │
       ┌───────────────▼───────────────┐
       │  Summarize via Gemini Model   │
       │  → Generate concise summary   │
       └───────────────┬───────────────┘
                       │
       ┌───────────────▼───────────────┐
       │  Save to Google Docs API      │
       │  → Create & write summary     │
       └───────────────┬───────────────┘
                       │
       ┌───────────────▼───────────────┐
       │ Return Google Doc Link / Save │
       │ Local Copy Confirmation       │
         


## Future Enhancements
 - Chrome extension for instant summarization.
 - Notion / Slack integrations.
 - Playlist batch summarization.
 - Smart topic tagging (auto keywords from Gemini).
 - Voice summary output (Text-to-Speech).



