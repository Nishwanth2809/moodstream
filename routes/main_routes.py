import os
import base64
import tempfile
import subprocess
from flask import Blueprint, request, jsonify

from utils.mood_analysis import analyze_mood_with_audio
from utils.audio_features import extract_audio_features
from utils.spotify_recommender import get_recommendations

main_bp = Blueprint("main_bp", __name__)


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

    return jsonify({
        "mood": mood,
        "songs": songs
    })


# ------------------------------
#   VOICE ANALYSIS ROUTE
# ------------------------------
@main_bp.route("/voice", methods=["POST"])
def analyze_voice():
    data = request.get_json(silent=True) or {}

    text = data.get("text", "").strip()
    audio_b64 = data.get("audio", "")
    language = data.get("language", "english")

    if not audio_b64 and not text:
        return jsonify({"error": "No audio or text provided"}), 400

    temp_webm = None
    temp_wav = None

    try:
        if audio_b64:
            # Decode base64 → raw bytes
            audio_bytes = base64.b64decode(audio_b64)

            # Create temp files (delete=False so ffmpeg can open them)
            temp_webm = tempfile.NamedTemporaryFile(delete=False, suffix=".webm")
            temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")

            temp_webm.close()
            temp_wav.close()

            # Save webm
            with open(temp_webm.name, "wb") as f:
                f.write(audio_bytes)

            # Convert webm → wav using ffmpeg (Render supports ffmpeg)
            proc = subprocess.run([
                "ffmpeg", "-y",
                "-i", temp_webm.name,
                "-ac", "1",
                "-ar", "16000",
                temp_wav.name
            ], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

            if proc.returncode != 0:
                err = proc.stderr.decode(errors="ignore")
                return jsonify({"error": "FFmpeg conversion failed", "details": err}), 500

            # Extract tempo + pitch
            tempo, pitch = extract_audio_features(temp_wav.name)
        else:
            # No audio uploaded — set defaults
            tempo, pitch = 0, 0

        # Detect mood using text + audio signals
        mood = analyze_mood_with_audio(text, tempo, pitch)
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
        # Cleanup temp files if they exist
        for tf in (temp_webm, temp_wav):
            try:
                if tf and os.path.exists(tf.name):
                    os.remove(tf.name)
            except Exception:
                pass
