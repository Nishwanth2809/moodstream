from flask import Blueprint, request, jsonify, render_template
from utils.mood_analysis import analyze_mood_with_audio
from utils.spotify_helper import get_songs_by_mood_and_language

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    return render_template("front.html")


@main_bp.route("/text", methods=["POST"])
def text_input():
    data = request.get_json()
    text = data.get("text", "")
    language = data.get("language", "english").lower()

    # Mood analysis (text-only, since browser Whisper handles transcription)
    mood = analyze_mood_with_audio(text)

    # Get recommended songs
    songs = get_songs_by_mood_and_language(mood, language)

    return jsonify({
        "text": text,
        "mood": mood,
        "songs": songs
    })
