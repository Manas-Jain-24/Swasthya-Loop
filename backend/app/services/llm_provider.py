import os
import logging
from typing import Optional, List
from pathlib import Path

logger = logging.getLogger("swasthya_llm")

def get_gemini_api_key() -> Optional[str]:
    key = os.environ.get("GEMINI_API_KEY")
    if key and key.strip():
        return key.strip()

    env_file = Path(__file__).resolve().parent.parent.parent.parent / ".env"
    if env_file.exists():
        try:
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("GEMINI_API_KEY="):
                        k = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if k:
                            os.environ["GEMINI_API_KEY"] = k
                            return k
        except Exception as e:
            logger.error(f"Error reading .env: {e}")
    return None

CANDIDATE_MODELS = [
    "gemini-3.8-flash",
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash"
]

def test_gemini_connection(api_key: str) -> bool:
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=api_key)
        for model in CANDIDATE_MODELS:
            try:
                resp = client.models.generate_content(
                    model=model,
                    contents="Say OK",
                    config=types.GenerateContentConfig(
                        thinking_config=types.ThinkingConfig(thinking_budget=0)
                    )
                )
                if resp and resp.text:
                    return True
            except Exception:
                try:
                    resp = client.models.generate_content(
                        model=model,
                        contents="Say OK"
                    )
                    if resp and resp.text:
                        return True
                except Exception:
                    continue
        return False
    except Exception:
        return False

def generate_plain_language_summary(facts: List[str], condition_name: str) -> Optional[str]:
    api_key = get_gemini_api_key()
    if not api_key:
        return None

    prompt = (
        "You are SwasthyaLoop's compassionate plain-language health summary assistant.\n"
        f"The patient is managing: {condition_name}.\n"
        "Summarize ONLY these structured clinical follow-up facts in an encouraging, clear paragraph for the patient:\n"
        + "\n".join(f"- {f}" for f in facts) +
        "\n\nSTRICT CLINICAL SAFETY RULES:\n"
        "- Do NOT provide medical diagnoses or interpret clinical severity.\n"
        "- Do NOT prescribe, recommend, or modify any medications or dosages.\n"
        "- Only speak to the facts listed above.\n"
        "- Keep the response under 100 words in friendly, empathetic language.\n"
    )

    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=api_key)
        for model in CANDIDATE_MODELS:
            response = None
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        thinking_config=types.ThinkingConfig(thinking_budget=0)
                    )
                )
            except Exception:
                try:
                    response = client.models.generate_content(
                        model=model,
                        contents=prompt
                    )
                except Exception:
                    continue

            if response and response.text:
                candidate = response.text.strip()
                forbidden_tokens = ["prescribe", "diagnosis", "dosage", "mg of", "take more", "cure"]
                violating = [token for token in forbidden_tokens if token in candidate.lower()]
                if violating:
                    return None
                return candidate
        return None
    except Exception:
        return None
