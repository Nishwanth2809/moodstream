import sys
import os
from pathlib import Path

# Add parent directory to Python path
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Minimal Flask app for serverless
from flask import Flask, render_template

# Create Flask app
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "default_secret_key")

# Simple home route that doesn't require heavy imports
@app.route('/')
def home():
    try:
        return render_template("front.html")
    except Exception as e:
        return f"<h1>Home Page</h1><p>Error loading template: {e}</p>", 200

# Health check route
@app.route('/health')
def health():
    return {"status": "ok"}, 200

# Login route
@app.route('/login')
def login():
    try:
        from config import SPOTIFY_CLIENT_ID, SPOTIFY_REDIRECT_URI, SPOTIFY_SCOPES
        from flask import redirect
        
        auth_url = (
            f"https://accounts.spotify.com/authorize?client_id={SPOTIFY_CLIENT_ID}"
            f"&response_type=code&redirect_uri={SPOTIFY_REDIRECT_URI}"
            f"&scope={SPOTIFY_SCOPES}"
        )
        return redirect(auth_url)
    except Exception as e:
        return f"<h1>Error</h1><p>{str(e)}</p>", 500

# Text mood route
@app.route('/text', methods=['POST'])
def text_input():
    try:
        from flask import request, jsonify
        from utils.mood_analysis import analyze_mood_with_audio
        from utils.spotify_helper import get_songs_by_mood_and_language
        
        data = request.get_json()
        text = data.get("text", "")
        language = data.get("language", "english").lower()
        mood = analyze_mood_with_audio(text)
        songs = get_songs_by_mood_and_language(mood, language)
        return jsonify({"text": text, "mood": mood, "songs": songs})
    except Exception as e:
        from flask import jsonify
        return jsonify({"error": str(e)}), 500

# Callback route
@app.route('/callback')
def callback():
    try:
        from flask import request, redirect, session, url_for
        import requests
        import time
        from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI
        
        code = request.args.get("code")
        if not code:
            return "Error: No code", 400

        token_data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": SPOTIFY_REDIRECT_URI,
            "client_id": SPOTIFY_CLIENT_ID,
            "client_secret": SPOTIFY_CLIENT_SECRET
        }

        response = requests.post("https://accounts.spotify.com/api/token", data=token_data)
        token_info = response.json()

        session["access_token"] = token_info.get("access_token")
        session["refresh_token"] = token_info.get("refresh_token")
        session["expires_at"] = time.time() + token_info.get("expires_in", 3600)

        return redirect(url_for("home"))
    except Exception as e:
        return f"<h1>Error</h1><p>{str(e)}</p>", 500





