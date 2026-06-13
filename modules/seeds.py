"""
Seed & Financial Guidance module.
Covers: seed varieties by crop/region, planting calendar, per-acre cost-benefit,
        national + state government seed subsidies.
"""

# ── Seed variety catalogue ─────────────────────────────────────────────────────
SEED_VARIETIES: dict[str, dict] = {
    "wheat": {
        "season": "Rabi (Nov – Apr)",
        "sowing_window": "Oct 25 – Nov 25",
        "seed_rate": "100 kg/acre",
        "spacing": "Row spacing: 22.5 cm",
        "depth": "4–5 cm",
        "germination": "7–10 days",
        "duration": "140–150 days",
        "water_needs": "4–5 irrigations",
        "beejamrut": True,
        "varieties": [
            {"name": "HD-2967", "yield": "50–55 q/acre", "duration": "145 days",
             "strength": "High yield, rust resistant", "states": ["Punjab", "Haryana", "UP", "Uttarakhand"]},
            {"name": "HD-3086", "yield": "52–58 q/acre", "duration": "142 days",
             "strength": "Yellow rust + heat tolerant", "states": ["Punjab", "Haryana", "Rajasthan"]},
            {"name": "GW-322", "yield": "40–45 q/acre", "duration": "115 days",
             "strength": "Short duration, heat tolerant", "states": ["Gujarat", "Rajasthan", "MP"]},
            {"name": "K-0307 (Shatabdi)", "yield": "48–52 q/acre", "duration": "138 days",
             "strength": "Late sowing tolerant", "states": ["UP", "Bihar", "Jharkhand"]},
        ],
    },
    "rice": {
        "season": "Kharif (Jun – Nov)",
        "sowing_window": "Jun 15 – Jul 15 (transplant); May 15 – Jun 15 (nursery)",
        "seed_rate": "25 kg/acre (transplant); 40 kg/acre (direct seeding)",
        "spacing": "20 cm × 15 cm",
        "depth": "2–3 cm (direct seeding)",
        "germination": "4–7 days",
        "duration": "110–145 days",
        "water_needs": "Continuous flooding or SRI (System of Rice Intensification)",
        "beejamrut": True,
        "varieties": [
            {"name": "Swarna (MTU-7029)", "yield": "50–55 q/acre", "duration": "145 days",
             "strength": "High yield, flood tolerant", "states": ["AP", "Telangana", "Odisha", "Bengal"]},
            {"name": "Pusa-44", "yield": "55–60 q/acre", "duration": "160 days",
             "strength": "Highest yield in Punjab", "states": ["Punjab", "Haryana"]},
            {"name": "MTU-1010", "yield": "48–52 q/acre", "duration": "125 days",
             "strength": "Short duration, quality grain", "states": ["AP", "Telangana", "Karnataka"]},
            {"name": "Sahbhagi Dhan", "yield": "30–35 q/acre", "duration": "110 days",
             "strength": "Drought tolerant — ZBNF recommended", "states": ["All states"]},
        ],
    },
    "cotton": {
        "season": "Kharif (Apr – Nov)",
        "sowing_window": "Apr 15 – Jun 15",
        "seed_rate": "1–1.5 kg/acre (hybrid); 8–10 kg/acre (desi)",
        "spacing": "90 cm × 45 cm",
        "depth": "3–4 cm",
        "germination": "5–7 days",
        "duration": "150–180 days",
        "water_needs": "5–7 irrigations; critical at flowering",
        "beejamrut": True,
        "varieties": [
            {"name": "Namdhari NS-855 (Desi)", "yield": "8–10 q/acre", "duration": "160 days",
             "strength": "Open-pollinated, low input, ZBNF ideal", "states": ["Vidarbha", "Telangana", "Gujarat"]},
            {"name": "DCH-32 (Hybrid)", "yield": "12–15 q/acre", "duration": "175 days",
             "strength": "High fiber length", "states": ["Maharashtra", "Gujarat", "AP"]},
            {"name": "LRA-5166 (Desi)", "yield": "7–9 q/acre", "duration": "155 days",
             "strength": "Drought tolerant, less pest pressure", "states": ["Rajasthan", "Haryana"]},
        ],
    },
    "tomato": {
        "season": "Year-round (main: Oct–Jan, Feb–May)",
        "sowing_window": "Nursery 4–5 weeks before transplanting",
        "seed_rate": "100–150 g/acre",
        "spacing": "60 cm × 45 cm",
        "depth": "0.5 cm (nursery)",
        "germination": "5–8 days",
        "duration": "70–100 days",
        "water_needs": "Drip irrigation preferred; every 3–5 days",
        "beejamrut": True,
        "varieties": [
            {"name": "Arka Rakshak (IIHR)", "yield": "100–120 q/acre", "duration": "75 days",
             "strength": "Triple disease resistant, long shelf life", "states": ["All states"]},
            {"name": "Pusa Ruby", "yield": "60–70 q/acre", "duration": "70 days",
             "strength": "Open-pollinated, good for processing", "states": ["All states"]},
            {"name": "Solan Vajra", "yield": "80–100 q/acre", "duration": "80 days",
             "strength": "TLCV virus resistant", "states": ["Hills, HP, UP, Uttarakhand"]},
        ],
    },
    "maize": {
        "season": "Kharif (Jun–Oct) / Rabi (Nov–Mar)",
        "sowing_window": "Jun 15 – Jul 15 (Kharif); Nov 1 – Nov 30 (Rabi)",
        "seed_rate": "8–10 kg/acre",
        "spacing": "60 cm × 20 cm",
        "depth": "4–5 cm",
        "germination": "5–7 days",
        "duration": "90–110 days",
        "water_needs": "5–6 irrigations; critical at tasseling",
        "beejamrut": True,
        "varieties": [
            {"name": "DHM-117", "yield": "35–40 q/acre", "duration": "100 days",
             "strength": "High yield, drought tolerant", "states": ["Bihar", "UP", "MP"]},
            {"name": "Vivek QPM-9", "yield": "30–35 q/acre", "duration": "90 days",
             "strength": "Protein-rich, short duration", "states": ["Hills, NE India"]},
            {"name": "Pusa Composite-3", "yield": "28–32 q/acre", "duration": "95 days",
             "strength": "Open-pollinated, lower seed cost", "states": ["All states"]},
        ],
    },
    "turmeric": {
        "season": "Kharif (Apr–Jan)",
        "sowing_window": "Apr – Jun (with first rains)",
        "seed_rate": "600–800 kg/acre (rhizomes)",
        "spacing": "45 cm × 20 cm",
        "depth": "5–7 cm",
        "germination": "20–30 days",
        "duration": "270–300 days",
        "water_needs": "Every 7–10 days; critical in dry spell",
        "beejamrut": True,
        "varieties": [
            {"name": "BSR-2 (Salem)", "yield": "70–80 q/acre fresh", "duration": "270 days",
             "strength": "High curcumin (5.5%), premium price", "states": ["Tamil Nadu", "Telangana"]},
            {"name": "Pratibha", "yield": "80–90 q/acre fresh", "duration": "280 days",
             "strength": "Disease resistant, high yield", "states": ["Maharashtra", "MP", "Odisha"]},
            {"name": "Suguna", "yield": "85–95 q/acre fresh", "duration": "285 days",
             "strength": "Best for multilevel farming shade", "states": ["Karnataka", "Kerala"]},
        ],
    },
    "onion": {
        "season": "Rabi (Nov–May) / Kharif (Jun–Dec)",
        "sowing_window": "Oct 15 – Nov 30 (Rabi); Jun – Jul (Kharif)",
        "seed_rate": "3–4 kg/acre",
        "spacing": "15 cm × 10 cm",
        "depth": "1–2 cm",
        "germination": "7–10 days",
        "duration": "100–120 days",
        "water_needs": "Every 8–10 days; stop 2 weeks before harvest",
        "beejamrut": True,
        "varieties": [
            {"name": "N-2-4-1", "yield": "100–120 q/acre", "duration": "120 days",
             "strength": "Pink, good storage, high pungency", "states": ["Maharashtra", "Karnataka"]},
            {"name": "Agrifound Dark Red", "yield": "80–100 q/acre", "duration": "110 days",
             "strength": "Dark red, all-India adapted", "states": ["All states"]},
        ],
    },
    "mustard": {
        "season": "Rabi (Oct–Mar)",
        "sowing_window": "Oct 1 – Oct 25",
        "seed_rate": "2–2.5 kg/acre",
        "spacing": "30 cm × 10 cm",
        "depth": "2–3 cm",
        "germination": "4–6 days",
        "duration": "110–130 days",
        "water_needs": "2–3 irrigations",
        "beejamrut": True,
        "varieties": [
            {"name": "Pusa Bold", "yield": "10–12 q/acre", "duration": "125 days",
             "strength": "High oil content (39–42%), widely adapted", "states": ["Rajasthan", "Haryana", "UP"]},
            {"name": "RH-749", "yield": "12–14 q/acre", "duration": "130 days",
             "strength": "Aphid tolerant, high yield", "states": ["Rajasthan", "Haryana"]},
        ],
    },
}

