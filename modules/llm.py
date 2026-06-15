"""LLM module — Groq integration with farming-optimized system prompt and guardrails."""
import os
import logging
import groq

logger = logging.getLogger(__name__)

# Text model — fastest + most capable on Groq free tier
TEXT_MODEL = "llama-3.3-70b-versatile"
# Vision model for crop disease photo analysis
VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

SYSTEM_PROMPT = """You are **KisanVoice** (किसान वॉयस), a compassionate expert in Zero Budget Natural Farming (ZBNF) and multilevel agroforestry, serving small and marginal farmers across India.

## Core Expertise
1. **Disease Identification & Organic Treatment**: Diagnose crop diseases from symptom descriptions or images; prescribe chemical-free remedies using neem, cow products, herbs, and microbial inoculants.
2. **Weather-Based Farming Guidance**: Interpret temperature, rainfall, and humidity data; recommend specific sowing, irrigation, harvesting, and protective actions.
3. **Market Intelligence**: Analyze mandi prices vs. MSP; suggest optimal timing, markets (physical/eNAM), and value-addition strategies.
4. **Zero Budget Natural Farming (ZBNF)**: Explain and prescribe Jeevamrut, Beejamrut, Panchagavya, Dashparni Ark, mulching, and moisture management techniques.
5. **Multilevel Cropping**: Design 4-5 layer companion cropping systems tailored to farmer's land, climate, and financial goals.
6. **Government Schemes**: PM-KISAN, PKVY, Fasal Bima, KCC, NMSA, eNAM — eligibility, benefits, application process.

## Voice-Optimized Response Rules
- **Brevity**: Keep responses under 180 words (voice output). If complex, give the key action first, details second.
- **Numbered steps**: Use 1-2-3 format for treatments and instructions.
- **Local materials**: ALWAYS suggest cheap, locally available ingredients (cow dung, neem, jaggery, etc.).
- **Affirm then advise**: Start with an empathetic acknowledgment ("Good question, Kisan-ji...").
- **Safety net**: For severe outbreaks or undiagnosed issues, recommend visiting Krishi Vigyan Kendra (KVK) or calling Kisan Call Center 1800-180-1551.

## Strict Guardrails
- Respond ONLY to agriculture, farming, livestock, rural livelihood, and related government scheme questions.
- If asked about non-farming topics, politely redirect: "I'm specialized in natural farming. For [topic], please consult the relevant expert."
- NEVER recommend synthetic pesticides or chemical fertilizers as primary solutions. Organic first, always.
- NEVER hallucinate MSP or scheme amounts — if uncertain, say "verify at official portal" and give the URL.
- Do NOT provide medical advice for humans or prescribe veterinary drugs.

## Language
- Detect the farmer's language from their query and respond in SAME language.
- For Hindi queries, use simple Hindi mixed with common farming terms.
- If language instruction is provided, strictly follow it.
- Use words farmers understand; avoid jargon."""

DEMO_RESPONSES = {
    "default": (
        "🌿 **KisanVoice Demo Mode** (API key not configured)\n\n"
        "To enable full AI responses, add your GROQ_API_KEY to the .env file.\n\n"
        "**Sample Answer**: For organic farming questions, I recommend starting with Jeevamrut — "
        "mix 10kg cow dung + 10L cow urine + 2kg jaggery + 2kg gram flour in 200L water, "
        "ferment 7 days, and apply 200L per acre every 15 days. This activates soil microbes "
        "and provides balanced nutrition naturally. 🌾"
    ),
    "disease": (
        "🔬 **Demo Disease Diagnosis**\n\n"
        "Based on typical symptoms described, this could be **Leaf Blight**.\n\n"
        "**Organic Treatment**:\n"
        "1. Spray 3% neem oil solution (3ml/L water + 2ml soap) twice weekly\n"
        "2. Drench soil with Trichoderma viride (5g/L water)\n"
        "3. Apply Jeevamrut as soil drench every 2 weeks\n"
        "4. Remove infected leaves and compost away from field\n\n"
        "*Add GROQ_API_KEY for accurate AI diagnosis*"
    ),
    "weather": (
        "🌦️ **Demo Weather Advice**\n\n"
        "Based on current weather conditions:\n"
        "- **Today**: Good for foliar spray in early morning before heat\n"
        "- **This week**: If rain forecast >10mm, hold off on top-dressing\n"
        "- **Irrigation**: Check soil moisture at 6-inch depth before watering\n\n"
        "*Add GROQ_API_KEY for personalized weather-based advice*"
    ),
}


def _get_client() -> groq.Groq | None:
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key or api_key == "your_groq_api_key_here":
        return None
    try:
        return groq.Groq(api_key=api_key)
    except Exception as e:
        logger.error(f"Failed to create Groq client: {e}")
        return None


def query(
    user_message: str,
    rag_context: str = "",
    language: str = "English",
    image_b64: str | None = None,
    demo_type: str = "default",
) -> tuple[str, str]:
    """
    Query Groq LLM for farming advice.

    Returns:
        (response_text, error_message)
    """
    client = _get_client()
    if client is None:
        return DEMO_RESPONSES.get(demo_type, DEMO_RESPONSES["default"]), ""

    lang_note = ""
    if language != "English":
        lang_note = f"\n\nLanguage instruction: Respond entirely in {language}."

    system = SYSTEM_PROMPT + lang_note

    user_text = user_message
    if rag_context:
        user_text = f"[Relevant Knowledge]\n{rag_context}\n\n[Farmer's Query]\n{user_message}"

    # Build user message content — use vision model when image is provided
    if image_b64:
        model = VISION_MODEL
        content = [
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"},
            },
            {"type": "text", "text": user_text},
        ]
    else:
        model = TEXT_MODEL
        content = user_text

    try:
        response = client.chat.completions.create(
            model=model,
            max_tokens=450,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": content},
            ],
        )
        return response.choices[0].message.content, ""
    except groq.AuthenticationError:
        return "", "Invalid API key. Please check your GROQ_API_KEY in .env file."
    except groq.RateLimitError:
        return "", "Rate limit reached. Please wait a moment and try again."
    except Exception as e:
        logger.error(f"LLM query error: {e}")
        return "", f"LLM error: {str(e)}"


def is_configured() -> bool:
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    return bool(api_key) and api_key != "your_groq_api_key_here"
