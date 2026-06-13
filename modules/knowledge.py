"""
Farming knowledge base with keyword-based RAG.
Covers: diseases, organic remedies, ZBNF techniques, multilevel farming, government schemes.
"""

DISEASES = {
    "leaf_blight": {
        "keywords": ["yellow spot", "brown edge", "blight", "brown patch", "leaf burn"],
        "crops": ["rice", "wheat", "maize", "paddy", "finger millet"],
        "symptoms": "Yellow/brown spots on leaves, browning edges, wilting in patches",
        "remedy": (
            "1. Spray 3% neem oil solution (3ml neem oil + 1ml soap + 1L water) twice weekly.\n"
            "2. Drench soil with Trichoderma viride (5g/L water).\n"
            "3. Apply Panchagavya (3% solution) as foliar spray.\n"
            "4. Remove and compost infected leaves away from field."
        ),
        "prevention": "Maintain crop spacing, avoid overhead irrigation, follow crop rotation.",
    },
    "powdery_mildew": {
        "keywords": ["white powder", "powdery", "white coating", "white dust", "flour on leaves"],
        "crops": ["cucurbits", "tomato", "chilli", "okra", "grapes", "peas"],
        "symptoms": "White powdery coating on leaves and stems, stunted growth, leaf curl",
        "remedy": (
            "1. Spray diluted buttermilk (1:10 ratio) in early morning.\n"
            "2. Mix 1 tsp baking soda + 2ml neem oil in 1L water; spray twice weekly.\n"
            "3. Apply cow urine spray (1:8 dilution).\n"
            "4. Increase potassium by applying wood ash around base."
        ),
        "prevention": "Ensure air circulation, avoid excess nitrogen, use resistant varieties.",
    },
    "root_rot": {
        "keywords": ["wilting", "root rot", "dark root", "soggy root", "stem rot", "collar rot"],
        "crops": ["all crops"],
        "symptoms": "Yellowing/wilting despite adequate water, dark mushy roots, plant collapse",
        "remedy": (
            "1. Drench with Jeevamrut (200ml per plant).\n"
            "2. Apply Trichoderma harzianum + Pseudomonas fluorescens mix in soil.\n"
            "3. Reduce watering immediately; improve field drainage.\n"
            "4. Add coarse sand or organic matter to improve soil aeration."
        ),
        "prevention": "Well-drained beds, proper Jeevamrut use, avoid waterlogging.",
    },
    "aphids": {
        "keywords": ["aphid", "sticky leaf", "curl leaf", "small insect", "black fly", "green fly", "sucking pest"],
        "crops": ["vegetables", "cotton", "wheat", "mustard", "okra"],
        "symptoms": "Sticky honeydew on leaves, curled new growth, clusters of tiny insects",
        "remedy": (
            "1. Spray diluted cow urine (1:8 ratio) twice a week.\n"
            "2. Neem-garlic-chilli spray: blend 100g garlic + 10 chillies + 500ml water, filter, dilute 1:5.\n"
            "3. Release ladybird beetles (available at KVK centers).\n"
            "4. Install yellow sticky traps between rows."
        ),
        "prevention": "Companion plant coriander/marigold, maintain natural predator habitat.",
    },
    "stem_borer": {
        "keywords": ["dead heart", "hollow stem", "borer", "larva", "white moth", "stem damage", "shoot dead"],
        "crops": ["rice", "sugarcane", "maize", "sorghum"],
        "symptoms": "Dead central shoot (dead heart) in paddy, hollow stems, white larvae inside",
        "remedy": (
            "1. Apply Neem Kernel Extract (5% NSKE): soak 5kg neem kernel in 100L water overnight.\n"
            "2. Release Trichogramma parasitoid cards (1.5 lakh eggs/acre).\n"
            "3. Install pheromone traps (1 per acre) to monitor adults.\n"
            "4. Use light traps at night to attract and kill moths."
        ),
        "prevention": "Balanced nutrition, avoid excess nitrogen, timely transplanting.",
    },
    "fungal_wilt": {
        "keywords": ["wilt", "fusarium", "verticillium", "vascular", "brown vein", "sudden death"],
        "crops": ["tomato", "chilli", "banana", "cotton"],
        "symptoms": "Sudden wilting, brown discoloration inside stem when cut, one-sided wilting",
        "remedy": (
            "1. Soil drench with Trichoderma viride (10g/L water).\n"
            "2. Apply Jeevamrut soil drench twice a month.\n"
            "3. Add well-decomposed FYM enriched with Trichoderma.\n"
            "4. Remove and destroy infected plants; do not compost."
        ),
        "prevention": "Crop rotation (avoid same family for 3 years), use certified seeds, soil solarization.",
    },
}

