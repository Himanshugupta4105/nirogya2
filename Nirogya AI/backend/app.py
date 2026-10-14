"""
Nirogya AI - Personal Health Copilot Backend Application
FastAPI Server providing complete REST APIs for:
- Multi-Patient Profile Management & Dynamic ABHA Credentials
- Real-time Medical Record Ingestion (OCR & Manual Structured Entry)
- Plain-Language Health Explanation Engine & Abnormal Biomarker Flags
- Dynamic Longitudinal Vitals Trend Computation & Health Timeline
- ABDM / ABHA Linking & HL7 FHIR R4 Standard Exchange
- Multi-Language Translation (EN, HI, TE, TA, BN, MR)
- Live Google Gemini AI Integration & Context-Aware Health Copilot
"""

import os
import json
import datetime
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel

from backend.database import init_db, HealthRepository
from backend.ocr_engine import MedicalRecordExtractor, CLINICAL_TEST_DICTIONARY
from backend.clinical_analyzer import ClinicalAnalyzer
from backend.abdm_fhir import AbdmFhirEngine
from backend.translator import TranslationEngine
from backend.sample_data import SAMPLE_RECORDS
from backend.gemini_service import GeminiService
from backend.groq_service import GroqService

# Initialize Database Schema & Seed Data
init_db()