# ── Per-acre economics ─────────────────────────────────────────────────────────
CROP_ECONOMICS: dict[str, dict] = {
    "wheat":    {"seed": 2500,  "land_prep": 3000, "sowing": 1500, "irrigation": 2500,
                 "organic_inputs": 2000, "pest_mgmt": 1000, "harvest": 3000,
                 "avg_yield_q": 10, "msp": 2275},
    "rice":     {"seed": 2000,  "land_prep": 4000, "sowing": 2500, "irrigation": 3000,
                 "organic_inputs": 2500, "pest_mgmt": 1500, "harvest": 3500,
                 "avg_yield_q": 22, "msp": 2183},
    "cotton":   {"seed": 1500,  "land_prep": 3500, "sowing": 1000, "irrigation": 2000,
                 "organic_inputs": 3000, "pest_mgmt": 2000, "harvest": 4000,
                 "avg_yield_q": 8,  "msp": 6620},
    "maize":    {"seed": 1500,  "land_prep": 2500, "sowing": 1000, "irrigation": 1500,
                 "organic_inputs": 1500, "pest_mgmt": 800,  "harvest": 2000,
                 "avg_yield_q": 15, "msp": 1850},
    "turmeric": {"seed": 15000, "land_prep": 4000, "sowing": 3000, "irrigation": 3000,
                 "organic_inputs": 3000, "pest_mgmt": 1000, "harvest": 5000,
                 "avg_yield_q": 40, "msp": None, "market_price": 12000},
    "mustard":  {"seed": 600,   "land_prep": 2000, "sowing": 800,  "irrigation": 1000,
                 "organic_inputs": 1500, "pest_mgmt": 500,  "harvest": 2000,
                 "avg_yield_q": 6,  "msp": 5650},
    "onion":    {"seed": 1500,  "land_prep": 3000, "sowing": 2000, "irrigation": 2500,
                 "organic_inputs": 2000, "pest_mgmt": 1000, "harvest": 3000,
                 "avg_yield_q": 60, "msp": None, "market_price": 1400},
    "tomato":   {"seed": 1200,  "land_prep": 3000, "sowing": 2500, "irrigation": 2500,
                 "organic_inputs": 2500, "pest_mgmt": 1500, "harvest": 3000,
                 "avg_yield_q": 80, "msp": None, "market_price": 1800},
}

