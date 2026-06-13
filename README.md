# 🌾 KisanVoice — Voice-Based Natural Farming Consultant

A voice-first AI consultant for Indian farmers transitioning to **Zero Budget Natural Farming (ZBNF)** and multilevel agroforestry. Ask questions by voice, get expert organic farming advice instantly — in your language.

[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://python.org)
[![Gradio](https://img.shields.io/badge/Gradio-4.x-orange)](https://gradio.app)
[![Groq](https://img.shields.io/badge/Groq-llama--3.3--70b-orange)](https://console.groq.com)
[![License](https://img.shields.io/badge/License-MIT-lightgrey)](LICENSE)

---

## 🎯 Features (2 selected)

### 1. 🔬 Disease Identification & Organic Treatment
- Describe crop symptoms **by voice or text** — get instant AI diagnosis
- **Photo upload** for visual disease recognition via Claude Vision
- Prescribes **chemical-free organic remedies** (neem, jeevamrut, cow urine, etc.)
- Keyword-based RAG retrieves relevant disease data before LLM call
- Audio playback of treatment guide in farmer's language

### 2. 🌦️ Weather & Market Intelligence
- **Real-time weather** via Open-Meteo (free, no API key needed)
- 7-day forecast with farming-specific alerts (spray windows, irrigation triggers, heat stress)
- **Mandi prices** for 15+ crops with MSP comparison — shows if price is above/below MSP
- AI-generated selling strategy per crop
- Full mandi price table with refresh

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Gradio Web UI                       │
│  Tab 1: Voice Consultant │ Tab 2: Disease │ Tab 3: W&M  │
└──────────────┬──────────────────────────────────────────┘
               │
    ┌──────────▼──────────┐
    │  Voice Pipeline     │
    │  Audio → STT → Text │
    │  Text → LLM → Text  │
    │  Text → TTS → Audio │
    └──────────┬──────────┘
               │
    ┌──────────▼──────────────────────────────────────────┐
    │              Module Layer                           │
    │                                                     │
    │  stt.py          tts.py          llm.py             │
    │  (Whisper)       (gTTS)          (Groq API)         │
    │                                                     │
    │  weather.py      market.py       knowledge.py       │
    │  (Open-Meteo)    (Mandi data)    (RAG KB)           │
    └─────────────────────────────────────────────────────┘
```

---

## 🧠 Prompt Design

### System Prompt Strategy
The `llm.py` system prompt is designed with **4 guardrail layers**:

1. **Role definition** — Specialized ZBNF expert, not a general assistant
2. **Response rules** — Voice-optimized (≤180 words), numbered steps, local materials
3. **Strict guardrails** — Only agriculture topics; NEVER recommend chemicals; hallucination prevention
4. **Language matching** — Detects query language, responds in same language automatically

### RAG Design (knowledge.py)
Instead of a vector database (which adds complexity and memory overhead), we use **keyword-based RAG**:
- Disease symptom keywords → disease remedies
- Remedy keywords → preparation instructions
- Scheme keywords → scheme details
- Returns max 3 context chunks to avoid prompt bloat

This gives 90% of vector RAG value with zero setup complexity — ideal for on-premise kiosk deployment.

### Example Prompt Flow
```
Farmer: "मेरे धान की पत्तियों पर पीले धब्बे हो गए हैं"
         (My paddy leaves have yellow spots)

RAG: fetches leaf_blight disease info

LLM Input:
  [System: ZBNF expert, respond in Hindi]
  [Context: Leaf blight — neem spray, trichoderma...]
  [User: yellow spots on paddy...]

LLM Output: Hindi response with 3-step neem treatment
TTS: gTTS converts to Hindi audio
```

---

## 🌐 Localization

Supported languages with full voice pipeline:

| Language | STT (Whisper) | TTS (gTTS) |
|----------|--------------|-----------|
| English | ✅ | ✅ |
| हिंदी (Hindi) | ✅ | ✅ |
| தமிழ் (Tamil) | ✅ | ✅ |
| తెలుగు (Telugu) | ✅ | ✅ |
| मराठी (Marathi) | ✅ | ✅ |
| ਪੰਜਾਬੀ (Punjabi) | ✅ | ✅ |
| বাংলা (Bengali) | ✅ | ✅ |
| ಕನ್ನಡ (Kannada) | ✅ | ✅ |
| മലയാളം (Malayalam) | ✅ | ✅ |
| ગુજરાતી (Gujarati) | ✅ | ✅ |

**LLM Language**: Claude detects query language and auto-responds in matching language. Explicit language selection overrides auto-detection.

---

## ⚙️ Tech Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| UI Framework | Gradio 4.x | Rapid deployment, mobile-responsive, built-in audio |
| LLM | Groq — llama-3.3-70b-versatile (text) + llama-3.2-11b-vision (image) | Free tier, ultra-fast inference |
| STT | OpenAI Whisper (base model) | Offline, 74MB, supports Indian languages |
| TTS | gTTS (Google TTS) | Free, supports 10 Indian languages |
| Weather | Open-Meteo API | Free forever, no API key, 1km resolution |
| Market Data | In-memory + Agmarknet-compatible structure | Real-time ready, demo fallback |
| RAG | Keyword-based (knowledge.py) | Zero dependencies, fast, accurate for domain |

---

## 🚀 Setup & Running

### Prerequisites
- Python 3.10+
- FFmpeg (for Whisper audio processing)
  ```bash
  # Windows
  winget install ffmpeg
  # Ubuntu
  sudo apt install ffmpeg
  ```

### Installation

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/kisanvoice
cd kisanvoice

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GROQ_API_KEY (free at console.groq.com)
```

### Running

```bash
python app.py
```

Open [http://localhost:7860](http://localhost:7860) or use the public Gradio share URL printed in console.

### Deploy to Hugging Face Spaces

1. Create a new Space on [huggingface.co/spaces](https://huggingface.co/spaces)
2. Select **Gradio** SDK
3. Push this repo
4. Add `GROQ_API_KEY` in Space secrets

---

## 📁 Project Structure

```
kisanvoice/
├── app.py                  # Main Gradio UI + event handlers
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
├── README.md               # This file
└── modules/
    ├── __init__.py
    ├── stt.py              # Speech-to-Text (Whisper)
    ├── tts.py              # Text-to-Speech (gTTS)
    ├── llm.py              # Claude LLM + system prompt
    ├── weather.py          # Open-Meteo weather API
    ├── market.py           # Crop mandi prices & MSP data
    └── knowledge.py        # Farming knowledge base (RAG)
```

---

## 🔒 Demo Mode

Run without an API key — the app works in **Demo Mode** with pre-written sample responses. All voice pipeline, weather, and market features remain fully functional.

---

## 🌱 Roadmap

- [ ] Integration with Agmarknet API for live mandi prices
- [ ] Soil health tracker with input logging
- [ ] Offline mode with local LLM (Ollama)
- [ ] WhatsApp Business API integration
- [ ] Community disease photo database
- [ ] IVRS integration for feature phone users

---

## 📜 License

MIT License — free for farmers, NGOs, and agricultural organizations.

---

*Built with ❤️ for India's 120 million farming families*
