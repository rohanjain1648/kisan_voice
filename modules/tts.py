"""Text-to-Speech — edge-tts neural voices (primary) with gTTS fallback."""
import asyncio
import tempfile
import logging

logger = logging.getLogger(__name__)

# Microsoft Edge neural voices — dedicated Indian language voices
EDGE_VOICE_MAP = {
    "English":              "en-IN-NeerjaNeural",
    "हिंदी (Hindi)":       "hi-IN-SwaraNeural",
    "தமிழ் (Tamil)":       "ta-IN-PallaviNeural",
    "తెలుగు (Telugu)":     "te-IN-ShrutiNeural",
    "मराठी (Marathi)":     "mr-IN-AarohiNeural",
    "ਪੰਜਾਬੀ (Punjabi)":   "pa-IN-OjasNeural",
    "বাংলা (Bengali)":     "bn-IN-TanishaaNeural",
    "ಕನ್ನಡ (Kannada)":    "kn-IN-SapnaNeural",
    "മലയാളം (Malayalam)": "ml-IN-SobhanaNeural",
    "ગુજરાતી (Gujarati)":  "gu-IN-DhwaniNeural",
}

# gTTS fallback lang codes
GTTS_LANG_MAP = {
    "English":              "en",
    "हिंदी (Hindi)":       "hi",
    "தமிழ் (Tamil)":       "ta",
    "తెలుగు (Telugu)":     "te",
    "मराठी (Marathi)":     "mr",
    "ਪੰਜਾਬੀ (Punjabi)":   "pa",
    "বাংলা (Bengali)":     "bn",
    "ಕನ್ನಡ (Kannada)":    "kn",
    "മലയാളം (Malayalam)": "ml",
    "ગુજરાતી (Gujarati)":  "gu",
}

_MAX_CHARS = 500


async def _edge_async(text: str, voice: str, path: str) -> None:
    import edge_tts
    await edge_tts.Communicate(text, voice).save(path)


def _synthesize_edge(text: str, language: str) -> tuple[str | None, str]:
    try:
        import edge_tts  # noqa: F401
    except ImportError:
        return None, "edge-tts not installed. Run: pip install edge-tts"

    voice = EDGE_VOICE_MAP.get(language, "en-IN-NeerjaNeural")
    speech = _strip_markdown(text)[:_MAX_CHARS]

    try:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tmp.close()
        # New event loop in caller thread — avoids conflict with Gradio's loop
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(_edge_async(speech, voice, tmp.name))
        finally:
            loop.close()
        return tmp.name, ""
    except Exception as e:
        logger.error(f"edge-tts error: {e}")
        return None, f"edge-tts failed: {str(e)}"


def _synthesize_gtts(text: str, language: str) -> tuple[str | None, str]:
    try:
        from gtts import gTTS
    except ImportError:
        return None, "gTTS not installed"

    lang = GTTS_LANG_MAP.get(language, "en")
    speech = _strip_markdown(text)[:_MAX_CHARS]

    try:
        tts_obj = gTTS(text=speech, lang=lang, slow=False)
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts_obj.save(tmp.name)
        tmp.close()
        return tmp.name, ""
    except Exception as e:
        logger.error(f"gTTS error: {e}")
        return None, f"gTTS failed: {str(e)}"


def synthesize(text: str, language: str = "English") -> tuple[str | None, str]:
    """Convert text to speech MP3. Returns (file_path, error_message)."""
    if not text or not text.strip():
        return None, "No text to synthesize."

    # Try edge-tts first — neural quality, proper Indian language pronunciation
    path, err = _synthesize_edge(text, language)
    if path:
        return path, ""

    # Fallback to gTTS
    logger.warning(f"edge-tts unavailable ({err}), falling back to gTTS")
    return _synthesize_gtts(text, language)


def _strip_markdown(text: str) -> str:
    import re
    text = re.sub(r"#{1,6}\s*", "", text)
    text = re.sub(r"\*{1,3}([^*]+)\*{1,3}", r"\1", text)
    text = re.sub(r"`[^`]+`", "", text)
    text = re.sub(r"\|[^\n]+\|", "", text)
    text = re.sub(r"-{3,}", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    text = re.sub(r"\n{2,}", " ", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


def is_available() -> bool:
    try:
        import edge_tts  # noqa: F401
        return True
    except ImportError:
        pass
    try:
        from gtts import gTTS  # noqa: F401
        return True
    except ImportError:
        return False
