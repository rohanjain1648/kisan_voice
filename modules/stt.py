"""Speech-to-Text module using faster-whisper (CPU-optimised, no torch required)."""
import os
import logging

logger = logging.getLogger(__name__)

_model = None
_model_size = os.environ.get("WHISPER_MODEL", "base")

LANG_MAP = {
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

# Script-priming prompts — force Whisper to output the correct script.
# Hindi and Urdu share phonetics; without this Whisper often picks Urdu
# and transcribes in Nastaliq script instead of Devanagari.
INITIAL_PROMPTS = {
    "hi": "यह हिंदी में एक कृषि प्रश्न है।",
    "mr": "हे मराठी भाषेतील कृषी प्रश्न आहे।",
    "ta": "இது தமிழில் ஒரு விவசாய கேள்வி.",
    "te": "ఇది తెలుగులో వ్యవసాయ ప్రశ్న.",
    "bn": "এটি বাংলায় একটি কৃষি প্রশ্ন।",
    "pa": "ਇਹ ਪੰਜਾਬੀ ਵਿੱਚ ਇੱਕ ਖੇਤੀ ਸਵਾਲ ਹੈ।",
    "kn": "ಇದು ಕನ್ನಡದಲ್ಲಿ ಕೃಷಿ ಪ್ರಶ್ನೆ.",
    "ml": "ഇത് മലയാളത്തിൽ ഒരു കൃഷി ചോദ്യം.",
    "gu": "આ ગુજરાતીમાં એક ખેતી પ્રશ્ન છે.",
    "en": "This is a natural farming question in English.",
}


def _load_model():
    global _model
    if _model is None:
        try:
            from faster_whisper import WhisperModel
            logger.info(f"Loading faster-whisper model: {_model_size}")
            _model = WhisperModel(_model_size, device="cpu", compute_type="int8")
            logger.info("faster-whisper model loaded")
        except ImportError:
            logger.error("faster-whisper not installed. Run: pip install faster-whisper")
        except Exception as e:
            logger.error(f"Failed to load faster-whisper model: {e}")
    return _model


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
        return "", "Whisper model unavailable. Run: pip install faster-whisper"

    lang_code = LANG_MAP.get(language, "en")
    initial_prompt = INITIAL_PROMPTS.get(lang_code, "")

    try:
        segments, _ = model.transcribe(
            audio_path,
            language=lang_code,
            beam_size=3,
            vad_filter=True,
            initial_prompt=initial_prompt,
        )
        text = " ".join(seg.text for seg in segments).strip()
        if not text:
            return "", "Could not detect speech. Please speak clearly and try again."
        return text, ""
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return "", f"Transcription failed: {str(e)}"


def is_available() -> bool:
    try:
        from faster_whisper import WhisperModel  # noqa: F401
        return True
    except ImportError:
        return False
