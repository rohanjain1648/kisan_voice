"""
KisanVoice — Voice-Based Natural Farming Consultant
Features: Disease Identification · Seed & Financial Guidance · Weather & Market · Natural Farming Education
Tech: Gradio · Whisper STT · gTTS · Groq LLM · Open-Meteo
"""
import os
import io
import base64
import logging
import tempfile
from dotenv import load_dotenv

load_dotenv()

import gradio as gr

from modules import stt, tts, llm, weather as weather_mod, market as market_mod, knowledge
from modules import seeds as seeds_mod, education as edu_mod

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────
# CONSTANTS
# ──────────────────────────────────────────────────────────────

LANGUAGES = [
    "English",
    "हिंदी (Hindi)",
    "தமிழ் (Tamil)",
    "తెలుగు (Telugu)",
    "मराठी (Marathi)",
    "ਪੰਜਾਬੀ (Punjabi)",
    "বাংলা (Bengali)",
    "ಕನ್ನಡ (Kannada)",
    "മലയാളം (Malayalam)",
    "ગુજરાતી (Gujarati)",
]

EXAMPLE_QUESTIONS = [
    ("🍃 Yellow spots on tomato?", "My tomato leaves have yellow spots with brown edges and the plant is wilting. What disease is this and how can I treat it organically?"),
    ("🌱 How to make Jeevamrut?", "How do I prepare Jeevamrut and when should I apply it to my crops?"),
    ("🌾 Multilevel farming?", "Explain multilevel farming with all 5 layers. What crops should I grow on 1 acre?"),
    ("💰 PM-KISAN scheme?", "Tell me about PM-KISAN scheme — how much money, who is eligible, and how to apply?"),
    ("🐛 Aphids on cotton?", "I see small black insects on my cotton leaves and the leaves are getting sticky. How to control them without chemicals?"),
    ("🌿 Dashparni Ark recipe?", "How to make Dashparni Ark and which plants do I need?"),
]

CSS = """
/* ─── Global ─── */
.gradio-container { max-width: 960px !important; margin: 0 auto; }
body { font-family: 'Segoe UI', 'Noto Sans', sans-serif; }

/* ─── Header ─── */
#kisan-header {
    background: linear-gradient(135deg, #1b4332 0%, #2d6a4f 50%, #52b788 100%);
    color: white;
    padding: 24px 20px;
    border-radius: 14px;
    text-align: center;
    margin-bottom: 18px;
    box-shadow: 0 4px 20px rgba(45,106,79,0.3);
}
#kisan-header h1 { font-size: 2rem; margin: 0 0 6px; letter-spacing: 1px; }
#kisan-header p { margin: 4px 0; opacity: 0.9; font-size: 0.95rem; }

/* ─── Status badges ─── */
.api-ok { background:#d1fae5; color:#065f46; padding:6px 12px; border-radius:20px; font-size:0.85rem; font-weight:600; }
.api-warn { background:#fef3c7; color:#92400e; padding:6px 12px; border-radius:20px; font-size:0.85rem; font-weight:600; }

/* ─── Tabs ─── */
.tab-nav button { font-size: 1rem !important; padding: 10px 16px !important; }

/* ─── Chat ─── */
.chatbot-wrap { border-radius:12px; border:2px solid #52b788 !important; }

/* ─── Voice button ─── */
#voice-btn { background: #2d6a4f !important; font-size:1.05rem !important; border-radius:10px !important; }
#voice-btn:hover { background: #1b4332 !important; }

/* ─── Price table ─── */
.price-table { font-size:0.88rem; }

/* ─── Tip box ─── */
.tip-box {
    background: #f0fdf4;
    border-left: 4px solid #52b788;
    padding: 10px 14px;
    border-radius: 0 8px 8px 0;
    margin: 8px 0;
    font-size: 0.9rem;
}
"""

# ──────────────────────────────────────────────────────────────
# PIPELINE FUNCTIONS
# ──────────────────────────────────────────────────────────────

def _transcribe(audio_path, language):
    if audio_path is None:
        return "", "⚠️ No audio recorded."
    text, err = stt.transcribe(audio_path, language)
    if err:
        return "", f"⚠️ {err}"
    return text, f"✅ Heard: \"{text}\""


