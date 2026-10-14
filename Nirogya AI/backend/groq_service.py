"""
Nirogya AI - Groq AI Integration Engine
Provides ultra-fast LLM inference via Groq Cloud for:
- Empathetic plain-language patient health explanations in English & Indian languages
- Real-time conversational Medical Health Copilot grounded in patient history
- Dynamic fallback to built-in Clinical NLP when API key is not available
"""

import os
import json
import logging
from typing import Dict, Any, Optional
import requests

logger = logging.getLogger("nirogya.groq")

KEY_STORAGE_FILE = os.path.join(os.path.dirname(__file__), ".groq_key")

# Default Groq model — fast and medically capable
GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_API_BASE = "https://api.groq.com/openai/v1/chat/completions"


class GroqService:
    _api_key: Optional[str] = None

    # ── Key Management ────────────────────────────────────────────────────────

    @classmethod
    def get_api_key(cls) -> Optional[str]:
        if cls._api_key:
            return cls._api_key
        # Environment variable takes priority
        env_key = os.environ.get("GROQ_API_KEY", "").strip()
        if env_key:
            cls._api_key = env_key
            return env_key
        # Persisted key file
        if os.path.exists(KEY_STORAGE_FILE):
            try:
                with open(KEY_STORAGE_FILE, "r", encoding="utf-8") as f:
                    saved = f.read().strip()
                    if saved:
                        cls._api_key = saved
                        return saved
            except Exception as e:
                logger.warning(f"Could not read saved Groq key: {e}")
        return None

    @classmethod
    def set_api_key(cls, key: str) -> Dict[str, Any]:
        cleaned = key.strip()
        cls._api_key = cleaned if cleaned else None
        try:
            if cleaned:
                with open(KEY_STORAGE_FILE, "w", encoding="utf-8") as f:
                    f.write(cleaned)
            elif os.path.exists(KEY_STORAGE_FILE):
                os.remove(KEY_STORAGE_FILE)
        except Exception as e:
            logger.warning(f"Could not persist Groq key: {e}")

        valid = False
        message = "Key cleared. Built-in Clinical NLP engine active."
        if cleaned:
            test_res = cls.test_connection(cleaned)
            valid = test_res.get("success", False)
            message = test_res.get("message", "Groq API key configured.")

        return {
            "has_key": bool(cleaned),
            "is_valid": valid,
            "message": message,
            "engine": f"Groq ({GROQ_MODEL})" if valid else "Nirogya Built-in Clinical Engine"
        }

    @classmethod
    def get_status(cls) -> Dict[str, Any]:
        key = cls.get_api_key()
        has_key = bool(key)
        return {
            "has_key": has_key,
            "engine": f"Groq ({GROQ_MODEL})" if has_key else "Nirogya Built-in Clinical Engine",
            "model": GROQ_MODEL,
            "status": "LIVE_ACTIVE" if has_key else "BUILTIN_ACTIVE",
            "instructions": (
                "Get a free Groq API key at https://console.groq.com to unlock "
                "ultra-fast generative AI health explanations."
            )
        }

    # ── Connection Test ───────────────────────────────────────────────────────

    @classmethod
    def test_connection(cls, key: str) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": GROQ_MODEL,
            "messages": [
                {"role": "user", "content": "Reply with HEALTH_READY if you are active."}
            ],
            "max_tokens": 20,
            "temperature": 0
        }
        try:
            res = requests.post(GROQ_API_BASE, headers=headers, json=payload, timeout=10)
            if res.status_code == 200:
                return {"success": True, "message": f"Groq API connected! Model: {GROQ_MODEL}"}
            err = res.text[:200]
            return {"success": False, "message": f"Groq API error (HTTP {res.status_code}): {err}"}
        except Exception as e:
            return {"success": False, "message": f"Groq connection error: {str(e)}"}

    # ── Chat Completion ───────────────────────────────────────────────────────

    @classmethod
    def chat_completion(
        cls,
        user_message: str,
        patient_profile: Dict[str, Any],
        active_document: Optional[Dict[str, Any]] = None,
        language: str = "en"
    ) -> Optional[str]:
        """
        Calls Groq API for conversational copilot if key is available.
        Returns the assistant reply string, or None if unavailable.
        """
        key = cls.get_api_key()
        if not key:
            return None

        # Assemble rich clinical context
        doc_details = ""
        if active_document:
            parsed = active_document.get("parsed_data", {})
            tests = parsed.get("lab_tests", [])
            meds = parsed.get("medications", [])
            doc_details = (
                f"\nActive Document: {active_document.get('title', 'Unknown')} "
                f"(Date: {active_document.get('doc_date', 'N/A')}, "
                f"Provider: {active_document.get('provider', 'N/A')})\n"
                f"Lab Tests:\n{json.dumps(tests, indent=2) if tests else 'None'}\n"
                f"Medications:\n{json.dumps(meds, indent=2) if meds else 'None'}\n"
            )

        lang_note = f"Reply in {language} language." if language != "en" else "Reply in clear English."

        system_prompt = (
            "You are Nirogya AI, an empathetic, highly knowledgeable Personal Health Copilot "
            "and medical educator for Indian patients.\n\n"
            f"Current patient:\n"
            f"- Name: {patient_profile.get('name', 'Patient')}\n"
            f"- Age: {patient_profile.get('age', 50)} years\n"
            f"- Gender: {patient_profile.get('gender', 'Unknown')}\n"
            f"- Blood Group: {patient_profile.get('blood_group', 'Unknown')}\n"
            f"- ABHA ID: {patient_profile.get('abha_number', 'N/A')}\n"
            f"- Known Conditions: {patient_profile.get('condition_summary', 'General Health Care')}\n"
            f"{doc_details}\n"
            "Rules:\n"
            "1. Explain medical terms, biomarkers, and medications in simple, reassuring plain language (8th-grade reading level).\n"
            "2. Use relatable analogies (e.g., HbA1c as a 3-month engine heat gauge, kidneys as home water filters).\n"
            "3. If the user writes in Hindi, reply in clear, natural Hindi with polite aap tone.\n"
            "4. Always include: What it means | Actionable lifestyle/diet tips | 2-3 questions to ask their doctor.\n"
            "5. End with: 'This is educational health guidance. Please consult your physician before making medical changes.'\n"
            "6. Use clean Markdown with bold headings and bullet points. Keep responses focused and readable.\n\n"
            f"{lang_note}"
        )

        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": GROQ_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.35,
            "max_tokens": 1024
        }

        try:
            res = requests.post(GROQ_API_BASE, headers=headers, json=payload, timeout=15)
            if res.status_code == 200:
                data = res.json()
                choices = data.get("choices", [])
                if choices:
                    return choices[0].get("message", {}).get("content", "")
            logger.warning(f"Groq API returned HTTP {res.status_code}: {res.text[:200]}")
        except Exception as e:
            logger.warning(f"Groq chat_completion error: {e}")

        return None
