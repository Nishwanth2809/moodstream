import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

# Lazy load
_sia = None

def get_sia():
    global _sia
    if _sia is None:
        try:
            nltk.download("vader_lexicon", quiet=True)
            _sia = SentimentIntensityAnalyzer()
        except Exception as e:
            print(f"Sentiment model load failed: {e}")
            _sia = None
    return _sia

def analyze_mood_with_audio(text, tempo=0, avg_pitch=0):
    sia = get_sia()
    try:
        sentiment = sia.polarity_scores(text) if sia else {"compound": 0}
        compound = sentiment["compound"]
    except:
        compound = 0

    lower = text.lower()

    if "love" in lower:
        return "love"
    if any(w in lower for w in ["angry", "furious", "rage"]):
        return "angry"
    if any(w in lower for w in ["sad", "cry", "depressed"]):
        return "sad"

    if compound <= -0.4:
        return "sad"
    if compound >= 0.4:
        return "happy"

    return "neutral"
