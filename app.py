import os
import base64
import requests
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

TRANSLATE_URL = "https://translation.googleapis.com/language/translate/v2"
LANGUAGES_URL = f"{TRANSLATE_URL}/languages"
VISION_URL = "https://vision.googleapis.com/v1/images:annotate"

API_KEY = os.getenv("GCP_API_KEY")
if not API_KEY:
    raise RuntimeError("GCP_API_KEY not set. Put it in .env or set env var.")

app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)

@app.get("/")
def root():
    return send_from_directory("static", "index.html")

# ---- Languages (needed for populating the selects) ----
@app.get("/api/languages")
def get_languages():
    """
    Returns Google's supported languages with English names for display.
    """
    params = {"key": API_KEY, "target": "en"}
    try:
        r = requests.get(LANGUAGES_URL, params=params, timeout=15)
        r.raise_for_status()
        data = r.json().get("data", {})
        # Expected shape: { "languages": [ { "language": "af", "name": "Afrikaans" }, ... ] }
        return jsonify(data)
    except requests.exceptions.HTTPError as e:
        return jsonify({"error": f"Languages API error: {e.response.text}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---- Translate ----
@app.post("/api/translate")
def translate():
    """
    Translates text via Google Translate v2.
    """
    payload = request.get_json(silent=True) or {}
    text = (payload.get("text") or "").strip()
    target = (payload.get("target") or "en").strip()
    source = (payload.get("source") or "").strip().lower()

    if not text:
        return jsonify({"error": "missing 'text'"}), 400

    params = {
        "key": API_KEY,
        "q": text,
        "target": target,
        "format": "text",
    }
    if source and source != "auto":
        params["source"] = source

    try:
        r = requests.post(TRANSLATE_URL, params=params, timeout=15)
        r.raise_for_status()
        translations = r.json()["data"]["translations"]
        result = translations[0]
        return jsonify({
            "translatedText": result.get("translatedText"),
            "detectedSourceLanguage": result.get("detectedSourceLanguage"),
        })
    except requests.exceptions.HTTPError as e:
        return jsonify({"error": f"Translation API error: {e.response.text}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---- OCR ----
@app.post("/api/ocr")
def ocr():
    """
    OCR via Google Vision (DOCUMENT_TEXT_DETECTION).
    Accepts multipart/form-data with 'image' file (PNG/JPG/WebP).
    """
    if "image" not in request.files:
        return jsonify({"error": "Missing 'image' file."}), 400

    file = request.files["image"]

    allowed_mimes = {"image/png", "image/jpeg", "image/webp"}
    allowed_exts = (".png", ".jpg", ".jpeg", ".webp")
    if (file.mimetype not in allowed_mimes) and (not file.filename.lower().endswith(allowed_exts)):
        return jsonify({"error": "Unsupported file type. Use PNG/JPG/WEBP."}), 400

    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    if size > 6 * 1024 * 1024:
        return jsonify({"error": "File too large (max 6 MB)."}), 413

    img_bytes = file.read()
    img_b64 = base64.b64encode(img_bytes).decode("utf-8")

    body = {
        "requests": [{
            "image": {"content": img_b64},
            "features": [{"type": "DOCUMENT_TEXT_DETECTION"}]
        }]
    }

    try:
        r = requests.post(f"{VISION_URL}?key={API_KEY}", json=body, timeout=30)
        r.raise_for_status()
        payload = r.json()
        text = payload["responses"][0].get("fullTextAnnotation", {}).get("text", "")
        return jsonify({"text": text})
    except requests.exceptions.HTTPError as e:
        return jsonify({"error": e.response.text}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)
