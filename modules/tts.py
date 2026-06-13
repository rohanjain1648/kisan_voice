"""Text-to-Speech module using gTTS."""
import tempfile
import logging
import os

logger = logging.getLogger(__name__)

GTTS_LANG_MAP = {
    "English": "en",
    "हिंदी (Hindi)": "hi",
    "தமிழ் (Tamil)": "ta",
    "తెలుగు (Telugu)": "te",
    "मराठी (Marathi)": "mr",
    "ਪੰਜਾਬੀ (Punjabi)": "pa",
    "বাংলা (Bengali)": "bn",
    "ಕನ್ನಡ (Kannada)": "kn",
    "മലയാളം (Malayalam)": "ml",
    "ગુજરાતી (Gujarati)": "gu",
}

# gTTS has a character limit per request; chunk long texts
_MAX_CHUNK = 500


def _chunk_text(text: str, max_len: int = _MAX_CHUNK) -> list[str]:
    """Split text into sentence-boundary chunks."""
    sentences = text.replace("\n", " ").split(". ")
    chunks, current = [], ""
    for s in sentences:
        candidate = current + s + ". "
        if len(candidate) > max_len and current:
            chunks.append(current.strip())
            current = s + ". "
        else:
            current = candidate
    if current.strip():
        chunks.append(current.strip())
    return chunks or [text[:max_len]]


def synthesize(text: str, language: str = "English") -> tuple[str | None, str]:
    """
    Convert text to speech MP3 file.

    Returns:
        (file_path, error_message) — file_path is None on failure
    """
    if not text or not text.strip():
        return None, "No text to synthesize."

    try:
        from gtts import gTTS
    except ImportError:
        return None, "gTTS not installed. Run: pip install gTTS"

    lang = GTTS_LANG_MAP.get(language, "en")

    # Strip markdown formatting for cleaner speech
    clean_text = _strip_markdown(text)
    # Take first ~400 chars for voice (full text shown in UI)
    speech_text = clean_text[:400] if len(clean_text) > 400 else clean_text

    try:
        tts = gTTS(text=speech_text, lang=lang, slow=False)
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(tmp.name)
        tmp.close()
        return tmp.name, ""
    except Exception as e:
        logger.error(f"TTS error: {e}")
        return None, f"TTS failed: {str(e)}"


def _strip_markdown(text: str) -> str:
    """Remove common markdown so TTS speaks naturally."""
    import re
    text = re.sub(r"#{1,6}\s*", "", text)       # Headers
    text = re.sub(r"\*{1,3}([^*]+)\*{1,3}", r"\1", text)  # Bold/italic
    text = re.sub(r"`[^`]+`", "", text)          # Inline code
    text = re.sub(r"\|[^\n]+\|", "", text)       # Tables
    text = re.sub(r"-{3,}", "", text)             # HR
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)  # Links
    text = re.sub(r"\n{2,}", " ", text)           # Multiple newlines
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()