# ── Government seed & farming subsidies ───────────────────────────────────────
CENTRAL_SCHEMES: list[dict] = [
    {
        "name": "National Seeds Mission (NSM)",
        "benefit": "50% subsidy on foundation/certified seeds of notified varieties",
        "crops": "Wheat, Rice, Pulses, Oilseeds, Coarse cereals",
        "apply": "District Agriculture Office or State Seeds Corporation",
        "amount": "50% cost subsidy on certified seed purchase",
    },
    {
        "name": "NFSM Seed Mini Kits",
        "benefit": "FREE certified seed kits distributed to farmers",
        "crops": "Rice, Wheat, Pulses, Coarse cereals",
        "apply": "District Agriculture Officer — register before season",
        "amount": "Free seed kit (1–2 kg per farmer per season)",
    },
    {
        "name": "PKVY (Paramparagat Krishi Vikas Yojana)",
        "benefit": "₹50,000/ha over 3 years for organic farming + seed support",
        "crops": "All crops transitioning to organic",
        "apply": "Form clusters of 50+ farmers → apply via State Organic Mission",
        "amount": "₹50,000/hectare/3 years",
    },
    {
        "name": "PM-KISAN",
        "benefit": "Direct income support ₹6,000/year to all eligible farmer families",
        "crops": "All",
        "apply": "pmkisan.gov.in or nearest CSC",
        "amount": "₹6,000/year in 3 installments of ₹2,000",
    },
    {
        "name": "Kisan Credit Card (KCC)",
        "benefit": "Crop loan at 4% effective interest (7% minus 3% interest subvention)",
        "crops": "All crops",
        "apply": "Nearest bank branch with land records + Aadhaar",
        "amount": "Up to ₹3 lakh at 4% interest",
    },
    {
        "name": "Seed Village Programme",
        "benefit": "Training + 25–50% subsidy to produce quality seeds at village level",
        "crops": "Self-pollinated crops: wheat, rice, pulses, oilseeds",
        "apply": "State Agriculture Department or KVK",
        "amount": "25–50% cost subsidy on seed processing",
    },
]

