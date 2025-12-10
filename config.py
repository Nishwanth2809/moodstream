import os

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# Use environment-specific redirect URI
if os.getenv("VERCEL_ENV"):
    SPOTIFY_REDIRECT_URI = f"https://{os.getenv('VERCEL_URL')}/callback"
else:
    SPOTIFY_REDIRECT_URI = "http://localhost:5000/callback"

SPOTIFY_SCOPES = "streaming user-read-playback-state user-modify-playback-state"
