from flask import Blueprint, request, jsonify, render_template
from utils.mood_analysis import analyze_mood_with_audio
from utils.audio_features import extract_audio_features
from utils.spotify_helper import get_songs_by_mood_and_language
import base64, io, os
from pydub import AudioSegment

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def home():
    return render_template("front.html")

@main_bp.route("/text", methods=["POST"])
def text_input():
    data = request.get_json()
    text = data.get("text", "")
    language = data.get("language", "english").lower()

    mood = analyze_mood_with_audio(text)
    songs = get_songs_by_mood_and_language(mood, language)

    return jsonify({
        "text": text,
        "mood": mood,
        "songs": songs
    })

@main_bp.route("/voice", methods=["POST"])
def voice_input():
    try:
        data = request.get_json()

        text = data.get("text", "")
        audio_base64 = data.get("audio")   # <-- FIXED
        language = data.get("language", "english").lower()

        if not audio_base64:
            return jsonify({"error": "No audio received"}), 400

        # Decode audio
        audio_data = base64.b64decode(audio_base64)
        audio = AudioSegment.from_file(io.BytesIO(audio_data), format="webm")
        audio = audio.set_frame_rate(16000).set_channels(1)

        temp_path = "temp_audio.wav"
        audio.export(temp_path, format="wav")

        tempo, pitch = extract_audio_features(temp_path)

        mood = analyze_mood_with_audio(text, tempo, pitch)
        songs = get_songs_by_mood_and_language(mood, language)

        os.remove(temp_path)

        return jsonify({
            "text": text,
            "tempo": tempo,
            "pitch": pitch,
            "mood": mood,
            "songs": songs
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

