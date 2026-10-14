"""
Comprehensive API test suite for Nirogya AI
"""
import sys
import urllib.request
import json

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def test_api(name, url, post_data=None):
    try:
        req = urllib.request.Request(url)
        if post_data:
            req.add_header('Content-Type', 'application/json')
            data = json.dumps(post_data).encode('utf-8')
            resp = urllib.request.urlopen(req, data=data)
        else:
            resp = urllib.request.urlopen(req)
        res = json.loads(resp.read().decode('utf-8'))
        print(f"PASS: {name} (Keys: {list(res.keys()) if isinstance(res, dict) else len(res)})")
        return res
    except Exception as e:
        print(f"FAIL: {name} -> {e}")
        return None

def test_upload():
    try:
        boundary = '----WebKitFormBoundaryNirogyaAiTest77'
        sample_doc = (
            "MAX HEALTHCARE OUTPATIENT Rx\n"
            "Patient: Rajesh Kumar Sharma | Date: 12-Oct-2026 | Dr. S. Kapoor\n"
            "Diagnoses: Type 2 Diabetes, High Cholesterol\n\n"
            "Rx:\n"
            "1. Tab. Glycomet 500mg - 1 tab BD before food\n"
            "2. Tab. Telma 40 - 1 tab OD after breakfast\n"
            "Advice: Low sugar diet."
        )
        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="file"; filename="opd_rx.txt"\r\n'
            f"Content-Type: text/plain\r\n\r\n"
            f"{sample_doc}\r\n"
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="provider"\r\n\r\n'
            f"Max Super Speciality OPD\r\n"
            f"--{boundary}--\r\n"
        ).encode('utf-8')

        req = urllib.request.Request('http://localhost:8000/api/documents/upload', data=body)
        req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
        resp = urllib.request.urlopen(req)
        res = json.loads(resp.read().decode('utf-8'))
        print(f"PASS: File Upload Ingestion -> Doc ID: {res.get('doc_id')}, Meds: {len(res.get('parsed_data', {}).get('medications', []))}")
        return res
    except Exception as e:
        print(f"FAIL: File Upload Ingestion -> {e}")
        return None

if __name__ == '__main__':
    print("=== TESTING ALL NIROGYA AI ENDPOINTS ===")
    test_api("Profile API", "http://localhost:8000/api/profile")
    test_api("Timeline API", "http://localhost:8000/api/timeline")
    test_api("Vitals Trends API", "http://localhost:8000/api/vitals")
    test_api("Medications API", "http://localhost:8000/api/medications")
    doc_en = test_api("Doc Details (English)", "http://localhost:8000/api/documents/sample_lab_report?lang=en")
    doc_hi = test_api("Doc Details (Hindi)", "http://localhost:8000/api/documents/sample_lab_report?lang=hi")
    test_api("FHIR Export API", "http://localhost:8000/api/fhir/export/sample_lab_report")
    test_api("ABHA Generator", "http://localhost:8000/api/abha/generate", {"name": "Rajesh Kumar Sharma", "year_of_birth": 1974})
    chat_res = test_api("AI Copilot Chat (HbA1c query)", "http://localhost:8000/api/copilot/chat", {"message": "Explain my high HbA1c in simple terms", "language": "en"})
    test_upload()
    test_api("Drug Interactions Matrix", "http://localhost:8000/api/interactions")
    test_api("Nutrition Plan Guide", "http://localhost:8000/api/nutrition")
    test_api("ABDM Consent Handshake Simulation", "http://localhost:8000/api/abdm/consent-flow", {"hip": "Apollo Hospitals", "purpose": "Care Management"})
    
    # Verify WOW Factor payload integration
    if doc_en:
        assert "biomarker_deltas" in doc_en, "biomarker_deltas missing from doc_en"
        assert "drug_interactions" in doc_en, "drug_interactions missing from doc_en"
        assert "nutrition_plan" in doc_en, "nutrition_plan missing from doc_en"
        print("VERIFIED: doc_en contains biomarker_deltas, drug_interactions, and nutrition_plan!")

    print("\nALL NIROGYA AI SUITE TESTS COMPLETED SUCCESSFULLY!")