ORGANIC_REMEDIES = {
    "jeevamrut": {
        "name": "Jeevamrut (जीवामृत)",
        "purpose": "Soil microbial activator, fertilizer, pest repellent",
        "ingredients": "200L water + 10kg fresh cow dung + 10L cow urine + 2kg jaggery + 2kg gram/pulse flour + 1 handful soil from old banyan/peepal tree",
        "method": "Mix in drum, stir twice daily, ferment for 7-10 days under shade. Use 200L per acre as soil drench or 10% foliar spray.",
        "frequency": "Once every 2 weeks or after every irrigation",
    },
    "beejamrut": {
        "name": "Beejamrut (बीजामृत)",
        "purpose": "Seed treatment to prevent seed-borne diseases, improve germination",
        "ingredients": "5L water + 250g fresh cow dung + 250ml cow urine + 50g lime + 1 handful soil",
        "method": "Mix all, stir well, let settle 30 min. Soak seeds for 6-12 hours or coat and dry in shade.",
        "frequency": "Once before every planting",
    },
    "panchagavya": {
        "name": "Panchagavya (पंचगव्य)",
        "purpose": "Growth promoter, immunity booster, pest deterrent",
        "ingredients": "5 cow products: 3kg cow dung + 2L cow urine + 2L milk + 2L curd + 500g ghee",
        "method": "Mix dung + ghee, ferment 3 days. Add other products, ferment 30 days stirring daily. Use at 3% concentration.",
        "frequency": "Spray every 15 days throughout crop season",
    },
    "neem_spray": {
        "name": "Neem Oil Spray",
        "purpose": "Broad-spectrum pest control, fungal prevention",
        "ingredients": "1L water + 5ml cold-pressed neem oil + 2ml liquid soap (emulsifier)",
        "method": "Mix soap in water first, then add neem oil, shake well. Spray in evening or early morning.",
        "frequency": "Every 5-7 days for prevention; every 3 days during active infestation",
    },
    "dashparni_ark": {
        "name": "Dashparni Ark (दशपर्णी अर्क)",
        "purpose": "Multi-pest repellent using 10 bitter plant leaves",
        "ingredients": "10 types of bitter leaves: neem + papaya + custard apple + pomegranate + guava + bel + drumstick + lantana + calotropis + eucalyptus (1kg each), 200L water, 2L cow urine, 2kg cow dung",
        "method": "Blend leaves, add to water with cow products, ferment 30-40 days stirring daily. Filter and dilute 3L in 100L water for spraying.",
        "frequency": "Every 10 days as preventive spray",
    },
    "cow_urine_spray": {
        "name": "Cow Urine Spray (गौमूत्र)",
        "purpose": "Fungicide, pesticide, micronutrient supplier",
        "ingredients": "1 part fresh cow urine + 7-8 parts water",
        "method": "Dilute and spray. Can also add 10g neem leaves powder per liter.",
        "frequency": "Twice weekly for prevention; every 2 days for active issues",
    },
}

MULTILEVEL_FARMING = {
    "description": "Grow 4-5 crops simultaneously at different vertical heights to maximize income, biodiversity, and ecological balance on the same land area.",
    "principle": "Mimics natural forest structure — tall trees, medium trees, shrubs, ground cover, and root crops all growing together.",
    "layers": {
        "Canopy (15-25 ft)": "Coconut, Teak, Mango, Jackfruit, Bamboo",
        "Sub-canopy (8-15 ft)": "Banana, Papaya, Drumstick (Moringa), Guava, Lemon",
        "Shrub (3-8 ft)": "Tomato, Chilli, Brinjal, Capsicum, Coffee, Cardamom",
        "Ground Cover (0-3 ft)": "Turmeric, Ginger, Leafy greens, Watermelon, Pumpkin",
        "Root Layer": "Yam, Colocasia, Beetroot, Radish, Groundnut",
        "Climbers (vertical)": "Beans, Cucumber, Bitter gourd, Bottle gourd (on natural/bamboo supports)",
    },
    "income_example": "1 acre multilevel farm: Coconut ₹40,000 + Banana ₹30,000 + Turmeric ₹50,000 + Vegetables ₹20,000 = ₹1,40,000/year vs ₹50,000 monoculture",
    "benefits": [
        "3-5x more income from same land",
        "Natural pest control (biodiversity reduces outbreaks)",
        "Year-round income (different harvest times)",
        "Soil health improvement (different root depths, leaf mulch)",
        "Reduced input costs (less irrigation, fertilizer needed)",
        "Climate resilience (multiple crops = risk distribution)",
    ],
    "getting_started": [
        "Start with existing crops — add multilevel components gradually",
        "Plant banana + drumstick as quick-return medium layer first",
        "Grow turmeric/ginger in shade of medium layer",
        "Add coconut/mango as long-term investment",
        "Use farm boundaries for bamboo/teak as border crop",
    ],
}

