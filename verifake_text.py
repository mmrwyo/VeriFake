"""Importable preprocessing shared by training and web inference."""
import re

def normalize(text):
    text = str(text).lower()
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    text = re.sub(r"[^a-z\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()

def normalize_batch(texts):
    return [normalize(text) for text in texts]

def news_input(title, body):
    """Use this construction with the exported raw-input Pipeline."""
    return str(title or "") + " " + str(body or "")
