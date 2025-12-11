import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

_sia = None
_models_loaded = False


def _load_models():
    """
    Loads NLTK VADER sentiment model safely only once.
    """
    global _sia, _models_loaded
    if _models_loaded:
        return

    try:
        nltk.download("punkt", quiet=True)
        nltk.download("vader_lexicon", quiet=True)
        _sia = SentimentIntensityAnalyzer()
        _models_loaded = True
    except Exception as e:
        print(f"Warning: Could not load NLP models: {e}")
        _sia = None
        _models_loaded = True


def get_sia():
    """
    Returns initialized SentimentIntensityAnalyzer or None.
    """
    _load_models()
    return _sia


def analyze_mood_with_audio(text, tempo=0, avg_pitch=0):
    """
    Combines:
    - NLP sentiment analysis
    - Tempo (energy)
    - Pitch (intensity)
    To determine mood accurately.
    """

    # Try NLP model
    try:
        sia = get_sia()
        sentiment = sia.polarity_scores(text) if sia else {"compound": 0}
        compound = sentiment["compound"]
    except Exception:
        compound = 0  # fallback

    # Normalize values
    norm_tempo = min(max((tempo - 40) / (200 - 40), 0), 1)
    norm_pitch = min(max((avg_pitch - 50) / (500 - 50), 0), 1)
    norm_sentiment = (compound + 1) / 2  # compound [-1,1] → [0,1]

    lower = text.lower()

    # Force-detect keywords
    if "love" in lower:
        return "love"
    if any(w in lower for w in ["angry", "furious", "rage"]):
        return "angry"
    if any(w in lower for w in ["sad", "cry", "tear", "depressed"]):
        return "sad"
    if any(w in lower for w in ["happy", "joy", "great"]):
        return "happy"

    # Weighted mood score  
    score = 0.4 * norm_sentiment + 0.3 * norm_tempo + 0.3 * norm_pitch

    # Mood decision rules
    if score >= 0.7:
        return "happy"
    elif score <= 0.3:
        return "sad"
    elif avg_pitch > 250 and tempo > 120:
        return "angry"
    else:
        return "neutral"
