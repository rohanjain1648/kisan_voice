"""Crop market prices module with realistic Indian mandi data."""
import random
from datetime import datetime

# Mandi prices (₹/quintal) — updated periodically in production via Agmarknet API
# Structure: name, current_price, msp (or None), trend, best_market, notes
CROP_REGISTRY: dict[str, dict] = {
    "wheat": {
        "display": "Wheat (गेहूं)", "current": 2310, "msp": 2275,
        "trend": "↑", "trend_label": "Rising", "unit": "quintal",
        "best_market": "Ludhiana (Punjab), Sirsa (Haryana)",
        "harvest_months": ["Mar", "Apr"],
        "storage_tip": "Moisture below 12% needed for safe storage. Use hermetic bags.",
    },
    "rice": {
        "display": "Rice / Paddy (धान)", "current": 2350, "msp": 2183,
        "trend": "↑", "trend_label": "Rising", "unit": "quintal",
        "best_market": "Chhattisgarh Mandi, AP Mandis",
        "harvest_months": ["Oct", "Nov"],
        "storage_tip": "Dry to 14% moisture. Protect from weevils with neem leaves.",
    },
    "cotton": {
        "display": "Cotton (कपास)", "current": 6950, "msp": 6620,
        "trend": "↑", "trend_label": "Rising", "unit": "quintal",
        "best_market": "Rajkot (Gujarat), Akola (Maharashtra)",
        "harvest_months": ["Oct", "Nov", "Dec"],
        "storage_tip": "Store in dry place. Grade before selling for 10-15% premium.",
    },
    "tomato": {
        "display": "Tomato (टमाटर)", "current": 1800, "msp": None,
        "trend": "↕", "trend_label": "Volatile", "unit": "quintal",
        "best_market": "Azadpur (Delhi), Vashi (Mumbai)",
        "harvest_months": ["Oct", "Nov", "Feb", "Mar"],
        "storage_tip": "Sell immediately after harvest. Consider FPO for bulk selling.",
    },
    "onion": {
        "display": "Onion (प्याज)", "current": 1400, "msp": None,
        "trend": "↓", "trend_label": "Falling", "unit": "quintal",
        "best_market": "Lasalgaon (Nashik), Solapur",
        "harvest_months": ["Apr", "May", "Nov"],
        "storage_tip": "Curing reduces moisture loss. Ventilated storage critical.",
    },
    "potato": {
        "display": "Potato (आलू)", "current": 900, "msp": None,
        "trend": "→", "trend_label": "Stable", "unit": "quintal",
        "best_market": "Agra (UP), Jalandhar (Punjab)",
        "harvest_months": ["Mar", "Apr"],
        "storage_tip": "Cold storage extends shelf life to 6 months.",
    },
    "soybean": {
        "display": "Soybean (सोयाबीन)", "current": 4520, "msp": 4600,
        "trend": "→", "trend_label": "Stable", "unit": "quintal",
        "best_market": "Indore, Dewas (Madhya Pradesh)",
        "harvest_months": ["Oct", "Nov"],
        "storage_tip": "Dry to 12% moisture. Check for aflatoxin before selling.",
    },
    "maize": {
        "display": "Maize (मक्का)", "current": 1920, "msp": 1850,
        "trend": "↑", "trend_label": "Rising", "unit": "quintal",
        "best_market": "Karnataka, Bihar Mandis",
        "harvest_months": ["Sep", "Oct", "Mar"],
        "storage_tip": "Dry below 14% moisture. Store in airtight bins.",
    },
    "turmeric": {
        "display": "Turmeric (हल्दी)", "current": 12500, "msp": None,
        "trend": "↑", "trend_label": "Rising", "unit": "quintal",
        "best_market": "Nizamabad (Telangana), Sangli (Maharashtra)",
        "harvest_months": ["Jan", "Feb", "Mar"],
        "storage_tip": "Cure and polish for premium price. Organic certified commands 20-30% premium.",
    },
    "ginger": {
        "display": "Ginger (अदरक)", "current": 8200, "msp": None,
        "trend": "↕", "trend_label": "Volatile", "unit": "quintal",
        "best_market": "Cochin (Kerala), Wayanad",
        "harvest_months": ["Dec", "Jan", "Feb"],
        "storage_tip": "Process to dry ginger for longer shelf life and better price.",
    },
    "chilli": {
        "display": "Chilli (मिर्च)", "current": 9800, "msp": None,
        "trend": "↑", "trend_label": "Rising", "unit": "quintal",
        "best_market": "Guntur (Andhra Pradesh), Khammam",
        "harvest_months": ["Dec", "Jan", "Feb"],
        "storage_tip": "Dry to below 10% moisture. Grade by color for premium.",
    },
    "sugarcane": {
        "display": "Sugarcane (गन्ना)", "current": 315, "msp": 315,
        "trend": "→", "trend_label": "Stable", "unit": "quintal",
        "best_market": "Local Sugar Mill (SAP price applies)",
        "harvest_months": ["Oct", "Nov", "Dec", "Jan", "Feb", "Mar"],
        "storage_tip": "Deliver within 24 hours of harvest. SAP rate guaranteed by state.",
    },
    "mustard": {
        "display": "Mustard (सरसों)", "current": 5450, "msp": 5650,
        "trend": "↓", "trend_label": "Below MSP", "unit": "quintal",
        "best_market": "Alwar (Rajasthan), Bharatpur",
        "harvest_months": ["Mar", "Apr"],
        "storage_tip": "Use government procurement (NAFED) when price is below MSP.",
    },
    "chickpea": {
        "display": "Chickpea / Chana (चना)", "current": 5300, "msp": 5440,
        "trend": "↓", "trend_label": "Below MSP", "unit": "quintal",
        "best_market": "Indore, Gwalior (MP), Jodhpur",
        "harvest_months": ["Mar", "Apr"],
        "storage_tip": "Clean and grade. Register on eNAM for transparent price discovery.",
    },
    "groundnut": {
        "display": "Groundnut (मूंगफली)", "current": 5800, "msp": 6377,
        "trend": "↓", "trend_label": "Below MSP", "unit": "quintal",
        "best_market": "Rajkot (Gujarat), Kurnool (AP)",
        "harvest_months": ["Oct", "Nov"],
        "storage_tip": "Use government procurement when market price below MSP.",
    },
}