def _respond(user_text: str, language: str, rag_context: str = "", demo_type="default", image_b64=None):
    if not user_text.strip():
        return "", "Please provide a question.", None

    response, err = llm.query(
        user_message=user_text,
        rag_context=rag_context,
        language=language,
        image_b64=image_b64,
        demo_type=demo_type,
    )
    if err:
        return "", f"⚠️ {err}", None

    audio_path, _ = tts.synthesize(response, language)
    return response, "", audio_path


def _pil_to_b64(img) -> str | None:
    if img is None:
        return None
    if isinstance(img, str):
        with open(img, "rb") as f:
            return base64.b64encode(f.read()).decode()
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode()


# ──────────────────────────────────────────────────────────────
# EVENT HANDLERS
# ──────────────────────────────────────────────────────────────

def handle_voice_query(audio, language, history):
    text, status = _transcribe(audio, language)
    if not text:
        return history, status, None
    context = knowledge.get_context(text)
    response, err, audio_out = _respond(text, language, context)
    if err:
        return history, err, None
    history = history + [{"role": "user", "content": text}, {"role": "assistant", "content": response}]
    return history, status, audio_out


def handle_text_query(text, language, history):
    if not text.strip():
        return history, None
    context = knowledge.get_context(text)
    response, _, audio_out = _respond(text, language, context)
    history = history + [{"role": "user", "content": text}, {"role": "assistant", "content": response}]
    return history, audio_out


def handle_disease_query(audio, symptoms_text, image, language):
    # 1. STT if audio provided
    final_text = symptoms_text.strip()
    status_msg = ""
    if audio is not None:
        transcribed, err = stt.transcribe(audio, language)
        if transcribed:
            final_text = transcribed
            status_msg = f"🎤 Heard: \"{transcribed}\""

    if not final_text and image is None:
        return "Please describe symptoms or upload a photo.", "", None

    image_b64 = _pil_to_b64(image)
    context = knowledge.get_context(final_text) if final_text else ""

    query_text = final_text or "Please identify the crop disease in the image and suggest organic treatment."
    response, err, audio_out = _respond(
        query_text, language, context, demo_type="disease", image_b64=image_b64
    )
    if err:
        return f"⚠️ {err}", status_msg, None
    return response, status_msg, audio_out


def handle_weather_market(location, crop, language):
    weather_md = ""
    market_md = ""
    farming_advice = ""

    if location.strip():
        w = weather_mod.get_weather(location)
        weather_md = weather_mod.format_weather_markdown(w)
        weather_context = weather_mod.get_weather_summary_for_llm(w)

        advice_query = (
            "Based on these weather conditions, what specific farming activities should I do today and this week? "
            "Include advice on irrigation, spraying, harvesting, and field preparation."
        )
        farming_advice, _, _ = _respond(
            advice_query, language, f"[Weather Data]\n{weather_context}", demo_type="weather"
        )

    if crop:
        market_md = market_mod.format_market_card(crop)
        # Add market context to LLM for selling advice
        market_context = market_mod.get_market_summary_for_llm(crop)
        sell_query = f"Should I sell my {crop} crop now or wait? What is the best strategy?"
        sell_advice, _, _ = _respond(sell_query, language, market_context)
        market_md += f"\n\n### 🤖 AI Selling Advice\n{sell_advice}"

    return weather_md, market_md, farming_advice


def refresh_prices():
    return market_mod.get_all_prices_table()


def handle_seed_guidance(audio, crop, state, acres_str, language):
    acres = 1.0
    try:
        acres = max(0.25, min(float(acres_str or "1"), 100))
    except (ValueError, TypeError):
        pass

    # Voice → override crop if transcribed
    voice_note = ""
    if audio is not None:
        transcribed, _ = stt.transcribe(audio, language)
        if transcribed:
            voice_note = transcribed
            # try to extract crop name from voice
            for c in seeds_mod.crop_list():
                if c in transcribed.lower():
                    crop = c
                    break

    planting_card = seeds_mod.get_planting_card(crop)
    financial_card = seeds_mod.get_financial_card(crop, acres)
    varieties_table = seeds_mod.get_varieties_table(crop)
    subsidies_card = seeds_mod.get_subsidies_card(state)

    # AI advice
    seed_context = seeds_mod.get_seed_context_for_llm(crop, state)
    query = voice_note or f"Give me complete planting advice for {crop} in {state}. When to sow, which variety, how much water, and what organic inputs to use?"
    ai_advice, _, audio_out = _respond(query, language, seed_context, demo_type="default")

    return planting_card, financial_card, varieties_table, subsidies_card, ai_advice, audio_out


