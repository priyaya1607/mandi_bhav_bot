import re
from typing import Dict, Optional, Tuple

COMMODITY_ALIASES = {
    "Tomato": [
        "tomato", "tomatoes", "tamatar", "tamaatar", "tamater", "tamatar ka", "tamatar bhav"
    ],
    "Potato": [
        "potato", "potatoes", "aloo", "alu", "batata", "aaloo", "aloo ka"
    ],
    "Onion": [
        "onion", "onions", "pyaz", "pyaaz", "piyaz", "kanda", "pyaz ka"
    ]
}

MANDI_ALIASES = {
    "Lucknow": ["lucknow", "lko", "lakhnau", "lucknow mandi", "lko mandi"],
    "Kanpur": ["kanpur", "knp", "kanpur mandi"],
    "Agra": ["agra", "taj city", "agra mandi"]
}

INTENT_KEYWORDS = {
    "price_forecast": [
        "forecast", "future", "anumaan", "agle hafte", "next 7 days", "prediction",
        "kal ka", "aane wale", "aage", "estimate"
    ],
    "price_history": [
        "history", "historical", "past", "pichle", "pichla", "purana", "record",
        "records", "pehle"
    ],
    "price_trend": [
        "trend", "badh raha", "ghat raha", "movement", "utav-chadhaw", "up", "down"
    ],
    "latest_price": [
        "bhav", "rate", "price", "daam", "kya hai", "latest", "aaj ka", "current",
        "kitna", "mandi bhav"
    ]
}


def normalize_text(text: str) -> str:
    """Lowercases and cleans punctuation."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    return " ".join(text.split())


def extract_commodity(normalized: str) -> Optional[str]:
    """Extracts canonical commodity name from text."""
    for canonical, aliases in COMMODITY_ALIASES.items():
        for alias in aliases:
            pattern = rf"\b{re.escape(alias)}\b"
            if re.search(pattern, normalized):
                return canonical
    return None


def extract_mandi(normalized: str) -> Optional[str]:
    """Extracts canonical mandi name from text."""
    for canonical, aliases in MANDI_ALIASES.items():
        for alias in aliases:
            pattern = rf"\b{re.escape(alias)}\b"
            if re.search(pattern, normalized):
                return canonical
    return None


def extract_intent(normalized: str) -> str:
    """Extracts query intent."""
    for intent, keywords in INTENT_KEYWORDS.items():
        for kw in keywords:
            if kw in normalized:
                return intent
    return "latest_price"


def parse_query(user_query: str) -> Dict[str, Optional[str]]:
    """
    Parses a user query into structured components:
    - commodity: "Tomato", "Potato", "Onion", or None
    - mandi: "Lucknow", "Kanpur", "Agra", or None
    - intent: "latest_price", "price_forecast", "price_history", "price_trend"
    """
    normalized = normalize_text(user_query)
    commodity = extract_commodity(normalized)
    mandi = extract_mandi(normalized)
    intent = extract_intent(normalized)

    # Default to Lucknow if query mentions Mandi without explicit city
    if mandi is None and "mandi" in normalized:
        mandi = "Lucknow"

    return {
        "raw_query": user_query,
        "commodity": commodity,
        "mandi": mandi,
        "intent": intent,
        "is_complete": (commodity is not None and mandi is not None)
    }