def get_price(crop_name: str) -> dict | None:
    """Get price data for a crop with slight random variation (simulates live data)."""
    key = crop_name.lower().strip().replace(" ", "_")
    # Also try partial match
    if key not in CROP_REGISTRY:
        for k in CROP_REGISTRY:
            if k.startswith(key[:4]) or key in k:
                key = k
                break
        else:
            return None

    data = CROP_REGISTRY[key].copy()
    # Simulate market fluctuation ±2%
    variation = random.uniform(-0.02, 0.02)
    data["current"] = round(data["current"] * (1 + variation))
    data["as_of"] = datetime.now().strftime("%d %b %Y, %H:%M IST")
    return data


def format_market_card(crop_name: str) -> str:
    """Generate a detailed market intelligence card for a crop."""
    data = get_price(crop_name)
    if not data:
        available = ", ".join(k.title() for k in CROP_REGISTRY)
        return f"❌ Market data for **{crop_name}** not available.\n\n**Available crops**: {available}"

    current = data["current"]
    msp = data.get("msp")

    # MSP comparison
    if msp:
        diff = current - msp
        if diff >= 0:
            msp_line = f"✅ **₹{current}/q** — ₹{diff} above MSP (₹{msp}). Good time to sell!"
            action = "**Recommended Action**: Sell now or within 1-2 weeks if price trend is stable."
        else:
            msp_line = f"⚠️ **₹{current}/q** — ₹{abs(diff)} BELOW MSP (₹{msp}). Consider government procurement."
            action = "**Recommended Action**: Register at nearest NAFED/FCI procurement center. Do NOT sell below MSP."
    else:
        msp_line = f"**₹{current}/q** — No government MSP fixed for this crop."
        action = "**Recommended Action**: Compare on eNAM (enam.gov.in) for best pan-India price."

    trend_emoji = {"↑": "📈", "↓": "📉", "↕": "📊", "→": "➡️"}.get(data["trend"], "")

    return f"""## {data['display']} — Market Report
*As of {data['as_of']}*

### Price Summary
{msp_line}

| Metric | Value |
|--------|-------|
| {trend_emoji} Price Trend | {data['trend']} {data['trend_label']} |
| 🏪 Best Market | {data['best_market']} |
| 📅 Harvest Months | {', '.join(data['harvest_months'])} |

### Selling Strategy
{action}

### Storage Tip
💡 {data['storage_tip']}

### Useful Links
- 📊 Live prices: [eNAM Portal](https://enam.gov.in)
- 🏦 MSP procurement: Contact nearest NAFED/FCI office
- 📱 Agmarknet price app: Available on Android"""


def get_all_prices_table() -> list[list]:
    """Return price table rows for Gradio DataFrame."""
    rows = []
    for key, data in CROP_REGISTRY.items():
        variation = random.uniform(-0.02, 0.02)
        current = round(data["current"] * (1 + variation))
        msp = f"₹{data['msp']}" if data["msp"] else "—"
        above_below = ""
        if data["msp"]:
            diff = current - data["msp"]
            above_below = f"+{diff}" if diff >= 0 else str(diff)
        rows.append([
            data["display"],
            f"₹{current}",
            msp,
            above_below,
            f"{data['trend']} {data['trend_label']}",
            data["best_market"],
        ])
    return rows


def crop_list() -> list[str]:
    return list(CROP_REGISTRY.keys())


def get_market_summary_for_llm(crop_name: str) -> str:
    """Compact market context for LLM prompt."""
    data = get_price(crop_name)
    if not data:
        return f"No market data available for {crop_name}."
    msp_text = f"MSP: ₹{data['msp']}/quintal" if data["msp"] else "No MSP"
    return (
        f"{data['display']}: Current price ₹{data['current']}/quintal | "
        f"{msp_text} | Trend: {data['trend_label']} | "
        f"Best market: {data['best_market']}"
    )
