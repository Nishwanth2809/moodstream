import spacy
import nltk
import numpy as np
from nltk.sentiment import SentimentIntensityAnalyzer

# Lazy load models
_nlp = None
_sia = None
_models_loaded = False

def _load_models():
    global _nlp, _sia, _models_loaded
    if _models_loaded:
        return
    try:
        nltk.download("punkt", quiet=True)
        nltk.download("vader_lexicon", quiet=True)
        _nlp = spacy.load("en_core_web_sm")
        _sia = SentimentIntensityAnalyzer()
        _models_loaded = True
    except Exception as e:
        print(f"Warning: Could not load NLP models: {e}")
        _models_loaded = True

def get_nlp():
    _load_models()
    return _nlp

def get_sia():
    _load_models()
    return _sia

def analyze_mood_with_audio(text, tempo=0, avg_pitch=0):
    try:
        sia = get_sia()
        nlp = get_nlp()
        
        if sia is None or nlp is None:
            # Fallback to simple analysis
            return simple_mood_analysis(text, tempo, avg_pitch)
        
        sentiment = sia.polarity_scores(text)
        compound = sentiment["compound"]
        doc = nlp(text)
        if any(tok.dep_ == "neg" for tok in doc):
            compound *= -1
    except Exception as e:
        print(f"Error in detailed mood analysis: {e}")
        return simple_mood_analysis(text, tempo, avg_pitch)

    norm_tempo = min(max((tempo - 40) / (200 - 40), 0), 1)
    norm_pitch = min(max((avg_pitch - 50) / (500 - 50), 0), 1)
    norm_sentiment = (compound + 1) / 2

    lower = text.lower()
    if "love" in lower:
        return "love"
    if any(w in lower for w in ["angry", "furious", "rage"]):
        return "angry"
    if any(w in lower for w in ["sad", "cry", "depressed"]):
        return "sad"

    score = 0.3 * norm_tempo + 0.3 * norm_pitch + 0.4 * norm_sentiment
    if compound <= -0.4:
        return "sad"
    if avg_pitch > 250 and tempo > 120:
        return "angry"
    if score >= 0.7:
        return "happy"
    elif score <= 0.3:
        return "sad"
    elif norm_pitch > 0.75 and compound < 0:
        return "angry"
    else:
        return "neutral"

def simple_mood_analysis(text, tempo=0, avg_pitch=0):
    """Fallback mood analysis without heavy ML models"""
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

