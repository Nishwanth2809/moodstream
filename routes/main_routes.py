import os
import base64
import tempfile
import subprocess
from flask import Blueprint, request, jsonify, render_template

from utils.mood_analysis import analyze_mood_with_audio
from utils.audio_features import extract_audio_features
from utils.spotify_recommender import get_recommendations

main_bp = Blueprint("main_bp", __name__)

@main_bp.route("/")
def home():
    return render_template("front.html")


# --------------------------
#   TEXT INPUT ROUTE
# --------------------------
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


# --------------------------
#   VOICE INPUT ROUTE
# --------------------------
@main_bp.route("/voice", methods=["POST"])
def analyze_voice():
    data = request.get_json(silent=True) or {}

    text = data.get("text", "").strip()  # Whisper in browser gives this
    audio_b64 = data.get("audio", "")
    language = data.get("language", "english")

    if not text:
        return jsonify({"error": "No text received from Whisper"}), 400

    tempo = 0
    pitch = 0

    # If audio exists, extract tempo + pitch
    if audio_b64:
        try:
            audio_bytes = base64.b64decode(audio_b64)

            temp_webm = tempfile.NamedTemporaryFile(delete=False, suffix=".webm")
            temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")

            with open(temp_webm.name, "wb") as f:
                f.write(audio_bytes)

            # convert webm → wav
            subprocess.run([
                "ffmpeg", "-y",
                "-i", temp_webm.name,
                "-ac", "1",
                "-ar", "16000",
                temp_wav.name
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            tempo, pitch = extract_audio_features(temp_wav.name)

        except Exception as e:
            print("Audio processing error:", e)

        finally:
            try:
                os.remove(temp_webm.name)
                os.remove(temp_wav.name)
            except:
                pass

    # Final mood detection
    mood = analyze_mood_with_audio(text, tempo, pitch)
    songs = get_recommendations(mood, language)

    return jsonify({
        "text": text,
        "mood": mood,
        "tempo": tempo,
        "pitch": pitch,
        "songs": songs
    })