def handle_education_query(audio, text_query, topic_label, language):
    # Resolve topic key from label
    topic_key = ""
    if topic_label:
        for k, v in edu_mod.TOPICS.items():
            if v["title"] in topic_label or topic_label in v["title"]:
                topic_key = k
                break

    # Voice input
    final_query = text_query.strip()
    if audio is not None:
        transcribed, _ = stt.transcribe(audio, language)
        if transcribed:
            final_query = transcribed
            if not topic_key:
                matched = edu_mod.search_topics(transcribed)
                if matched:
                    topic_key = matched[0]

    # Topic content for display
    topic_content = edu_mod.get_topic_content(topic_key) if topic_key else ""

    # Build query for LLM
    if not final_query and topic_key:
        topic = edu_mod.get_topic(topic_key)
        final_query = f"Explain {topic['title']} in simple terms for a farmer. Give practical steps and examples."

    if not final_query:
        return topic_content, "Please select a topic or ask a question.", None

    rag_context = edu_mod.get_context_for_llm(topic_key) if topic_key else knowledge.get_context(final_query)
    ai_response, _, audio_out = _respond(final_query, language, rag_context)

    return topic_content, ai_response, audio_out


# ──────────────────────────────────────────────────────────────
# UI BUILD
# ──────────────────────────────────────────────────────────────