GOVERNMENT_SCHEMES = {
    "PM-KISAN": {
        "full_name": "Pradhan Mantri Kisan Samman Nidhi",
        "benefit": "₹6,000/year in 3 installments of ₹2,000 directly to bank account",
        "eligibility": "Small and marginal farmers with less than 2 hectares land",
        "apply": "pmkisan.gov.in or nearest CSC center, Aadhaar + land records needed",
        "helpline": "155261",
    },
    "PKVY": {
        "full_name": "Paramparagat Krishi Vikas Yojana",
        "benefit": "₹50,000/hectare/3 years for transitioning to organic farming",
        "eligibility": "Farmer clusters of min. 50 farmers / 50 acres for organic certification",
        "apply": "Through District Agriculture Office or State Organic Mission",
        "helpline": "Contact State Agriculture Department",
    },
    "PM_FASAL_BIMA": {
        "full_name": "Pradhan Mantri Fasal Bima Yojana",
        "benefit": "Crop insurance: 2% premium for Kharif, 1.5% for Rabi, 5% for horticulture",
        "eligibility": "All farmers growing notified crops in notified areas",
        "apply": "pmfby.gov.in or bank/insurance company before crop season",
        "helpline": "1800-200-7710",
    },
    "KCC": {
        "full_name": "Kisan Credit Card",
        "benefit": "Low-interest credit (4-7%) up to ₹3 lakh for farming needs",
        "eligibility": "All farmers with land records",
        "apply": "Nearest bank with land records and Aadhaar",
        "helpline": "Contact your bank",
    },
    "eNAM": {
        "full_name": "National Agriculture Market",
        "benefit": "Online trading platform — get best pan-India mandi prices",
        "eligibility": "All registered farmers",
        "apply": "enam.gov.in, register your produce for transparent bidding",
        "helpline": "1800-270-0224",
    },
}

SEASONAL_CALENDAR = {
    "Kharif (June-October)": ["Rice", "Maize", "Cotton", "Soybean", "Sugarcane", "Groundnut", "Turmeric", "Ginger"],
    "Rabi (Nov-March)": ["Wheat", "Mustard", "Peas", "Chickpea (Chana)", "Potato", "Onion", "Tomato"],
    "Zaid (March-June)": ["Watermelon", "Muskmelon", "Cucumber", "Bitter gourd", "Okra", "Maize (summer)"],
    "Year-round": ["Banana", "Coconut", "Papaya", "Drumstick", "Leafy greens", "Chilli"],
}