STATE_SCHEMES: dict[str, list[str]] = {
    "Punjab":       ["Punjab Apni Mandi Scheme (direct selling)", "Kisan Karj Mafi (debt waiver)", "Free electricity for irrigation"],
    "Haryana":      ["Meri Fasal Mera Byora portal", "Bhavantar Bharpai Yojana (price deficiency payment)", "50% subsidy on drip irrigation"],
    "Maharashtra":  ["Jalyukt Shivar (water conservation)", "Nanaji Deshmukh Krishi Sanjivani (PDKVY)", "Seed subsidy for pulses + oilseeds"],
    "UP":           ["UP Kisan Karj Rahat (debt relief)", "Mukhyamantri Kisan & Sarvhit Bima", "50% subsidy on farm machinery"],
    "MP":           ["Bhavantar Bhugtan Yojana (MSP deficiency)", "PM Krishi Sinchai Yojana", "Zero-interest crop loan"],
    "Rajasthan":    ["Mukhyamantri Krishi Vikas Yojana", "Subsidy on drip/sprinkler irrigation", "Free seed for SC/ST farmers"],
    "AP":           ["YSR Rythu Bharosa (₹13,500/year)", "Zero-interest crop loan", "Free seed kits"],
    "Telangana":    ["Rythu Bandhu (₹10,000/acre/year)", "Rythu Bima (life insurance)", "Free seed kits at mandal level"],
    "Karnataka":    ["Raitha Siri (₹25,000 assistance)", "PM-KISAN + state top-up", "Subsidy on certified organic seeds"],
    "Tamil Nadu":   ["Uzhavar Sandhai direct markets", "CM's Comprehensive Crop Insurance", "50% subsidy on Kisan Drone"],
    "Gujarat":      ["Mukhyamantri Kisan Sahay (₹20,000 crop failure)", "i-Khedut portal for subsidies", "Subsidy on organic inputs"],
    "Bihar":        ["Bihar Rajya Fasal Sahayata Yojana", "Seed subsidy for kharif + rabi", "Subsidy on soil testing"],
    "Other":        ["Contact your District Agriculture Officer", "Visit state agriculture department website", "Call Kisan Call Center: 1800-180-1551"],
}


# ── Public-facing functions ───────────────────────────────────────────────────

def crop_list() -> list[str]:
    return list(SEED_VARIETIES.keys())


def get_seed_guide(crop: str) -> dict | None:
    return SEED_VARIETIES.get(crop.lower())


def get_varieties_table(crop: str) -> list[list]:
    guide = get_seed_guide(crop)
    if not guide:
        return []
    return [
        [v["name"], v["yield"], v["duration"], v["strength"], ", ".join(v["states"][:2])]
        for v in guide.get("varieties", [])
    ]