def build_app() -> gr.Blocks:
    api_status_html = (
        '<span class="api-ok">✅ Groq AI Connected</span>'
        if llm.is_configured()
        else '<span class="api-warn">⚠️ Demo Mode — Add GROQ_API_KEY in .env</span>'
    )
    stt_status = "✅ Whisper STT Ready" if stt.is_available() else "⚠️ Whisper not installed — text input only"

    with gr.Blocks(title="KisanVoice 🌾 Natural Farming Consultant") as app:

        # ── Header ────────────────────────────────────────────
        gr.HTML(f"""
        <div id="kisan-header">
            <h1>🌾 KisanVoice — किसान वॉयस</h1>
            <p>Voice-First AI Natural Farming Consultant · Zero Budget Natural Farming (ZBNF)</p>
            <p>Multilevel Agroforestry Expert · Available in 10 Languages</p>
            <p style="margin-top:10px;">{api_status_html} &nbsp; | &nbsp; {stt_status}</p>
        </div>
        """)

        # ── Language selector (global) ─────────────────────────
        with gr.Row():
            lang_dd = gr.Dropdown(
                choices=LANGUAGES, value="English",
                label="🌐 Language / भाषा चुनें",
                scale=2,
            )
            gr.HTML("""
            <div class="tip-box" style="margin:auto 0;">
                <strong>Quick Start:</strong>
                Select language → Click 🎤 to record → Get expert advice instantly
            </div>
            """)

        # ══════════════════════════════════════════════════════
        with gr.Tabs():

            # ── TAB 1: VOICE CONSULTANT ────────────────────────
            with gr.Tab("🎙️ Voice Consultant"):
                gr.Markdown("### Ask Any Natural Farming Question — by Voice or Text")

                with gr.Row(equal_height=False):
                    # Left column — Input
                    with gr.Column(scale=1, min_width=280):
                        audio_in = gr.Audio(
                            sources=["microphone", "upload"],
                            type="filepath",
                            label="🎤 Record Your Question",
                        )
                        voice_btn = gr.Button(
                            "🎙️ Process Voice Query", variant="primary",
                            size="lg", elem_id="voice-btn",
                        )
                        status_box = gr.Textbox(
                            label="📝 Transcription", interactive=False, lines=2,
                        )
                        gr.Markdown("**— or type your question —**")
                        text_in = gr.Textbox(
                            placeholder="e.g., My paddy leaves show brown spots...",
                            label="💬 Text Question", lines=3,
                        )
                        text_btn = gr.Button("💬 Submit Question", variant="secondary")
                        clear_btn = gr.Button("🗑️ Clear Chat", size="sm")

                    # Right column — Chat output
                    with gr.Column(scale=2):
                        chatbot = gr.Chatbot(
                            label="🌿 KisanVoice AI Responses",
                            height=420,
                            elem_classes=["chatbot-wrap"],
                        )
                        audio_out = gr.Audio(
                            label="🔊 Voice Response",
                            autoplay=True, interactive=False,
                        )

                # Example questions
                gr.Markdown("#### 💡 Quick Examples:")
                ex_row1 = gr.Row()
                ex_buttons = []
                with ex_row1:
                    for label, _ in EXAMPLE_QUESTIONS[:3]:
                        b = gr.Button(label, size="sm")
                        ex_buttons.append(b)
                ex_row2 = gr.Row()
                with ex_row2:
                    for label, _ in EXAMPLE_QUESTIONS[3:]:
                        b = gr.Button(label, size="sm")
                        ex_buttons.append(b)

                # State
                chat_state = gr.State([])

                # Events
                voice_btn.click(
                    handle_voice_query,
                    inputs=[audio_in, lang_dd, chat_state],
                    outputs=[chat_state, status_box, audio_out],
                ).then(lambda h: h, chat_state, chatbot)

                text_btn.click(
                    handle_text_query,
                    inputs=[text_in, lang_dd, chat_state],
                    outputs=[chat_state, audio_out],
                ).then(lambda h: h, chat_state, chatbot)

                text_in.submit(
                    handle_text_query,
                    inputs=[text_in, lang_dd, chat_state],
                    outputs=[chat_state, audio_out],
                ).then(lambda h: h, chat_state, chatbot)

                clear_btn.click(
                    lambda: ([], [], ""),
                    outputs=[chat_state, chatbot, status_box],
                )

                # Wire example buttons
                for btn, (_, question) in zip(ex_buttons, EXAMPLE_QUESTIONS):
                    btn.click(lambda q=question: q, outputs=text_in).then(
                        handle_text_query,
                        inputs=[text_in, lang_dd, chat_state],
                        outputs=[chat_state, audio_out],
                    ).then(lambda h: h, chat_state, chatbot)

            # ── TAB 2: DISEASE IDENTIFIER ──────────────────────
            with gr.Tab("🔬 Disease Identifier"):
                gr.Markdown("""
                ### Crop Disease Diagnosis & Organic Treatment
                *Describe symptoms by voice or text. Optionally upload a photo for visual diagnosis.*
                """)

                with gr.Row(equal_height=False):
                    with gr.Column(scale=1):
                        disease_audio = gr.Audio(
                            sources=["microphone"], type="filepath",
                            label="🎤 Describe Symptoms by Voice",
                        )
                        disease_symptoms = gr.Textbox(
                            label="🌿 Describe Symptoms (or use voice above)",
                            placeholder=(
                                "e.g., Rice leaves showing yellow-brown patches with water-soaked "
                                "edges, plant wilting in hot afternoon..."
                            ),
                            lines=4,
                        )
                        disease_image = gr.Image(
                            label="📷 Upload Crop Photo (optional — for visual diagnosis)",
                            type="pil",
                            sources=["upload", "webcam"],
                        )
                        disease_btn = gr.Button(
                            "🔍 Diagnose & Get Organic Treatment",
                            variant="primary", size="lg",
                        )
                        disease_status = gr.Textbox(
                            label="Status", interactive=False, lines=1,
                        )

                        # Common disease shortcuts
                        gr.Markdown("**Common Issues (click to fill):**")
                        with gr.Row():
                            d1 = gr.Button("🟡 Yellow/Brown Leaves", size="sm")
                            d2 = gr.Button("🤍 White Powder", size="sm")
                        with gr.Row():
                            d3 = gr.Button("🐛 Pest Damage", size="sm")
                            d4 = gr.Button("💀 Wilting / Root Rot", size="sm")
                        with gr.Row():
                            d5 = gr.Button("🕷️ Mite / Webbing", size="sm")
                            d6 = gr.Button("🌿 Stem Borer", size="sm")

                    with gr.Column(scale=2):
                        disease_result = gr.Markdown(
                            value="*Diagnosis and organic treatment will appear here...*",
                            label="🏥 AI Diagnosis & Treatment Plan",
                        )
                        disease_audio_out = gr.Audio(
                            label="🔊 Listen to Treatment Guide",
                            autoplay=True, interactive=False,
                        )

                disease_btn.click(
                    handle_disease_query,
                    inputs=[disease_audio, disease_symptoms, disease_image, lang_dd],
                    outputs=[disease_result, disease_status, disease_audio_out],
                )

                DISEASE_PROMPTS = {
                    d1: "Leaves showing yellow patches and brown edges. Some leaves are drying up. Plant looks stressed.",
                    d2: "White powdery coating on leaves and stems. New growth is stunted and curled.",
                    d3: "Small holes in leaves, sticky residue, insects visible on underside of leaves.",
                    d4: "Plant suddenly wilting despite watering. Roots look dark and mushy when I pull out the plant.",
                    d5: "Very fine webbing on undersides of leaves. Tiny mites visible. Leaves turning bronze/silver.",
                    d6: "Central shoot of plant has died (dead heart). Hollow stems. Saw white larvae inside stem.",
                }
                for btn, prompt in DISEASE_PROMPTS.items():
                    btn.click(lambda p=prompt: p, outputs=disease_symptoms)

            # ── TAB 3: WEATHER & MARKET ────────────────────────
            with gr.Tab("🌦️ Weather & Market"):
                gr.Markdown("""
                ### Real-Time Weather + Mandi Market Intelligence
                *Get weather-based farming advice and today's crop prices for smart selling decisions.*
                """)

                with gr.Row():
                    loc_in = gr.Textbox(
                        label="📍 Your Location (village / district / city)",
                        placeholder="e.g., Pune, Warangal, Ludhiana",
                        scale=2,
                    )
                    crop_dd = gr.Dropdown(
                        choices=market_mod.crop_list(),
                        value="wheat",
                        label="🌾 Select Crop for Price Analysis",
                        scale=1,
                    )
                    wm_btn = gr.Button("🔍 Fetch Weather & Prices", variant="primary", scale=1)

                with gr.Row(equal_height=False):
                    with gr.Column():
                        weather_out = gr.Markdown(
                            value="*Enter your location and click Fetch...*",
                            label="🌤️ Weather Report & Farming Alerts",
                        )
                    with gr.Column():
                        market_out = gr.Markdown(
                            value="*Select a crop and click Fetch...*",
                            label="💰 Market Intelligence",
                        )

                farming_advice_out = gr.Textbox(
                    label="🌿 AI Farming Advice (based on today's weather)",
                    lines=6, interactive=False,
                )

                wm_btn.click(
                    handle_weather_market,
                    inputs=[loc_in, crop_dd, lang_dd],
                    outputs=[weather_out, market_out, farming_advice_out],
                )

                # ── All prices table ────────────────────────────
                gr.Markdown("---")
                gr.Markdown("### 📊 Today's Mandi Rates — All Crops")
                price_table = gr.DataFrame(
                    value=market_mod.get_all_prices_table(),
                    headers=["Crop", "Market Price", "MSP", "vs MSP", "Trend", "Best Market"],
                    label="Live Mandi Prices",
                    interactive=False,
                    elem_classes=["price-table"],
                )
                with gr.Row():
                    refresh_btn = gr.Button("🔄 Refresh Prices", size="sm")
                    gr.HTML("""
                    <div class="tip-box">
                        💡 <strong>Tip</strong>: When market price is below MSP,
                        sell through NAFED / state procurement to get guaranteed MSP.
                        Register on <strong>eNAM</strong> for transparent pan-India price discovery.
                    </div>
                    """)

                refresh_btn.click(refresh_prices, outputs=price_table)

            # ── TAB 4: SEED & FINANCIAL GUIDANCE ──────────────
            with gr.Tab("🌱 Seed & Finance"):
                gr.Markdown("### Seed Selection · Planting Guide · Cost-Benefit · Government Subsidies")

                with gr.Row():
                    seed_audio = gr.Audio(
                        sources=["microphone"], type="filepath",
                        label="🎤 Ask by voice (e.g. 'Best wheat variety in Punjab')",
                        scale=2,
                    )
                    seed_crop_dd = gr.Dropdown(
                        choices=seeds_mod.crop_list(), value="wheat",
                        label="🌾 Crop", scale=1,
                    )
                    seed_state_dd = gr.Dropdown(
                        choices=list(seeds_mod.STATE_SCHEMES.keys()), value="Punjab",
                        label="📍 State", scale=1,
                    )
                    seed_acres = gr.Number(value=1.0, label="Acres", minimum=0.25, maximum=100, scale=1)
                    seed_btn = gr.Button("🔍 Get Guidance", variant="primary", scale=1)

                with gr.Row(equal_height=False):
                    with gr.Column():
                        seed_planting_out = gr.Markdown(
                            value="*Select crop and click Get Guidance...*",
                            label="🌱 Planting Guide",
                        )
                    with gr.Column():
                        seed_finance_out = gr.Markdown(
                            value="*Financial analysis will appear here...*",
                            label="💰 Cost-Benefit Analysis",
                        )

                seed_varieties_table = gr.DataFrame(
                    headers=["Variety", "Yield", "Duration", "Strengths", "Best States"],
                    label="🌾 Recommended Seed Varieties",
                    interactive=False,
                )

                with gr.Row(equal_height=False):
                    with gr.Column():
                        seed_subsidies_out = gr.Markdown(label="🏛️ Subsidies & Schemes")
                    with gr.Column():
                        seed_ai_out = gr.Textbox(
                            label="🤖 AI Planting Advice", lines=6, interactive=False,
                        )
                        seed_audio_out = gr.Audio(
                            label="🔊 Listen", autoplay=True, interactive=False,
                        )

                seed_btn.click(
                    handle_seed_guidance,
                    inputs=[seed_audio, seed_crop_dd, seed_state_dd, seed_acres, lang_dd],
                    outputs=[seed_planting_out, seed_finance_out, seed_varieties_table,
                             seed_subsidies_out, seed_ai_out, seed_audio_out],
                )

                # Quick crop shortcuts
                gr.Markdown("**Quick select:**")
                with gr.Row():
                    for crop_name in ["wheat", "rice", "tomato", "cotton", "turmeric", "maize"]:
                        gr.Button(f"🌾 {crop_name.title()}", size="sm").click(
                            lambda c=crop_name: c, outputs=seed_crop_dd
                        )

            # ── TAB 5: NATURAL FARMING EDUCATION ──────────────
            with gr.Tab("📖 Education"):
                gr.Markdown("### Natural Farming Education — Learn ZBNF, Multilevel Farming & More")

                with gr.Row():
                    edu_topic_dd = gr.Dropdown(
                        choices=edu_mod.topic_labels(),
                        value=edu_mod.topic_labels()[0],
                        label="📚 Select Topic",
                        scale=3,
                    )
                    edu_path_dd = gr.Dropdown(
                        choices=[v["label"] for v in edu_mod.LEARNING_PATHS.values()],
                        value=list(edu_mod.LEARNING_PATHS.values())[0]["label"],
                        label="🎯 Learning Path",
                        scale=2,
                    )

                with gr.Row():
                    edu_audio_in = gr.Audio(
                        sources=["microphone"], type="filepath",
                        label="🎤 Ask anything about natural farming",
                        scale=2,
                    )
                    edu_text_in = gr.Textbox(
                        placeholder="e.g., How do I design a multilevel farm on 2 acres?",
                        label="💬 Or type your question",
                        lines=2, scale=3,
                    )
                    edu_ask_btn = gr.Button("💡 Ask & Learn", variant="primary", scale=1)

                with gr.Row(equal_height=False):
                    with gr.Column(scale=2):
                        edu_content_out = gr.Markdown(
                            value="*Select a topic above to read the full guide...*",
                            label="📖 Topic Guide",
                        )
                    with gr.Column(scale=1):
                        edu_ai_out = gr.Textbox(
                            label="🤖 AI Explanation (voice-optimised)", lines=10, interactive=False,
                        )
                        edu_audio_out = gr.Audio(
                            label="🔊 Listen", autoplay=True, interactive=False,
                        )

                # Topic quick-launch buttons
                gr.Markdown("**Jump to topic:**")
                topic_rows = [edu_mod.topic_labels()[i:i+4] for i in range(0, len(edu_mod.topic_labels()), 4)]
                for row_labels in topic_rows:
                    with gr.Row():
                        for label in row_labels:
                            gr.Button(label, size="sm").click(lambda l=label: l, outputs=edu_topic_dd)

                # Load topic content when dropdown changes
                def load_topic(label):
                    topic = edu_mod.get_topic_by_label(label)
                    return topic["content"] if topic else "*Topic not found.*"

                edu_topic_dd.change(load_topic, inputs=edu_topic_dd, outputs=edu_content_out)

                # Load learning path description
                def load_path(label):
                    for v in edu_mod.LEARNING_PATHS.values():
                        if v["label"] == label:
                            topics = " → ".join(
                                edu_mod.TOPICS[k]["icon"] + " " + edu_mod.TOPICS[k]["title"]
                                for k in v["steps"] if k in edu_mod.TOPICS
                            )
                            return f"**{v['description']}**\n\nLearning sequence: {topics}"
                    return ""

                path_info = gr.Markdown()
                edu_path_dd.change(load_path, inputs=edu_path_dd, outputs=path_info)

                edu_ask_btn.click(
                    handle_education_query,
                    inputs=[edu_audio_in, edu_text_in, edu_topic_dd, lang_dd],
                    outputs=[edu_content_out, edu_ai_out, edu_audio_out],
                )
                edu_text_in.submit(
                    handle_education_query,
                    inputs=[edu_audio_in, edu_text_in, edu_topic_dd, lang_dd],
                    outputs=[edu_content_out, edu_ai_out, edu_audio_out],
                )

            # ── TAB 6: KNOWLEDGE BASE ──────────────────────────
            with gr.Tab("📚 Knowledge Base"):
                gr.Markdown("### Natural Farming Quick Reference")

                with gr.Accordion("🌿 Organic Remedies & Recipes", open=True):
                    with gr.Row():
                        with gr.Column():
                            gr.Markdown("""
**Jeevamrut (जीवामृत)** — Microbial activator
- 200L water + 10kg cow dung + 10L cow urine
- 2kg jaggery + 2kg gram flour + handful of banyan soil
- Ferment 7-10 days, stir twice daily
- Apply 200L/acre every 2 weeks

**Beejamrut (बीजामृत)** — Seed treatment
- 5L water + 250g cow dung + 250ml cow urine
- 50g lime + handful of soil
- Soak seeds 6-12 hrs, dry in shade before planting

**Panchagavya (पंचगव्य)** — Growth booster
- 3kg cow dung + 2L urine + 2L milk + 2L curd + 500g ghee
- Ferment 30 days, stir daily
- Spray at 3% concentration every 15 days
                            """)
                        with gr.Column():
                            gr.Markdown("""
**Neem Spray** — Pest & fungal control
- 5ml cold-pressed neem oil + 2ml liquid soap + 1L water
- Spray evening/morning, every 5-7 days

**Dashparni Ark (दशपर्णी अर्क)** — Broad-spectrum pest repellent
- 1kg each: neem, papaya, custard apple, pomegranate, guava,
  bel, drumstick, lantana, calotropis, eucalyptus leaves
- Add 2L cow urine + 2kg cow dung + 200L water
- Ferment 30-40 days; dilute 3L in 100L for spraying

**Cow Urine Spray (गौमूत्र)** — Fungicide & micronutrient
- Dilute 1:8 with water; spray twice weekly
- Can add 10g neem leaf powder per liter
                            """)

                with gr.Accordion("🌾 Multilevel Farming Layers", open=False):
                    gr.Markdown("""
**Design your farm like a forest — 5 vertical layers:**

| Layer | Height | Crops |
|-------|--------|-------|
| 🌴 Canopy | 15–25 ft | Coconut, Teak, Mango, Jackfruit, Bamboo |
| 🌳 Sub-Canopy | 8–15 ft | Banana, Papaya, Drumstick, Guava, Lemon |
| 🌿 Shrub | 3–8 ft | Tomato, Chilli, Brinjal, Coffee, Cardamom |
| 🌱 Ground Cover | 0–3 ft | Turmeric, Ginger, Leafy greens, Watermelon |
| 🌾 Root Layer | Underground | Yam, Colocasia, Groundnut, Radish |

**Bonus — Climbers**: Beans, Cucumber, Bitter gourd on bamboo/natural supports

> **Income Example (1 acre)**: Coconut ₹40K + Banana ₹30K + Turmeric ₹50K + Vegetables ₹20K = **₹1,40,000/year** vs ₹50K from monoculture
                    """)

                with gr.Accordion("🏛️ Government Schemes", open=False):
                    gr.Markdown("""
| Scheme | Benefit | Apply |
|--------|---------|-------|
| **PM-KISAN** | ₹6,000/year (3 × ₹2,000 installments) | pmkisan.gov.in |
| **PKVY** | ₹50,000/hectare/3yr for organic transition | District Agriculture Office |
| **PM Fasal Bima** | Crop insurance at 2% premium (Kharif) | pmfby.gov.in / Bank |
| **Kisan Credit Card** | Loan at 4% for up to ₹3 lakh | Any bank with land records |
| **eNAM** | Online mandi — pan-India price discovery | enam.gov.in |

**Helplines:**
- Kisan Call Center: **1800-180-1551** (Toll Free, 24×7, 22 languages)
- PM-KISAN Helpline: **155261**
- Crop Insurance: **1800-200-7710**
- eNAM: **1800-270-0224**
                    """)

                with gr.Accordion("📅 Seasonal Crop Calendar", open=False):
                    gr.Markdown("""
| Season | Period | Key Crops |
|--------|--------|-----------|
| **Kharif** | June–October | Rice, Maize, Cotton, Soybean, Sugarcane, Groundnut, Turmeric |
| **Rabi** | November–March | Wheat, Mustard, Peas, Chickpea, Potato, Onion, Tomato |
| **Zaid** | March–June | Watermelon, Muskmelon, Cucumber, Bitter gourd, Okra |
| **Year-Round** | All months | Banana, Coconut, Papaya, Drumstick, Leafy greens |

> **ZBNF Tip**: Sow Beejamrut-treated seeds + apply Jeevamrut soil drench before first rain of Kharif for best results.
                    """)

        # ── Footer ────────────────────────────────────────────
        gr.HTML("""
        <div style="text-align:center; padding:18px; color:#6b7280; font-size:0.82rem; margin-top:16px; border-top:1px solid #e5e7eb;">
            <strong>🌾 KisanVoice</strong> — Built for Indian Farmers · Zero Budget Natural Farming (ZBNF)<br>
            Powered by <strong>Groq AI</strong> · <strong>Open-Meteo</strong> Weather · Realistic Mandi Data<br>
            <em>⚠️ Disclaimer: For severe pest/disease outbreaks, consult your local Agriculture Officer or Krishi Vigyan Kendra (KVK).</em>
        </div>
        """)

    return app


# ──────────────────────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("GRADIO_SERVER_PORT", 7860))

    # HF Spaces sets SPACE_ID — it provides the public URL itself, no share tunnel needed
    on_hf_spaces = bool(os.environ.get("SPACE_ID"))
    share = False if on_hf_spaces else os.environ.get("GRADIO_SHARE", "true").lower() == "true"

    logger.info(f"Starting KisanVoice | HF Spaces: {on_hf_spaces} | Share: {share}")
    logger.info(f"Groq API configured: {llm.is_configured()}")
    logger.info(f"Whisper (faster-whisper) available: {stt.is_available()}")

    app = build_app()
    app.launch(
        server_name="0.0.0.0",
        server_port=port,
        share=share,
        show_error=True,
        css=CSS,
        allowed_paths=[tempfile.gettempdir()],
    )