app = FastAPI(
    title="Nirogya AI - Personal Health Copilot",
    description="Multi-Patient Digital Health Intelligence, Dynamic OCR, Longitudinal Vitals, ABDM/FHIR R4 & Google Gemini AI",
    version="2.0.0"
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── PYDANTIC SCHEMAS ─────────────────────────────────────────────────────────

class ChatQuery(BaseModel):
    message: str
    patient_id: Optional[str] = "pat-101"
    doc_id: Optional[str] = None
    language: Optional[str] = "en"


class AbhaGenerateRequest(BaseModel):
    name: str
    year_of_birth: Optional[int] = 1974


class PatientCreateRequest(BaseModel):
    name: str
    age: int
    gender: str
    blood_group: str
    phone: Optional[str] = ""
    condition_summary: Optional[str] = ""
    emergency_contact: Optional[str] = ""


class ManualRecordRequest(BaseModel):
    patient_id: str
    title: str
    doc_type: str  # "lab_report", "prescription", "discharge_summary"
    provider: Optional[str] = "Diagnostic Lab / Clinic"
    doctor_name: Optional[str] = "Consulting Physician"
    doc_date: Optional[str] = None
    raw_text: Optional[str] = ""
    lab_values: Optional[Dict[str, float]] = None
    medications_list: Optional[List[Dict[str, str]]] = None


class GeminiKeyRequest(BaseModel):
    api_key: str


class GroqKeyRequest(BaseModel):
    api_key: str


class OcrKeyRequest(BaseModel):
    api_key: str


# ─── MULTI-PATIENT ENDPOINTS ──────────────────────────────────────────────────

@app.get("/api/patients")
def get_all_patients():
    """Returns list of all registered patients in the system"""
    return HealthRepository.get_all_patients()


@app.post("/api/patients")
def create_new_patient(req: PatientCreateRequest):
    """Registers a new patient, generates verified ABHA credentials, and initializes records"""
    try:
        new_pat = HealthRepository.create_patient(
            name=req.name,
            age=req.age,
            gender=req.gender,
            blood_group=req.blood_group,
            phone=req.phone,
            condition_summary=req.condition_summary,
            emergency_contact=req.emergency_contact
        )
        return {"success": True, "patient": new_pat}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create patient: {str(e)}")


@app.get("/api/patients/{patient_id}")
def get_single_patient(patient_id: str):
    """Returns detailed profile for a specific patient"""
    pat = HealthRepository.get_patient_profile(patient_id)
    if not pat:
        raise HTTPException(status_code=404, detail="Patient not found")
    return pat


@app.delete("/api/patients/{patient_id}")
def delete_patient(patient_id: str):
    """Deletes a patient and their associated health records"""
    success = HealthRepository.delete_patient(patient_id)
    if not success:
        raise HTTPException(status_code=400, detail="Cannot delete default demo patient")
    return {"success": True, "message": "Patient deleted successfully"}


# ─── PATIENT PROFILE, TIMELINE, VITALS, MEDICATIONS ───────────────────────────

@app.get("/api/profile")
def get_patient_profile(patient_id: Optional[str] = Query(None)):
    """Returns patient profile and ABHA credentials for active patient"""
    profile = HealthRepository.get_patient_profile(patient_id)
    return profile


@app.get("/api/timeline")
def get_timeline(patient_id: Optional[str] = Query(None)):
    """Returns chronological timeline of health events for active patient"""
    events = HealthRepository.get_timeline(patient_id)
    return events


@app.get("/api/vitals")
def get_vitals_trends(patient_id: Optional[str] = Query(None)):
    """Returns longitudinal vitals time-series data dynamically calculated from observations"""
    return HealthRepository.get_vitals_history(patient_id)


@app.get("/api/medications")
def get_medications(patient_id: Optional[str] = Query(None)):
    """Returns active medications with dosage, frequency, and instructions for active patient"""
    meds = HealthRepository.get_active_medications(patient_id)
    return meds


@app.get("/api/documents")
def get_documents(patient_id: Optional[str] = Query(None)):
    """Returns list of all indexed medical documents for active patient"""
    return HealthRepository.get_all_documents(patient_id)


@app.get("/api/documents/{doc_id}")
def get_document_details(
    doc_id: str,
    lang: str = Query("en"),
    patient_id: Optional[str] = Query(None)
):
    """Returns structured extraction, plain-language summary, and FHIR bundle for a document"""
    doc = HealthRepository.get_document_by_id(doc_id, patient_id)
    if not doc:
        # Check in memory sample records
        if doc_id in SAMPLE_RECORDS:
            sample = SAMPLE_RECORDS[doc_id]
            doc = {
                "id": doc_id,
                "patient_id": patient_id or "pat-101",
                "title": sample["title"],
                "doc_type": sample["doc_type"],
                "provider": sample["provider"],
                "doctor_name": sample["doctor_name"],
                "doc_date": sample["date"],
                "raw_text": sample["raw_text"],
                "parsed_data": sample["parsed_data"],
                "fhir_bundle": AbdmFhirEngine.convert_to_fhir_bundle(doc_id, sample, {"abha_number": "14-8921-4350-9812", "abha_address": "rajesh.sharma@abdm"})
            }
        else:
            raise HTTPException(status_code=404, detail="Document not found")

    # Generate clinical plain language explanation
    parsed = doc.get("parsed_data", {})
    summary = ClinicalAnalyzer.generate_health_summary(doc.get("doc_type", "lab_report"), parsed)

    # Compute Longitudinal Deltas against baseline
    biomarker_deltas = ClinicalAnalyzer.calculate_biomarker_deltas(parsed.get("lab_tests", []))

    # Compute Drug Interaction Safety Matrix
    drug_interactions = ClinicalAnalyzer.get_drug_interaction_matrix()

    # Generate Personalized Indian Nutrition Guide
    nutrition_plan = ClinicalAnalyzer.get_personalized_nutrition_plan()

    # Translate if regional language requested
    if lang != "en":
        summary = TranslationEngine.translate_summary(summary, lang)

    return {
        "document": doc,
        "summary": summary,
        "biomarker_deltas": biomarker_deltas,
        "drug_interactions": drug_interactions,
        "nutrition_plan": nutrition_plan
    }


# ─── REAL-TIME MANUAL RECORD ENTRY & FILE UPLOAD ──────────────────────────────

@app.post("/api/records/manual-entry")
def create_manual_record(req: ManualRecordRequest):
    """
    Real-time manual health record entry.
    Allows entering lab values, typing/pasting a prescription, or clinical notes directly,
    parsing them dynamically, computing flags, and updating the patient's records.
    """
    try:
        patient = HealthRepository.get_patient_profile(req.patient_id)
        doc_date = req.doc_date or datetime.date.today().isoformat()

        parsed = {
            "diagnoses": [],
            "lab_tests": [],
            "medications": []
        }

        # 1. Parse from raw text if provided
        if req.raw_text and req.raw_text.strip():
            parsed_from_text = MedicalRecordExtractor.parse_document(req.raw_text, req.doc_type)
            parsed["diagnoses"].extend(parsed_from_text.get("diagnoses", []))
            parsed["lab_tests"].extend(parsed_from_text.get("lab_tests", []))
            parsed["medications"].extend(parsed_from_text.get("medications", []))

        # 2. Add structured lab values if provided
        if req.lab_values:
            known_tests = {
                "fbs": {"name": "Fasting Blood Glucose (FBS)", "category": "Diabetology", "unit": "mg/dL", "ref_min": 70.0, "ref_max": 100.0},
                "ppbs": {"name": "Post-Prandial Glucose (PPBS)", "category": "Diabetology", "unit": "mg/dL", "ref_min": 70.0, "ref_max": 140.0},
                "hba1c": {"name": "HbA1c (Glycated Hemoglobin)", "category": "Diabetology", "unit": "%", "ref_min": 4.0, "ref_max": 5.6},
                "systolic": {"name": "Systolic Blood Pressure", "category": "Vitals", "unit": "mmHg", "ref_min": 90.0, "ref_max": 120.0},
                "diastolic": {"name": "Diastolic Blood Pressure", "category": "Vitals", "unit": "mmHg", "ref_min": 60.0, "ref_max": 80.0},
                "cholesterol": {"name": "Total Cholesterol", "category": "Lipid Profile", "unit": "mg/dL", "ref_min": 125.0, "ref_max": 200.0},
                "ldl": {"name": "LDL Cholesterol (Bad)", "category": "Lipid Profile", "unit": "mg/dL", "ref_min": 50.0, "ref_max": 100.0},
                "triglycerides": {"name": "Triglycerides", "category": "Lipid Profile", "unit": "mg/dL", "ref_min": 50.0, "ref_max": 150.0},
                "creatinine": {"name": "Serum Creatinine", "category": "Renal Function", "unit": "mg/dL", "ref_min": 0.7, "ref_max": 1.2},
                "tsh": {"name": "Thyroid Stimulating Hormone (TSH)", "category": "Thyroid", "unit": "uIU/mL", "ref_min": 0.35, "ref_max": 4.94},
                "vitamind": {"name": "Vitamin D3 (25-OH)", "category": "Vitamins", "unit": "ng/mL", "ref_min": 30.0, "ref_max": 100.0},
                "hemoglobin": {"name": "Hemoglobin (Hb)", "category": "CBC", "unit": "g/dL", "ref_min": 12.0, "ref_max": 16.0}
            }

            for key, val in req.lab_values.items():
                k_clean = key.lower().replace(" ", "").replace("_", "")
                meta = known_tests.get(k_clean, {
                    "name": key.title(),
                    "category": "General",
                    "unit": "",
                    "ref_min": 0.0,
                    "ref_max": 100.0
                })
                val_f = float(val)
                is_ab = val_f < meta["ref_min"] or val_f > meta["ref_max"]
                status = "NORMAL"
                if val_f > meta["ref_max"]:
                    status = "HIGH"
                elif val_f < meta["ref_min"]:
                    status = "LOW"

                parsed["lab_tests"].append({
                    "name": meta["name"],
                    "category": meta["category"],
                    "value": val_f,
                    "unit": meta["unit"],
                    "ref_min": meta["ref_min"],
                    "ref_max": meta["ref_max"],
                    "status": status,
                    "is_abnormal": is_ab
                })

        # 3. Add structured medications if provided
        if req.medications_list:
            for m in req.medications_list:
                parsed["medications"].append({
                    "name": m.get("name", "Medication"),
                    "generic": m.get("generic", ""),
                    "dosage": m.get("dosage", "1 Tablet"),
                    "frequency": m.get("frequency", "1 - 0 - 0 (Once daily)"),
                    "timing": m.get("timing", "After food"),
                    "purpose": m.get("purpose", "Therapy"),
                    "instructions_en": m.get("instructions", "Take as directed.")
                })

        # Generate FHIR Bundle
        abha_info = {
            "abha_number": patient.get("abha_number", "14-8921-4350-9812"),
            "abha_address": patient.get("abha_address", "user@abdm")
        }

        fhir = AbdmFhirEngine.convert_to_fhir_bundle("manual-temp", {
            "title": req.title,
            "doc_type": req.doc_type,
            "patient_name": patient.get("name", "Patient"),
            "doctor_name": req.doctor_name,
            "date": doc_date,
            "provider": req.provider,
            "parsed_data": parsed
        }, abha_info)

        # Save to database
        doc_id = HealthRepository.save_new_document(
            patient_id=req.patient_id,
            title=req.title,
            doc_type=req.doc_type,
            provider=req.provider,
            doctor_name=req.doctor_name,
            doc_date=doc_date,
            raw_text=req.raw_text or f"Manual Entry: {req.title}",
            parsed_data=parsed,
            fhir_bundle=fhir
        )

        summary = ClinicalAnalyzer.generate_health_summary(req.doc_type, parsed)

        return {
            "success": True,
            "doc_id": doc_id,
            "title": req.title,
            "parsed_data": parsed,
            "summary": summary,
            "fhir_bundle": fhir
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record manual entry: {str(e)}")


@app.post("/api/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    patient_id: str = Form("pat-101"),
    doc_type_hint: Optional[str] = Form(None),
    provider: Optional[str] = Form("Diagnostic Lab / Clinic"),
    lang: str = Form("en")
):
    """Processes uploaded file with OCR, extracts clinical entities, and generates FHIR + plain summary"""
    try:
        content = await file.read()
        extracted_text = MedicalRecordExtractor.extract_text_from_file(content, file.filename)
        parsed = MedicalRecordExtractor.parse_document(extracted_text, doc_type_hint)

        patient = HealthRepository.get_patient_profile(patient_id)
        abha_info = {
            "abha_number": patient.get("abha_number", "14-8921-4350-9812"),
            "abha_address": patient.get("abha_address", "user@abdm")
        }

        # Title generation
        title = f"{file.filename.split('.')[0].replace('_', ' ').title()} ({parsed['doc_type'].replace('_', ' ').title()})"

        # Generate FHIR Bundle
        fhir = AbdmFhirEngine.convert_to_fhir_bundle("upload-temp", {
            "title": title,
            "doc_type": parsed["doc_type"],
            "patient_name": parsed["patient_name"] or patient.get("name"),
            "doctor_name": parsed["doctor_name"],
            "date": parsed["date"],
            "provider": provider,
            "parsed_data": parsed
        }, abha_info)

        # Save to database
        doc_id = HealthRepository.save_new_document(
            patient_id=patient_id,
            title=title,
            doc_type=parsed["doc_type"],
            provider=provider,
            doctor_name=parsed["doctor_name"],
            doc_date=parsed["date"],
            raw_text=extracted_text,
            parsed_data=parsed,
            fhir_bundle=fhir
        )

        summary = ClinicalAnalyzer.generate_health_summary(parsed["doc_type"], parsed)

        if lang != "en":
            summary = TranslationEngine.translate_summary(summary, lang)

        return {
            "success": True,
            "doc_id": doc_id,
            "title": title,
            "parsed_data": parsed,
            "summary": summary,
            "fhir_bundle": fhir
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")


# ─── AI SETTINGS: GROQ, GEMINI & OCR.SPACE ───────────────────────────────────

# ── Groq AI ──────────────────────────────────────────────────────────────────

@app.get("/api/settings/groq")
def get_groq_status():
    """Returns status of Groq API key and active intelligence engine"""
    return GroqService.get_status()


@app.post("/api/settings/groq")
def set_groq_key(req: GroqKeyRequest):
    """Sets or clears Groq API key with live connection test"""
    return GroqService.set_api_key(req.api_key)


# ── Google Gemini (secondary / fallback) ──────────────────────────────────────

@app.get("/api/settings/gemini")
def get_gemini_status():
    """Returns status of Google Gemini API key and active intelligence engine"""
    return GeminiService.get_status()


@app.post("/api/settings/gemini")
def set_gemini_key(req: GeminiKeyRequest):
    """Sets or clears Google Gemini API key with live connection test"""
    return GeminiService.set_api_key(req.api_key)


# ── OCR.space ─────────────────────────────────────────────────────────────────

_OCR_KEY_FILE = os.path.join(os.path.dirname(__file__), ".ocr_key")
_ocr_api_key: Optional[str] = None


def _get_ocr_key() -> Optional[str]:
    global _ocr_api_key
    if _ocr_api_key:
        return _ocr_api_key
    env_key = os.environ.get("OCR_SPACE_API_KEY", "").strip()
    if env_key:
        _ocr_api_key = env_key
        return env_key
    if os.path.exists(_OCR_KEY_FILE):
        try:
            with open(_OCR_KEY_FILE, "r", encoding="utf-8") as f:
                saved = f.read().strip()
                if saved:
                    _ocr_api_key = saved
                    return saved
        except Exception:
            pass
    return None


@app.get("/api/settings/ocr")
def get_ocr_status():
    """Returns whether OCR.space API key is configured"""
    key = _get_ocr_key()
    return {
        "has_key": bool(key),
        "engine": "OCR.space Cloud OCR" if key else "Nirogya Built-in PDF/Text Extractor",
        "status": "LIVE_ACTIVE" if key else "BUILTIN_ACTIVE"
    }


@app.post("/api/settings/ocr")
def set_ocr_key(req: OcrKeyRequest):
    """Sets or clears the OCR.space API key"""
    global _ocr_api_key
    cleaned = req.api_key.strip()
    _ocr_api_key = cleaned if cleaned else None
    try:
        if cleaned:
            with open(_OCR_KEY_FILE, "w", encoding="utf-8") as f:
                f.write(cleaned)
        elif os.path.exists(_OCR_KEY_FILE):
            os.remove(_OCR_KEY_FILE)
    except Exception as e:
        pass
    return {
        "has_key": bool(cleaned),
        "message": "OCR.space API key saved successfully." if cleaned else "OCR.space key cleared.",
        "engine": "OCR.space Cloud OCR" if cleaned else "Nirogya Built-in PDF/Text Extractor"
    }


# ─── CONVERSATIONAL HEALTH COPILOT ────────────────────────────────────────────

@app.post("/api/copilot/chat")
def copilot_chat(req: ChatQuery):
    """
    Context-aware AI Health Copilot chat.
    Uses Google Gemini 2.5 Flash if API key is provided;
    otherwise seamlessly uses Nirogya AI's built-in Clinical Reasoning Rule Engine.
    """
    query = req.message.strip()
    query_lower = query.lower()
    patient_id = req.patient_id or "pat-101"
    doc_id = req.doc_id
    lang = req.language or "en"

    # Fetch patient profile and document context
    patient = HealthRepository.get_patient_profile(patient_id)
    doc = None
    if doc_id:
        doc = HealthRepository.get_document_by_id(doc_id, patient_id)
        if not doc and doc_id in SAMPLE_RECORDS:
            doc = SAMPLE_RECORDS[doc_id]

    # 1st — Try Groq AI (primary engine)
    groq_reply = GroqService.chat_completion(
        user_message=query,
        patient_profile=patient,
        active_document=doc,
        language=lang
    )
    if groq_reply:
        citations = [f"Nirogya AI Live (Groq LLaMA 3.3) · Patient: {patient.get('name')}"]
        if doc:
            citations.append(f"{doc.get('title', 'Clinical Record')} ({doc.get('doc_date', 'N/A')})")
        return {
            "reply": groq_reply,
            "engine": "Groq (llama-3.3-70b-versatile)",
            "citations": citations
        }

    # 2nd — Try Gemini AI (secondary fallback)
    gemini_reply = GeminiService.chat_completion(
        user_message=query,
        patient_profile=patient,
        active_document=doc,
        language=lang
    )
    if gemini_reply:
        citations = [f"Nirogya AI Live (Gemini 2.5 Flash) · Patient: {patient.get('name')}"]
        if doc:
            citations.append(f"{doc.get('title', 'Clinical Record')} ({doc.get('doc_date', 'N/A')})")
        return {
            "reply": gemini_reply,
            "engine": "Google Gemini 2.5 Flash",
            "citations": citations
        }

    # Fallback to Built-in Clinical Intelligence Reasoning Engine
    doc_title = doc.get("title", "Clinical Record") if doc else "Clinical Record"
    parsed = doc.get("parsed_data", {}) if doc else {}
    lab_tests = parsed.get("lab_tests", [])
    meds = parsed.get("medications", [])

    response_text = ""
    citations = []

    # 1. Questions about HbA1c / Sugar / Diabetes
    if any(k in query_lower for k in ["hba1c", "sugar", "glucose", "diabetes", "fbs", "मधुमेह", "शुगर"]):
        hba1c_test = next((t for t in lab_tests if "hba1c" in t["name"].lower()), None)
        fbs_test = next((t for t in lab_tests if "fasting" in t["name"].lower()), None)

        val_hba1c = hba1c_test["value"] if hba1c_test else 8.8
        val_fbs = fbs_test["value"] if fbs_test else 186.0

        if lang == "hi":
            response_text = (
                f"{patient.get('name', '')} जी के रिकॉर्ड के अनुसार, आपका HbA1c स्तर **{val_hba1c}%** है और फास्टिंग ब्लड ग्लूकोज **{val_fbs} mg/dL** है। "
                f"सामान्य रूप से HbA1c 5.7% से कम होना चाहिए। {val_hba1c}% का अर्थ है कि पिछले 3 महीनों में आपका औसत रक्त शर्करा लगभग 206 mg/dL के आसपास रहा है।\n\n"
                f"**महत्वपूर्ण सलाह:**\n"
                f"1. अपनी डॉक्टर द्वारा सुझाई गई दवा भोजन से पहले नियमित रूप से लें।\n"
                f"2. मीठे खाद्य पदार्थ, कोल्ड ड्रिंक्स और सफेद चावल/मैदे का सेवन कम करें।\n"
                f"3. रोजाना कम से कम 30 मिनट तेज गति से टहलें (Brisk Walk)।"
            )
        else:
            response_text = (
                f"Based on the health records for **{patient.get('name', 'Patient')}**, the HbA1c is **{val_hba1c}%** (target: < 5.7%) "
                f"and Fasting Blood Glucose is **{val_fbs} mg/dL** (target: 70 - 100 mg/dL).\n\n"
                f"**What this means:** HbA1c reflects average blood sugar over the 90-day lifespan of red blood cells. Elevated levels indicate ongoing glycemic stress on blood vessels and kidneys.\n\n"
                f"**Actionable Next Steps:**\n"
                f"• Follow prescribed antidiabetic medications consistently.\n"
                f"• Emphasize low glycemic index whole grains, leafy greens, and lentils.\n"
                f"• Consult your physician regarding glycemic titration."
            )
        citations = [f"{doc_title}", f"Patient: {patient.get('name')}"]

    # 2. Questions about Cholesterol / Lipids
    elif any(k in query_lower for k in ["cholesterol", "lipid", "ldl", "hdl", "triglyceride", "कोलेस्ट्रॉल"]):
        if lang == "hi":
            response_text = (
                f"आपकी लिपिड प्रोफाइल में टोटल कोलेस्ट्रॉल और LDL (खराब कोलेस्ट्रॉल) का स्तर देखा गया है। "
                f"हृदय और धमनियों की सुरक्षा के लिए स्टैटिन दवाएं (जैसे Rosuvastatin या Atorvastatin) रात को सोते समय ली जाती हैं। "
                f"तली हुई चीजें, पाम ऑयल और बेकरी उत्पाद सीमित करें।"
            )
        else:
            response_text = (
                f"Regarding lipid management for **{patient.get('name')}**:\n\n"
                f"Elevated LDL ('bad cholesterol') deposits fatty plaques along arterial walls. Keeping LDL low protects heart and vascular health.\n\n"
                f"**Diet & Lifestyle:** Switch to unrefined cold-pressed oils in moderation, increase soluble fiber (oats, psyllium husk), and stay physically active."
            )
        citations = [f"Lipid Panel · {patient.get('name')}"]

    # 3. Questions about Kidneys / Creatinine
    elif any(k in query_lower for k in ["creatinine", "kidney", "egfr", "renal", "गुर्दा", "किडनी"]):
        if lang == "hi":
            response_text = (
                f"सीरम क्रिएटिनिन गुर्दे (किडनी) की कार्यप्रणाली को दर्शाता है। "
                f"पर्याप्त मात्रा में पानी पिएं (दिन में 2-2.5 लीटर) और बिना डॉक्टर की सलाह के दर्द निवारक दवाएं (NSAID पेनकिलर) बिल्कुल न लें।"
            )
        else:
            response_text = (
                f"Creatinine is a muscle waste byproduct filtered by healthy kidneys. When kidneys experience stress from high blood sugar or elevated blood pressure, creatinine levels rise.\n\n"
                f"**Kidney Protection Strategy:** Stay well-hydrated, control blood pressure, and avoid over-the-counter NSAID painkillers."
            )
        citations = [f"Renal Function Review · {patient.get('name')}"]

    # 4. Questions about Medications
    elif any(k in query_lower for k in ["medicine", "prescription", "side effect", "interaction", "timing", "दवा", "दवाई"]):
        active_meds = HealthRepository.get_active_medications(patient_id)
        med_names = [m["name"] for m in active_meds[:4]] if active_meds else ["Prescribed Regimen"]
        response_text = (
            f"Active medications for **{patient.get('name')}**:\n"
            + "\n".join([f"• {m}" for m in med_names]) + "\n\n"
            f"Always take morning doses with or after breakfast, and evening doses post-dinner. Never discontinue cardioprotective or antidiabetic drugs without consulting your physician."
        )
        citations = [f"Medication Schedule · {patient.get('name')}"]

    # 5. Default General Healthcare Query
    else:
        if lang == "hi":
            response_text = (
                f"नमस्ते! मैं **{patient.get('name')}** का निरोग्य AI हेल्थ को-पायलट हूँ। "
                f"मैं आपकी लैब रिपोर्ट्स, पर्चियों, ब्लड शुगर, बीपी, और दवाओं के बारे में आसान भाषा में जानकारी दे सकता हूँ। "
                f"आप मुझसे अपनी जांच रिपोर्ट, दवाओं के समय या खान-पान के बारे में पूछ सकते हैं।"
            )
        else:
            response_text = (
                f"Hello! I am the Nirogya AI Health Copilot for **{patient.get('name')}**.\n\n"
                f"Known profile: {patient.get('age')} Y, {patient.get('gender')}, Blood Group {patient.get('blood_group')}, "
                f"Conditions: {patient.get('condition_summary', 'General Wellness')}.\n\n"
                f"Ask me anything about test values (HbA1c, BP, Lipids, Creatinine), medication timing, or doctor consultation questions!"
            )
        citations = [f"Nirogya AI Clinical Knowledge Base"]

    return {
        "reply": response_text,
        "engine": "Nirogya Built-in Clinical Intelligence",
        "citations": citations
    }


# ─── ABDM CONSENT SIMULATOR ───────────────────────────────────────────────────

@app.post("/api/abdm/consent-flow")
def simulate_abdm_consent(req: Dict[str, Any] = None):
    """Simulates 3-step ABDM Consent Handshake between HIP (Hospital), Patient, and HIU (Nirogya AI)"""
    import uuid
    req = req or {}
    hip = req.get("hip", "Apollo Hospitals / Metropolis Healthcare")
    purpose = req.get("purpose", "Care Management & Chronic Disease Monitoring")

    consent_id = f"CONSENT-{uuid.uuid4().hex[:8].upper()}"
    expiry = (datetime.date.today() + datetime.timedelta(days=30)).isoformat()

    return {
        "consent_id": consent_id,
        "status": "GRANTED_VERIFIED",
        "hip": hip,
        "hiu": "Nirogya AI Health Copilot",
        "patient_abha": req.get("patient_abha", "14-8921-4350-9812"),
        "purpose": purpose,
        "permission_mode": "VIEW",
        "date_range": "2026-05-01 to 2026-10-15",
        "expiry": expiry,
        "security": "ECDH-256 Encrypted FHIR Channel Active",
        "unlocked_records_count": 5
    }


# ─── STATIC FRONTEND MOUNT ───────────────────────────────────────────────────

frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
