"""
Multilingual support layer.

v1 scope (per project scoping decision in Milestone 1): English, Hindi,
Hinglish fully supported. Additional languages (Marathi, Gujarati, Tamil,
Telugu, Punjabi, Kannada, Bengali, Malayalam) are architected for — the
`SUPPORTED_LANGUAGES` registry and the RAG pipeline's `language` filter
already support N languages — but need native-speaker-reviewed content and
translated emergency copy before being turned on, so they're intentionally
left disabled here rather than shipped with unverified machine translation
for safety-critical emergency text.
"""

SUPPORTED_LANGUAGES = {
    "en": {"label": "English", "enabled": True},
    "hi": {"label": "हिन्दी (Hindi)", "enabled": True},
    "hi-en": {"label": "Hinglish", "enabled": True},
    "mr": {"label": "मराठी (Marathi)", "enabled": False},
    "gu": {"label": "ગુજરાતી (Gujarati)", "enabled": False},
    "ta": {"label": "தமிழ் (Tamil)", "enabled": False},
    "te": {"label": "తెలుగు (Telugu)", "enabled": False},
    "pa": {"label": "ਪੰਜਾਬੀ (Punjabi)", "enabled": False},
    "kn": {"label": "ಕನ್ನಡ (Kannada)", "enabled": False},
    "bn": {"label": "বাংলা (Bengali)", "enabled": False},
    "ml": {"label": "മലയാളം (Malayalam)", "enabled": False},
}

DEFAULT_LANGUAGE = "en"

# Emergency response text must be human-translated and clinically reviewed
# per language before going live — this is why it's a static lookup table,
# never machine-translated at request time.
EMERGENCY_RESPONSES = {
    "en": (
        "This sounds like it may be a medical emergency. Please act now:\n\n"
        "• Call 112 (National Emergency) or 108 (Ambulance) immediately.\n"
        "• If possible, go to the nearest hospital or Primary Health Centre right away.\n"
        "• If this involves thoughts of self-harm, you can also call the KIRAN helpline: "
        "1800-599-0019 (24/7, free).\n\n"
        "This assistant provides educational information only and cannot help in an "
        "emergency — please contact emergency services or a qualified professional now."
    ),
    "hi": (
        "यह एक चिकित्सा आपातकाल हो सकता है। कृपया अभी कार्रवाई करें:\n\n"
        "• तुरंत 112 (राष्ट्रीय आपातकाल) या 108 (एम्बुलेंस) पर कॉल करें।\n"
        "• यदि संभव हो, तो तुरंत नजदीकी अस्पताल या प्राथमिक स्वास्थ्य केंद्र जाएं।\n"
        "• यदि इसमें आत्म-हानि के विचार शामिल हैं, तो आप किरण हेल्पलाइन पर भी कॉल कर सकते हैं: "
        "1800-599-0019 (24/7, नि:शुल्क)।\n\n"
        "यह सहायक केवल शैक्षिक जानकारी प्रदान करता है और आपातकाल में मदद नहीं कर सकता — कृपया "
        "अभी आपातकालीन सेवाओं या किसी योग्य पेशेवर से संपर्क करें।"
    ),
    "hi-en": (
        "Yeh ek medical emergency ho sakti hai. Please abhi action lein:\n\n"
        "• Turant 112 (National Emergency) ya 108 (Ambulance) par call karein.\n"
        "• Agar possible ho, to nearest hospital ya Primary Health Centre turant jaayein.\n"
        "• Agar self-harm ke thoughts hain, to KIRAN helpline par bhi call kar sakte hain: "
        "1800-599-0019 (24/7, free).\n\n"
        "Yeh assistant sirf educational information deta hai aur emergency mein madad nahi "
        "kar sakta — please abhi emergency services ya qualified professional se contact karein."
    ),
}


def is_language_enabled(language_code: str) -> bool:
    lang = SUPPORTED_LANGUAGES.get(language_code)
    return bool(lang and lang["enabled"])


def resolve_language(requested: str) -> str:
    """Falls back to default if requested language isn't enabled — never
    silently serves an unreviewed/disabled language."""
    return requested if is_language_enabled(requested) else DEFAULT_LANGUAGE


def get_emergency_response(language: str) -> str:
    resolved = resolve_language(language)
    return EMERGENCY_RESPONSES.get(resolved, EMERGENCY_RESPONSES[DEFAULT_LANGUAGE])
