import os
import base64
import tempfile
import subprocess
from flask import Blueprint, request, jsonify, render_template
from faster_whisper import WhisperModel

from utils.mood_analysis import analyze_mood_with_audio
from utils.audio_features import extract_audio_features
from utils.spotify_recommender import get_recommendations

main_bp = Blueprint("main_bp", __name__)

# Load whisper model ONCE
model = WhisperModel("tiny", device="cpu", compute_type="int8")


# ------------------------------
#   HOME ROUTE
# ------------------------------
@main_bp.route("/")
def home():
    return render_template("front.html")


# ------------------------------
#   TEXT ANALYSIS ROUTE
# ------------------------------
@main_bp.route("/text", methods=["POST"])
def analyze_text():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")
    language = data.get("language", "english")

    if not text:
        return jsonify({"error": "No text provided"}), 400

    mood = analyze_mood_with_audio(text)
    songs = get_recommendations(mood, language)

    return jsonify({"mood": mood, "songs": songs})


# ------------------------------
#   VOICE ANALYSIS ROUTE
# ------------------------------
@main_bp.route("/voice", methods=["POST"])
def analyze_voice():
    data = request.get_json(silent=True) or {}

    audio_b64 = data.get("audio", "")
    language = data.get("language", "english")

    if not audio_b64:
        return jsonify({"error": "No audio provided"}), 400

    temp_webm = None
    temp_wav = None

    try:
        # ------------------------------
        # 1. Decode base64 → webm file
        # ------------------------------
        audio_bytes = base64.b64decode(audio_b64)

        temp_webm = tempfile.NamedTemporaryFile(delete=False, suffix=".webm")
        temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")

        with open(temp_webm.name, "wb") as f:
            f.write(audio_bytes)

        # ------------------------------
        # 2. Convert webm → wav (ffmpeg)
        # ------------------------------
        proc = subprocess.run([
            "ffmpeg", "-y",
            "-i", temp_webm.name,
            "-ac", "1",      # mono
            "-ar", "16000",  # sample rate
            temp_wav.name
        ], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

        if proc.returncode != 0:
            err = proc.stderr.decode(errors="ignore")
            return jsonify({"error": "FFmpeg conversion failed", "details": err}), 500

        # ------------------------------
        # 3. Extract tempo + pitch
        # ------------------------------
        tempo, pitch = extract_audio_features(temp_wav.name)

        # ------------------------------
        # 4. Whisper speech-to-text
        # ------------------------------
        segments, info = model.transcribe(temp_wav.name)

        text = " ".join(seg.text for seg in segments).strip()

        # ------------------------------
        # 5. Mood Detection
        # ------------------------------
        mood = analyze_mood_with_audio(text, tempo, pitch)

        # ------------------------------
        # 6. Get Recommendations
        # ------------------------------
        songs = get_recommendations(mood, language)

        return jsonify({
            "text": text,
            "mood": mood,
            "tempo": tempo,
            "pitch": pitch,
            "songs": songs
        })

    except Exception as e:
        return jsonify({"error": "Server error", "details": str(e)}), 500

    finally:
        # Cleanup temp files
        for tf in (temp_webm, temp_wav):
            try:
                if tf and os.path.exists(tf.name):
                    os.remove(tf.name)
            except:
                pass
