# AI Utils — Translate • Speak • OCR (Flask + Google Cloud + Render)

A fast, server-backed web app for Language Translation, Voice → Text (Speak), and Image → Text (OCR).
Built with Flask + Google Cloud (Translation & Vision) and deployed on Render.


# ✨ Features

Translate text (100+ languages) with auto-detect source

Speak: click Speak → talk → transcription appears (with live visualizer)

OCR: drag & drop an image (PNG/JPG/WebP) → extract text

Clean, responsive UI (tabs, dark mode, copy/swap, toasts, char counter)

Secure: API keys are server-side only (never exposed to the browser)



# 🧱 Tech Stack

Frontend: HTML, CSS, Vanilla JS

Backend: Python Flask, Gunicorn

Cloud APIs: Google Cloud Translation v2, Vision (DOCUMENT_TEXT_DETECTION)

Hosting: Render (Web Service)

# 🗺️ Architecture (at a glance)
Browser (UI)
 ├─ GET /                → Serves static/index.html
 ├─ GET /api/languages   → Flask → Google Translation (language list)
 ├─ POST /api/translate  → Flask → Google Translation (text → text)
 └─ POST /api/ocr        → Flask → Google Vision (image → text)

Speak (browser-only): Web Speech API + Web Audio visualizer (Chrome/Edge recommended)
Secrets: Stored as environment variables on server (Render). .env only for local dev.
	
# ▶️ Quick Start (Local)

# Clone

git clone https://github.com/BigDave07/ai-utils-translator-ocr-speech_to_text
cd https://github.com/BigDave07/ai-utils-translator-ocr-speech_to_text

# Create & activate a venv

python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate # macOS/Linux


# Install deps

pip install -r requirements.txt


# Secrets
Create .env (do not commit this):

GCP_API_KEY=YOUR_GOOGLE_CLOUD_API_KEY


In Google Cloud Console, enable:

Cloud Translation API

Cloud Vision API

Run

python app.py


Open http://localhost:5000

Note: The Speak tab uses the Web Speech API (best on Chrome/Edge).
For full cross-browser speech, you can add a server STT endpoint later.

# ☁️ Deploy on Render

Push this repo to GitHub.

On Render → New → Web Service → pick your repo.

Use:

Environment: Python

Build Command: pip install -r requirements.txt

Start Command: gunicorn -b 0.0.0.0:$PORT app:app

# Environment Variables:

GCP_API_KEY = YOUR_GOOGLE_CLOUD_API_KEY

(Optional) PYTHON_VERSION = 3.11.9

Create → wait for build → open your Render URL ✅

On Render’s free tier, services can sleep when idle; first request may be slower.

# 🔌 API Endpoints
GET /api/languages

Returns supported languages with English names.

Example response

{
  "languages": [
    { "language": "af", "name": "Afrikaans" },
    { "language": "ar", "name": "Arabic" }
  ]
}

POST /api/translate

Translate text.

Request

{ "text": "Hola mundo", "target": "en", "source": "auto" }


Response

{ "translatedText": "Hello world", "detectedSourceLanguage": "es" }


cURL

curl -s -X POST https://YOUR-RENDER-URL/api/translate \
  -H "Content-Type: application/json" \
  -d '{"text":"Bonjour tout le monde","target":"en","source":"auto"}'

POST /api/ocr

OCR for images (PNG/JPG/WebP). Returns extracted text.

cURL

curl -s -X POST https://YOUR-RENDER-URL/api/ocr \
  -F "image=@./tests/sample.jpg"

# 🔐 Security Notes

Never commit secrets. Keep .env local; set GCP_API_KEY in Render.

Validate uploads: allow only image types and set a safe size cap (e.g., 6 MB).

Consider rate limiting (e.g., flask-limiter) if you open this publicly.

# 🧪 Troubleshooting

requirements.txt not found → ensure it’s at repo root (or set Root Directory in Render).

403 from Google → enable Translation/Vision for the same GCP project as your key.

Missing/invalid key → set GCP_API_KEY in Render → redeploy.

Speak not working → use Chrome/Edge and allow microphone (lock icon → Site settings → Microphone → Allow).

CORS → if UI & API share origin (same Flask app), you’re fine. If not, enable CORS.

# 🗂️ Project Structure
YOUR-REPO/
├─ app.py                  # Flask app & endpoints
├─ requirements.txt        # Python deps
├─ static/
│  └─ index.html           # Single-page UI (Translate, Speak, OCR)
├─ .gitignore
└─ .env                    # local only (not committed)
