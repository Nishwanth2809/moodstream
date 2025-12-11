from flask import Blueprint, request, redirect, session, url_for
import requests
import time
from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI, SPOTIFY_SCOPES

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login")
def login():
    auth_url = (
        f"https://accounts.spotify.com/authorize?client_id={SPOTIFY_CLIENT_ID}"
        f"&response_type=code&redirect_uri={SPOTIFY_REDIRECT_URI}"
        f"&scope={SPOTIFY_SCOPES}"
    )
    return redirect(auth_url)

@auth_bp.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "Error: No code"

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

    # Redirect to the home endpoint on the main blueprint
    return redirect(url_for("main_bp.home"))
