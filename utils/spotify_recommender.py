import os
import random
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# ----------------------------------------
#  SPOTIFY CLIENT
# ----------------------------------------
sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")
    )
)

# ----------------------------------------
#  MOOD → PLAYLIST MAPPING
# ----------------------------------------
MOOD_PLAYLISTS = {
    "happy": {
        "english": "4Ml5FIY5qJ1qoSzjpgszx5",
        "hindi": "3D6sC3UYQUvTDuRE5hCqY4",
        "telugu": "293UF8TMOQFFtNwhctlKwU"
    },
    "sad": {
        "english": "0wZ03RU2rEOQ62qPpRghKV",
        "hindi": "7taJQO4qe6RlPAGimE9qRC",
        "telugu": "2BCsnZdPuiPV19hNulkQgT"
    },
    "neutral": {
        "english": "1YTrQChc67rZoNfG1YoTch",
        "hindi": "1YTrQChc67rZoNfG1YoTch",
        "telugu": "1YTrQChc67rZoNfG1YoTch"
    },
    "love": {
        "english": "46FwKzf5zAc7LnWJ8Gb0Ua",
        "hindi": "00tMG0oI6eqLUP0MsUxz12",
        "telugu": "5yFLeTOySZFQ9K1kFfmE6x"
    },
    "angry": {
        "english": "5I57hzwg68PIr0Xu0nX0pE",
        "hindi": "62QYDyNWB18qN0IjG6PVH8",
        "telugu": "6IY6M71r9yLzsOslKD7BzH"
    }
}

# ----------------------------------------
#  FETCH SONGS FROM PLAYLIST
# ----------------------------------------
def fetch_playlist_tracks(playlist_id):
    """Returns track info for a playlist."""
    try:
        data = sp.playlist_items(playlist_id)

        songs = []
        for item in data.get("items", []):
            track = item.get("track")

            if not track:
                continue

            songs.append({
                "name": track["name"],
                "artist": track["artists"][0]["name"],
                "cover": track["album"]["images"][0]["url"] if track["album"]["images"] else "",
                "spotify_url": track["external_urls"]["spotify"]
            })

        return songs

    except Exception as e:
        print("Spotify API error:", e)
        return []


# ----------------------------------------
#  MAIN RECOMMENDER FUNCTION
# ----------------------------------------
def get_recommendations(mood: str, language: str):
    mood = mood.lower().strip()
    language = language.lower().strip()

    if mood not in MOOD_PLAYLISTS:
        mood = "neutral"

    playlist_id = MOOD_PLAYLISTS.get(mood, {}).get(language)

    if not playlist_id:
        return []

    songs = fetch_playlist_tracks(playlist_id)

    if not songs:
        return []

    # Return 3 random songs
    return random.sample(songs, min(3, len(songs)))
