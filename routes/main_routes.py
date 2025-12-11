import os
import base64
import json
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
    data = request.get_json()
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
    try:
        data = request.get_json()

        text = data.get("text", "")
        audio_b64 = data.get("audio", "")
        language = data.get("language", "english")

        if not audio_b64:
            return jsonify({"error": "No audio received"}), 400

        # Convert base64 → raw bytes
        audio_bytes = base64.b64decode(audio_b64)

        # Create temp files
        temp_webm = tempfile.NamedTemporaryFile(delete=False, suffix=".webm")
        temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")

        # Save webm
        with open(temp_webm.name, "wb") as f:
            f.write(audio_bytes)

        # Convert webm → wav using FFmpeg (Render supports FFmpeg)
        subprocess.run([
            "ffmpeg", "-y",
            "-i", temp_webm.name,
            "-ac", "1",
            "-ar", "16000",
            temp_wav.name
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Extract tempo + pitch
        tempo, pitch = extract_audio_features(temp_wav.name)

        # Detect mood using text + audio signals
        mood = analyze_mood_with_audio(text, tempo, pitch)

        # Get songs
        songs = get_recommendations(mood, language)

        # Cleanup
        os.remove(temp_webm.name)
        os.remove(temp_wav.name)

        return jsonify({
            "mood": mood,
            "tempo": tempo,
            "pitch": pitch,
            "songs": songs
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