def get_planting_card(crop: str) -> str:
    guide = get_seed_guide(crop)
    if not guide:
        return f"Planting information for **{crop}** not available."
    beejamrut_note = "✅ **Treat seeds with Beejamrut** before sowing for better germination & disease resistance." if guide.get("beejamrut") else ""
    return f"""## 🌱 Planting Guide — {crop.title()}

| Parameter | Details |
|-----------|---------|
| 📅 Season | {guide['season']} |
| 🗓️ Sowing Window | {guide['sowing_window']} |
| 🌾 Seed Rate | {guide['seed_rate']} |
| 📏 Spacing | {guide['spacing']} |
| 🕳️ Depth | {guide['depth']} |
| 🌿 Germination | {guide['germination']} |
| ⏱️ Crop Duration | {guide['duration']} |
| 💧 Water Needs | {guide['water_needs']} |

{beejamrut_note}"""


def get_financial_card(crop: str, acres: float = 1.0) -> str:
    eco = CROP_ECONOMICS.get(crop.lower())
    if not eco:
        return f"Financial data for **{crop}** not available."

    costs = {k: v for k, v in eco.items() if k not in ("avg_yield_q", "msp", "market_price")}
    total_cost = round(sum(costs.values()) * acres)
    avg_yield = eco["avg_yield_q"] * acres
    price = eco.get("msp") or eco.get("market_price", 0)
    revenue = round(avg_yield * price)
    profit = revenue - total_cost
    roi = round((profit / total_cost) * 100) if total_cost else 0

    cost_rows = "\n".join(
        f"| {k.replace('_', ' ').title()} | ₹{round(v * acres):,} |"
        for k, v in costs.items()
    )

    msp_note = f"at MSP ₹{eco['msp']}/q" if eco.get("msp") else f"at market price ₹{eco.get('market_price', 0)}/q"
    profit_icon = "✅" if profit > 0 else "⚠️"

    return f"""## 💰 Financial Analysis — {crop.title()} ({acres} acre{'s' if acres > 1 else ''})

### Cost Breakdown
| Item | Amount |
|------|--------|
{cost_rows}
| **Total Cost** | **₹{total_cost:,}** |

### Revenue Projection
| Metric | Value |
|--------|-------|
| Avg. Yield | {avg_yield:.0f} quintals |
| Selling Price | ₹{price}/quintal ({msp_note}) |
| **Expected Revenue** | **₹{revenue:,}** |
| {profit_icon} **Net Profit** | **₹{profit:,}** |
| 📈 ROI | {roi}% |

> 💡 *Organic farming reduces input costs by 30–40% after Year 2 as soil health improves.*"""


def get_subsidies_card(state: str = "Other") -> str:
    central = "\n".join(
        f"**{s['name']}**: {s['benefit']} — *{s['amount']}* | Apply: {s['apply']}"
        for s in CENTRAL_SCHEMES
    )
    state_key = state if state in STATE_SCHEMES else "Other"
    state_list = "\n".join(f"- {item}" for item in STATE_SCHEMES[state_key])
    return f"""## 🏛️ Government Subsidies & Schemes

### Central Government (All States)
{central}

### {state_key} State Schemes
{state_list}

---
📞 **Seed Subsidy Helpline**: 1800-180-1551 (Kisan Call Center, free, 24×7)
🌐 **Online**: [TNAU Seed Portal](https://seeds.tnau.ac.in) · [iKhedut Gujarat](https://ikhedut.gujarat.gov.in)"""


def get_seed_context_for_llm(crop: str, state: str = "") -> str:
    guide = get_seed_guide(crop)
    if not guide:
        return f"No seed data for {crop}."
    top_variety = guide["varieties"][0] if guide["varieties"] else {}
    eco = CROP_ECONOMICS.get(crop, {})
    state_schemes = STATE_SCHEMES.get(state, STATE_SCHEMES["Other"])
    return (
        f"Crop: {crop.title()} | Season: {guide['season']} | "
        f"Sowing: {guide['sowing_window']} | Seed rate: {guide['seed_rate']} | "
        f"Duration: {guide['duration']} | Water: {guide['water_needs']} | "
        f"Best variety: {top_variety.get('name','N/A')} ({top_variety.get('yield','N/A')}) | "
        f"Approx cost/acre: ₹{sum(v for k,v in eco.items() if k not in ('avg_yield_q','msp','market_price')):,} | "
        f"State schemes: {'; '.join(state_schemes[:2])}"
    )
