import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

_sia = None
_models_loaded = False

def _load_models():
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
        _models_loaded = True

def get_sia():
    _load_models()
    return _sia

def analyze_mood_with_audio(text, tempo=0, avg_pitch=0):
    try:
        sia = get_sia()
        sentiment = sia.polarity_scores(text)
        compound = sentiment["compound"]
    except:
        return simple_mood_analysis(text, tempo, avg_pitch)

    norm_tempo = min(max((tempo - 40) / (200 - 40), 0), 1)
    norm_pitch = min(max((avg_pitch - 50) / (500 - 50), 0), 1)
    norm_sentiment = (compound + 1) / 2

    lower = text.lower()
    if "love" in lower:
        return "love"
    if any(w in lower for w in ["angry", "furious", "rage"]):
        return "angry"
    if any(w in lower for w in ["sad", "cry", "tear", "depressed"]):
        return "sad"
    if any(w in lower for w in ["happy", "joy", "great"]):
        return "happy"

    score = 0.4 * norm_sentiment + 0.3 * norm_tempo + 0.3 * norm_pitch

    if score >= 0.7:
        return "happy"
    elif score <= 0.3:
        return "sad"
    elif avg_pitch > 250 and tempo > 120:
        return "angry"
    else:
        return "neutral"

def simple_mood_analysis(text, tempo=0, avg_pitch=0):
    lower = text.lower()
    if "love" in lower:
        return "love"
    if any(w in lower for w in ["angry", "furious", "rage"]):
        return "angry"
    if any(w in lower for w in ["sad", "cry", "depressed"]):
        return "sad"
    if any(w in lower for w in ["happy", "joy", "great"]):
        return "happy"
    return "neutral"


