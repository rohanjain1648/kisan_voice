"""Speech-to-Text module using OpenAI Whisper."""
import os
import logging

logger = logging.getLogger(__name__)

_model = None
_model_size = os.environ.get("WHISPER_MODEL", "base")


def _load_model():
    global _model
    if _model is None:
        try:
            import whisper
            logger.info(f"Loading Whisper model: {_model_size}")
            _model = whisper.load_model(_model_size)
            logger.info("Whisper model loaded successfully")
        except ImportError:
            logger.error("openai-whisper not installed. Run: pip install openai-whisper")
            return None
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            return None
    return _model


LANG_MAP = {
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


def transcribe(audio_path: str, language: str = "English") -> tuple[str, str]:
    """
    Transcribe audio file to text.

    Returns:
        (transcript, error_message) — error_message is empty string on success
    """
    if audio_path is None:
        return "", "No audio provided."

    model = _load_model()
    if model is None:
        return "", "Whisper model unavailable. Check installation."

    try:
        lang_code = LANG_MAP.get(language, "en")
        options = {"language": lang_code, "task": "transcribe"}

        import whisper
        result = model.transcribe(audio_path, **options)
        text = result.get("text", "").strip()

        if not text:
            return "", "Could not detect speech. Please speak clearly and try again."

        return text, ""

    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return "", f"Transcription failed: {str(e)}"


def is_available() -> bool:
    try:
        import whisper  # noqa: F401
        return True
    except ImportError:
        return False