def get_context(query: str) -> str:
    """
    Keyword-based RAG: returns relevant knowledge for the query.
    Returns at most 3 knowledge chunks to keep LLM context focused.
    """
    q = query.lower()
    chunks = []

    # Disease matching
    for disease_key, disease in DISEASES.items():
        if any(kw in q for kw in disease["keywords"]):
            chunks.append(
                f"[Disease: {disease_key.replace('_', ' ').title()}]\n"
                f"Symptoms: {disease['symptoms']}\n"
                f"Organic Remedy:\n{disease['remedy']}\n"
                f"Prevention: {disease['prevention']}"
            )

    # Remedy matching
    remedy_triggers = ["spray", "remedy", "treatment", "organic", "jeevamrut", "beejamrut",
                       "panchagavya", "neem", "cow urine", "dashparni", "natural"]
    if any(t in q for t in remedy_triggers):
        for remedy_key, remedy in ORGANIC_REMEDIES.items():
            if remedy_key.replace("_", " ") in q or any(t in q for t in [remedy_key, remedy["name"].split()[0].lower()]):
                chunks.append(
                    f"[Remedy: {remedy['name']}]\n"
                    f"Purpose: {remedy['purpose']}\n"
                    f"Ingredients: {remedy['ingredients']}\n"
                    f"Method: {remedy['method']}\n"
                    f"Frequency: {remedy['frequency']}"
                )

    # Multilevel farming
    ml_triggers = ["multilevel", "multi-level", "layer", "companion", "multiple crop", "intercrop", "mixed crop", "agroforest"]
    if any(t in q for t in ml_triggers):
        ml = MULTILEVEL_FARMING
        layer_text = "\n".join([f"  {layer}: {crops}" for layer, crops in ml["layers"].items()])
        chunks.append(
            f"[Multilevel Farming]\n"
            f"{ml['description']}\n"
            f"Layers:\n{layer_text}\n"
            f"Income example: {ml['income_example']}\n"
            f"Benefits: {'; '.join(ml['benefits'][:3])}"
        )

    # Government schemes
    scheme_triggers = ["scheme", "subsidy", "government", "yojana", "pm-kisan", "pkvy", "insurance", "loan", "credit", "enam"]
    if any(t in q for t in scheme_triggers):
        for scheme_key, scheme in GOVERNMENT_SCHEMES.items():
            if scheme_key.lower() in q or scheme["full_name"].lower() in q or any(t in q for t in scheme_triggers[:4]):
                chunks.append(
                    f"[Scheme: {scheme['full_name']}]\n"
                    f"Benefit: {scheme['benefit']}\n"
                    f"Eligibility: {scheme['eligibility']}\n"
                    f"Apply: {scheme['apply']}"
                )

    # Seasonal calendar
    if any(t in q for t in ["season", "sow", "plant when", "kharif", "rabi", "zaid", "when to grow"]):
        season_text = "\n".join([f"  {s}: {', '.join(c[:5])}" for s, c in SEASONAL_CALENDAR.items()])
        chunks.append(f"[Seasonal Calendar]\n{season_text}")

    # Seed & variety guidance
    seed_triggers = ["seed", "variety", "sow", "planting", "germination", "hybrid", "desi", "seed rate",
                     "spacing", "depth", "nursery", "transplant", "beejamrut"]
    if any(t in q for t in seed_triggers):
        from modules import seeds as seeds_mod
        for crop_name in seeds_mod.crop_list():
            if crop_name in q:
                guide = seeds_mod.get_seed_guide(crop_name)
                if guide:
                    top = guide["varieties"][0] if guide["varieties"] else {}
                    chunks.append(
                        f"[Seed Guide: {crop_name.title()}]\n"
                        f"Season: {guide['season']} | Sowing: {guide['sowing_window']}\n"
                        f"Seed rate: {guide['seed_rate']} | Spacing: {guide['spacing']}\n"
                        f"Duration: {guide['duration']} | Water: {guide['water_needs']}\n"
                        f"Best variety: {top.get('name','N/A')} — Yield: {top.get('yield','N/A')} | {top.get('strength','')}"
                    )

    # Financial & subsidy guidance
    finance_triggers = ["cost", "profit", "income", "revenue", "subsidy", "scheme", "loan", "credit",
                        "financial", "budget", "expense", "pm-kisan", "pkvy", "nfsm", "kcc", "seed subsidy"]
    if any(t in q for t in finance_triggers):
        from modules import seeds as seeds_mod
        scheme_text = "\n".join(
            f"• {s['name']}: {s['benefit']} ({s['amount']})"
            for s in seeds_mod.CENTRAL_SCHEMES[:4]
        )
        chunks.append(f"[Government Seed & Farm Subsidies]\n{scheme_text}")

    # Natural farming education topics
    edu_triggers = ["learn", "teach", "explain", "what is", "how does", "education", "training",
                    "zbnf", "zero budget", "palekar", "waaphasa", "mulch", "water conservation",
                    "post harvest", "value addition", "store", "grading", "sell", "market"]
    if any(t in q for t in edu_triggers):
        from modules import education as edu_mod
        matched = edu_mod.search_topics(q)
        for key in matched[:2]:
            ctx = edu_mod.get_context_for_llm(key)
            if ctx:
                chunks.append(ctx)

    return "\n\n".join(chunks[:3])  # Top 3 relevant chunks
