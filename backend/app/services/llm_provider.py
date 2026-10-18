import os
from typing import Optional, List
import urllib.request
import json

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def generate_plain_language_summary(facts: List[str], condition_name: str) -> Optional[str]:
    """
    Attempts to use Gemini REST API if GEMINI_API_KEY is present in environment.
    Strictly constrained: rewrites only provided structured facts.
    Returns None if key is missing, network error, or safety violation.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    prompt = (
        "You are SwasthyaLoop's plain-language health summary assistant.\n"
        "Summarize ONLY these structured follow-up facts in a reassuring, clear paragraph for the patient:\n"
        + "\n".join(f"- {f}" for f in facts) +
        "\n\nSTRICT SAFETY CONSTRAINTS:\n"
        "- Do NOT diagnose or interpret medical severity.\n"
        "- Do NOT recommend medications, dosage changes, or treatments.\n"
        "- Keep response under 100 words.\n"
    )

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 200
        }
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            result = json.loads(response.read().decode("utf-8"))
            candidate = result["candidates"][0]["content"]["parts"][0]["text"].strip()
            
            # Safety suppression check
            forbidden_tokens = ["prescribe", "diagnosis", "dosage", "mg of", "take more", "cure"]
            if any(token in candidate.lower() for token in forbidden_tokens):
                return None
            return candidate
    except Exception:
        return None
