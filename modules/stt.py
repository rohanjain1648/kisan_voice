"""Speech-to-Text module using faster-whisper (CPU-optimised, no torch required)."""
import os
import logging

logger = logging.getLogger(__name__)

_model = None
_model_size = os.environ.get("WHISPER_MODEL", "small")  # small >> base for Indian langs

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

# Reverse map for display (lang_code → display name)
_CODE_TO_DISPLAY = {v: k for k, v in LANG_MAP.items()}
_CODE_TO_DISPLAY["ur"] = "हिंदी (Hindi)"  # Urdu shares phonetics — remap to Hindi

# Script-priming prompts — feed the target script so Whisper outputs correct characters.
# Critical for Hindi: without this, Whisper often outputs Urdu/Nastaliq instead of Devanagari.
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


def transcribe(audio_path: str, language: str = "English") -> tuple[str, str, str]:
    """
    Transcribe audio. STT always auto-detects language regardless of UI selection
    (UI language controls LLM response + TTS only).

    Returns:
        (transcript, detected_language_display, error_message)
    """
    if audio_path is None:
        return "", "", "No audio provided."

    model = _load_model()
    if model is None:
        return "", "", "Whisper model unavailable. Run: pip install faster-whisper"

    # IMPORTANT: Always auto-detect spoken language.
    # Forcing the UI language (e.g. "en") onto Indian-language speech produces garbage.
    # The UI dropdown controls LLM/TTS language only.
    #
    # Exception: when user explicitly selects a non-English language, use it as a
    # hint + inject its script as initial_prompt to lock Whisper to the right script.
    lang_code = LANG_MAP.get(language, "en")
    if language == "English":
        # Auto-detect — don't force English when user might be speaking another language
        forced_lang = None
        initial_prompt = ""
    else:
        forced_lang = lang_code
        initial_prompt = INITIAL_PROMPTS.get(lang_code, "")

    try:
        segments, info = model.transcribe(
            audio_path,
            language=forced_lang,
            beam_size=5,          # higher beam = better accuracy
            vad_filter=True,
            initial_prompt=initial_prompt or None,
        )
        text = " ".join(seg.text for seg in segments).strip()

        # Resolve detected language for display
        detected_code = info.language if info else (forced_lang or "en")
        # Urdu (ur) is phonetically identical to Hindi — remap to Hindi
        if detected_code == "ur":
            detected_code = "hi"
        detected_display = _CODE_TO_DISPLAY.get(detected_code, detected_code.upper())

        if not text:
            return "", detected_display, "Could not detect speech. Please speak clearly and try again."
        return text, detected_display, ""
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return "", "", f"Transcription failed: {str(e)}"


def is_available() -> bool:
    try:
        from faster_whisper import WhisperModel  # noqa: F401
        return True
    except ImportError:
        return False
