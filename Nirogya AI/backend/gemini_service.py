"""
Nirogya AI - Live Google Gemini AI Integration Engine
Provides real-time Generative AI capabilities for:
- Clinical record entity extraction & reasoning
- Empathetic plain-language patient explanations in 6 Indian languages
- Real-time conversational Health Copilot grounded in patient medical history
- Dynamic fallback to local clinical NLP when API key is not provided
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
import requests

logger = logging.getLogger("nirogya.gemini")

KEY_STORAGE_FILE = os.path.join(os.path.dirname(__file__), ".gemini_key")


class GeminiService:
    _api_key: Optional[str] = None

    @classmethod
    def get_api_key(cls) -> Optional[str]:
        if cls._api_key:
            return cls._api_key
        # Check environment variable
        env_key = os.environ.get("GEMINI_API_KEY", "").strip()
        if env_key:
            cls._api_key = env_key
            return env_key
        # Check persisted file
        if os.path.exists(KEY_STORAGE_FILE):
            try:
                with open(KEY_STORAGE_FILE, "r", encoding="utf-8") as f:
                    saved = f.read().strip()
                    if saved:
                        cls._api_key = saved
                        return saved
            except Exception as e:
                logger.warning(f"Could not read saved key: {e}")
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
            logger.warning(f"Could not persist key: {e}")

        # Test validation if key provided
        valid = False
        message = "Key cleared. Built-in Clinical NLP engine active."
        if cleaned:
            test_res = cls.test_connection(cleaned)
            valid = test_res.get("success", False)
            message = test_res.get("message", "API key configured.")

        return {
            "has_key": bool(cleaned),
            "is_valid": valid,
            "message": message,
            "engine": "Google Gemini 2.5 Flash" if valid else "Nirogya Built-in Clinical Engine"
        }

    @classmethod
    def get_status(cls) -> Dict[str, Any]:
        key = cls.get_api_key()
        has_key = bool(key)
        return {
            "has_key": has_key,
            "engine": "Google Gemini 2.5 Flash" if has_key else "Nirogya Built-in Clinical Engine",
            "model": "gemini-2.5-flash",
            "status": "LIVE_ACTIVE" if has_key else "BUILTIN_ACTIVE",
            "instructions": "Get a free Google Gemini API key at https://aistudio.google.com/app/apikey to unlock full generative AI capabilities."
        }

    @classmethod
    def test_connection(cls, key: str) -> Dict[str, Any]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}"
        payload = {
            "contents": [{
                "parts": [{"text": "Reply with 'HEALTH_READY' if you are active."}]
            }]
        }
        try:
            res = requests.post(url, json=payload, timeout=8)
            if res.status_code == 200:
                return {"success": True, "message": "Gemini API connected successfully! Live Generative AI is active."}
            else:
                err_text = res.text[:200]
                # Try fallback model gemini-1.5-flash
                fallback_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
                res2 = requests.post(fallback_url, json=payload, timeout=8)
                if res2.status_code == 200:
                    return {"success": True, "message": "Gemini 1.5 Flash connected successfully!"}
                return {"success": False, "message": f"API key error (HTTP {res.status_code}): {err_text}"}
        except Exception as e:
            return {"success": False, "message": f"Connection error: {str(e)}"}

    @classmethod
    def chat_completion(
        cls,
        user_message: str,
        patient_profile: Dict[str, Any],
        active_document: Optional[Dict[str, Any]] = None,
        language: str = "en"
    ) -> Optional[str]:
        """Calls Gemini API for conversational copilot if key is available, else returns None"""
        key = cls.get_api_key()
        if not key:
            return None

        # Assemble rich clinical system context
        doc_details = ""
        if active_document:
            parsed = active_document.get("parsed_data", {})
            tests = parsed.get("lab_tests", [])
            meds = parsed.get("medications", [])
            doc_details = f"""
Active Document: {active_document.get('title', 'Unknown')} (Date: {active_document.get('doc_date', 'N/A')}, Provider: {active_document.get('provider', 'N/A')})
Lab Tests Recorded:
{json.dumps(tests, indent=2) if tests else "None"}
Medications Recorded:
{json.dumps(meds, indent=2) if meds else "None"}
"""

        system_instruction = f"""
You are Nirogya AI, an empathetic, highly knowledgeable Personal Health Copilot and medical educator for Indian patients.
The current patient is:
- Name: {patient_profile.get('name', 'Patient')}
- Age: {patient_profile.get('age', 50)} Y
- Gender: {patient_profile.get('gender', 'Unknown')}
- Blood Group: {patient_profile.get('blood_group', 'Unknown')}
- ABHA ID: {patient_profile.get('abha_number', 'N/A')}
- Known Health Conditions: {patient_profile.get('condition_summary', 'General Health Care')}

{doc_details}

Rules:
1. Explain medical terms, biomarkers, and medications in simple, reassuring plain language (8th-grade reading level).
2. Use relatable analogies (e.g., comparing HbA1c to a 3-month engine heat gauge, or kidneys to home water filtration).
3. If the user asks in Hindi, reply in clear, natural Hindi with polite tone (आप). If they ask in another Indian language (te, ta, mr, bn), reply in that language or English as appropriate.
4. Include: What this means, Actionable lifestyle / diet tips, and 2-3 specific questions they can ask their doctor.
5. ALWAYS add a subtle safety disclaimer: 'This is educational health guidance. Please consult your physician before making medical changes.'
6. Use clean Markdown formatting with bolding and bullet points. Keep responses focused and readable.
"""

        lang_instruction = f"Reply in {language} language." if language != "en" else "Reply in clear English."

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": f"{system_instruction}\n\nUser Question: {user_message}\n\n{lang_instruction}"}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 1000
            }
        }

        # Try gemini-2.5-flash then gemini-1.5-flash
        models = ["gemini-2.5-flash", "gemini-1.5-flash"]
        for m in models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={key}"
            try:
                res = requests.post(url, json=payload, timeout=12)
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            return parts[0].get("text", "")
            except Exception as e:
                logger.warning(f"Error querying {m}: {e}")
                continue

        return None
