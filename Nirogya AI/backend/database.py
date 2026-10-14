"""
Nirogya AI - Persistent SQLite Storage & Multi-Patient Repository
Manages:
- Multiple Patients & dynamic ABHA credentials
- Clinical documents & OCR metadata per patient
- Longitudinal Timeline events per patient
- Lab Observations & dynamic Vitals time-series calculations
- Active Medications & Dosage regimens per patient
"""

import sqlite3
import json
import os
import uuid
import datetime
from typing import Dict, Any, List, Optional
from backend.sample_data import SAMPLE_RECORDS, DEFAULT_TIMELINE_EVENTS, VITALS_HISTORY
from backend.abdm_fhir import AbdmFhirEngine

DB_FILE = os.path.join(os.path.dirname(__file__), "nirogya.db")


def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Patients Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        age INTEGER,
        gender TEXT,
        blood_group TEXT,
        abha_number TEXT,
        abha_address TEXT,
        abha_status TEXT,
        phone TEXT,
        emergency_contact TEXT,
        condition_summary TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 2. Uploaded / Ingested Documents
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id TEXT PRIMARY KEY,
        patient_id TEXT DEFAULT 'pat-101',
        title TEXT NOT NULL,
        doc_type TEXT NOT NULL,
        provider TEXT,
        doctor_name TEXT,
        doc_date TEXT,
        raw_text TEXT,
        parsed_data TEXT,
        fhir_bundle TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 3. Timeline Events
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS timeline_events (
        id TEXT PRIMARY KEY,
        patient_id TEXT DEFAULT 'pat-101',
        event_date TEXT NOT NULL,
        event_type TEXT NOT NULL,
        title TEXT NOT NULL,
        summary TEXT NOT NULL,
        badge TEXT,
        badge_color TEXT,
        document_id TEXT
    )
    """)

    # 4. Lab Observations
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS lab_observations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id TEXT DEFAULT 'pat-101',
        doc_id TEXT,
        test_name TEXT NOT NULL,
        category TEXT,
        value REAL,
        unit TEXT,
        ref_min REAL,
        ref_max REAL,
        status TEXT,
        is_abnormal INTEGER,
        test_date TEXT
    )
    """)

    # 5. Medications
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS medications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id TEXT DEFAULT 'pat-101',
        doc_id TEXT,
        name TEXT NOT NULL,
        generic TEXT,
        dosage TEXT,
        frequency TEXT,
        timing TEXT,
        duration TEXT,
        purpose TEXT,
        instructions_en TEXT,
        instructions_hi TEXT,
        is_active INTEGER DEFAULT 1
    )
    """)

    # Schema migration: check for missing patient_id columns in existing DB
    tables_to_check = ["documents", "timeline_events", "lab_observations", "medications"]
    for t in tables_to_check:
        cursor.execute(f"PRAGMA table_info({t})")
        columns = [col[1] for col in cursor.fetchall()]
        if "patient_id" not in columns:
            cursor.execute(f"ALTER TABLE {t} ADD COLUMN patient_id TEXT DEFAULT 'pat-101'")

    cursor.execute("PRAGMA table_info(patients)")
    pat_columns = [col[1] for col in cursor.fetchall()]
    if "condition_summary" not in pat_columns:
        cursor.execute("ALTER TABLE patients ADD COLUMN condition_summary TEXT")

    conn.commit()

    # Seed initial realistic multi-patient data if empty or missing
    cursor.execute("SELECT COUNT(*) FROM patients")
    pat_count = cursor.fetchone()[0]
    if pat_count == 0:
        seed_all_patients(conn)
    elif pat_count == 1:
        # Add additional demo patients to demonstrate multi-patient capability
        seed_additional_patients(conn)

    conn.close()


def generate_random_abha(name: str) -> tuple[str, str]:
    import random
    digits = f"14-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
    clean_name = "".join(c for c in name.lower() if c.isalnum() or c == " ").split()
    addr_prefix = ".".join(clean_name[:2]) if clean_name else "user"
    address = f"{addr_prefix}{random.randint(10, 99)}@abdm"
    return digits, address


def seed_all_patients(conn):
    cursor = conn.cursor()

    # Patient 1: Rajesh Kumar Sharma (Type-2 Diabetes & Hypertension)
    cursor.execute("""
    INSERT INTO patients (id, name, age, gender, blood_group, abha_number, abha_address, abha_status, phone, emergency_contact, condition_summary)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "pat-101",
        "Rajesh Kumar Sharma",
        52,
        "Male",
        "B+ Positive",
        "14-8921-4350-9812",
        "rajesh.sharma@abdm",
        "ACTIVE_LINKED",
        "+91 98112 34567",
        "Pooja Sharma (Wife) - +91 98112 34568",
        "Type 2 Diabetes Mellitus, Hypertension & Mixed Dyslipidemia"
    ))

    # Documents Seed for Rajesh
    abha_info_rajesh = {
        "abha_number": "14-8921-4350-9812",
        "abha_address": "rajesh.sharma@abdm"
    }

    for key, doc in SAMPLE_RECORDS.items():
        doc_id = key
        fhir = AbdmFhirEngine.convert_to_fhir_bundle(doc_id, doc, abha_info_rajesh)

        cursor.execute("""
        INSERT INTO documents (id, patient_id, title, doc_type, provider, doctor_name, doc_date, raw_text, parsed_data, fhir_bundle)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            doc_id,
            "pat-101",
            doc["title"],
            doc["doc_type"],
            doc["provider"],
            doc["doctor_name"],
            doc["date"],
            doc["raw_text"],
            json.dumps(doc["parsed_data"]),
            json.dumps(fhir)
        ))

        # Seed lab tests
        for test in doc["parsed_data"].get("lab_tests", []):
            cursor.execute("""
            INSERT INTO lab_observations (patient_id, doc_id, test_name, category, value, unit, ref_min, ref_max, status, is_abnormal, test_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                "pat-101",
                doc_id,
                test["name"],
                test.get("category", "General"),
                test.get("value", 0.0),
                test.get("unit", ""),
                test.get("ref_min", 0.0),
                test.get("ref_max", 100.0),
                test.get("status", "NORMAL"),
                1 if test.get("is_abnormal") else 0,
                doc["date"]
            ))

        # Seed medications
        for med in doc["parsed_data"].get("medications", []):
            cursor.execute("""
            INSERT INTO medications (patient_id, doc_id, name, generic, dosage, frequency, timing, duration, purpose, instructions_en, instructions_hi, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            """, (
                "pat-101",
                doc_id,
                med["name"],
                med.get("generic", ""),
                med.get("dosage", "1 Tablet"),
                med.get("frequency", "1 - 0 - 1"),
                med.get("timing", "After food"),
                med.get("duration", "30 Days"),
                med.get("purpose", ""),
                med.get("instructions_en", ""),
                med.get("instructions_hi", "")
            ))

    # Timeline Seed for Rajesh
    for evt in DEFAULT_TIMELINE_EVENTS:
        cursor.execute("""
        INSERT INTO timeline_events (id, patient_id, event_date, event_type, title, summary, badge, badge_color, document_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            evt["id"],
            "pat-101",
            evt["date"],
            evt["type"],
            evt["title"],
            evt["summary"],
            evt["badge"],
            evt["badge_color"],
            evt["document_key"]
        ))

    conn.commit()
    seed_additional_patients(conn)


def seed_additional_patients(conn):
    cursor = conn.cursor()

    # Patient 2: Priya Patel (Hypothyroidism & Vitamin D3 Deficiency)
    cursor.execute("SELECT COUNT(*) FROM patients WHERE id = 'pat-102'")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
        INSERT INTO patients (id, name, age, gender, blood_group, abha_number, abha_address, abha_status, phone, emergency_contact, condition_summary)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "pat-102",
            "Priya Patel",
            34,
            "Female",
            "O+ Positive",
            "14-7712-9014-3321",
            "priya.patel@abdm",
            "ACTIVE_LINKED",
            "+91 97234 11223",
            "Nikhil Patel (Husband) - +91 97234 11224",
            "Subclinical Hypothyroidism, Vitamin D3 Deficiency & Fatigue"
        ))

        # Add Priya's document
        priya_doc_id = "doc-priya-thyroid-2026"
        priya_parsed = {
            "diagnoses": ["Hypothyroidism (Primary)", "Severe Vitamin D3 Deficiency"],
            "lab_tests": [
                {"name": "Thyroid Stimulating Hormone (TSH)", "category": "Thyroid", "value": 7.84, "unit": "uIU/mL", "ref_min": 0.35, "ref_max": 4.94, "status": "HIGH", "is_abnormal": True},
                {"name": "Total Thyroxine (T4)", "category": "Thyroid", "value": 6.4, "unit": "ug/dL", "ref_min": 5.1, "ref_max": 14.1, "status": "NORMAL", "is_abnormal": False},
                {"name": "Vitamin D3 (25-OH)", "category": "Vitamins", "value": 14.2, "unit": "ng/mL", "ref_min": 30.0, "ref_max": 100.0, "status": "DEFICIENT", "is_abnormal": True},
                {"name": "Vitamin B12", "category": "Vitamins", "value": 168.0, "unit": "pg/mL", "ref_min": 211.0, "ref_max": 911.0, "status": "DEFICIENT", "is_abnormal": True},
                {"name": "Hemoglobin (Hb)", "category": "CBC", "value": 11.8, "unit": "g/dL", "ref_min": 12.0, "ref_max": 15.0, "status": "LOW", "is_abnormal": True}
            ],
            "medications": [
                {"name": "Thyronorm 50 mcg (Levothyroxine)", "generic": "Levothyroxine Sodium", "dosage": "1 Tablet", "frequency": "1 - 0 - 0 (Morning)", "timing": "Early morning empty stomach with water, 45 min before breakfast", "purpose": "Thyroid hormone replacement"},
                {"name": "Calcirol Sachet (Cholecalciferol 60k IU)", "generic": "Vitamin D3", "dosage": "1 Sachet", "frequency": "Once weekly with warm milk", "timing": "Sunday mornings", "purpose": "Rapid Vitamin D repletion"}
            ]
        }

        priya_fhir = AbdmFhirEngine.convert_to_fhir_bundle(priya_doc_id, {
            "title": "Thyroid & Micronutrient Comprehensive Panel",
            "doc_type": "lab_report",
            "patient_name": "Priya Patel",
            "doctor_name": "Dr. Neha Kulkarni, MD",
            "date": "2026-08-20",
            "provider": "Sterling Accuris Diagnostics, Ahmedabad",
            "parsed_data": priya_parsed
        }, {"abha_number": "14-7712-9014-3321", "abha_address": "priya.patel@abdm"})

        cursor.execute("""
        INSERT INTO documents (id, patient_id, title, doc_type, provider, doctor_name, doc_date, raw_text, parsed_data, fhir_bundle)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            priya_doc_id,
            "pat-102",
            "Thyroid & Micronutrient Comprehensive Panel",
            "lab_report",
            "Sterling Accuris Diagnostics, Ahmedabad",
            "Dr. Neha Kulkarni, MD",
            "2026-08-20",
            "STERLING ACCURIS DIAGNOSTICS - Patient: Priya Patel, 34 Y, Female. TSH 7.84 uIU/mL (HIGH), Vit D3 14.2 ng/mL (DEFICIENT).",
            json.dumps(priya_parsed),
            json.dumps(priya_fhir)
        ))

        # Priya's Timeline
        cursor.execute("""
        INSERT INTO timeline_events (id, patient_id, event_date, event_type, title, summary, badge, badge_color, document_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "evt-p1",
            "pat-102",
            "2026-08-20",
            "lab_report",
            "Endocrine & Vitamin Panel (Sterling)",
            "Diagnosed with Subclinical Hypothyroidism (TSH 7.84) and Vitamin D deficiency (14.2 ng/mL).",
            "Thyroid Panel",
            "warning",
            priya_doc_id
        ))
        cursor.execute("""
        INSERT INTO timeline_events (id, patient_id, event_date, event_type, title, summary, badge, badge_color, document_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "evt-p2",
            "pat-102",
            "2026-08-22",
            "prescription",
            "Endocrinology Consultation - Dr. Neha Kulkarni",
            "Initiated Thyronorm 50mcg daily and weekly Calcirol 60,000 IU sachets for 8 weeks.",
            "Prescription",
            "primary",
            priya_doc_id
        ))

        # Priya's Meds
        for med in priya_parsed["medications"]:
            cursor.execute("""
            INSERT INTO medications (patient_id, doc_id, name, generic, dosage, frequency, timing, duration, purpose, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            """, (
                "pat-102",
                priya_doc_id,
                med["name"],
                med["generic"],
                med["dosage"],
                med["frequency"],
                med["timing"],
                "60 Days",
                med["purpose"]
            ))

    # Patient 3: Amit Verma (Post-CABG Cardiac & Hypertensive Care)
    cursor.execute("SELECT COUNT(*) FROM patients WHERE id = 'pat-103'")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
        INSERT INTO patients (id, name, age, gender, blood_group, abha_number, abha_address, abha_status, phone, emergency_contact, condition_summary)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "pat-103",
            "Amit Verma",
            68,
            "Male",
            "A+ Positive",
            "14-4421-8890-1123",
            "amit.verma@abdm",
            "ACTIVE_LINKED",
            "+91 98101 99887",
            "Vikas Verma (Son) - +91 98101 99888",
            "Post-CABG Cardiac Care, Stage 2 Hypertension & Hypercholesterolemia"
        ))

        amit_doc_id = "doc-amit-cardio-2026"
        amit_parsed = {
            "diagnoses": ["Coronary Artery Disease (Post-CABG)", "Stage 2 Essential Hypertension"],
            "lab_tests": [
                {"name": "Total Cholesterol", "category": "Lipid Profile", "value": 182.0, "unit": "mg/dL", "ref_min": 125.0, "ref_max": 200.0, "status": "NORMAL", "is_abnormal": False},
                {"name": "LDL Cholesterol (Bad)", "category": "Lipid Profile", "value": 68.0, "unit": "mg/dL", "ref_min": 50.0, "ref_max": 70.0, "status": "OPTIMAL", "is_abnormal": False},
                {"name": "Triglycerides", "category": "Lipid Profile", "value": 142.0, "unit": "mg/dL", "ref_min": 50.0, "ref_max": 150.0, "status": "NORMAL", "is_abnormal": False},
                {"name": "Serum Creatinine", "category": "Renal Function", "value": 1.1, "unit": "mg/dL", "ref_min": 0.7, "ref_max": 1.2, "status": "NORMAL", "is_abnormal": False}
            ],
            "medications": [
                {"name": "Ecosprin-AV 75/20 (Aspirin + Atorvastatin)", "generic": "Aspirin 75mg + Atorvastatin 20mg", "dosage": "1 Capsule", "frequency": "0 - 0 - 1 (Night)", "timing": "Post dinner at bedtime", "purpose": "Dual antiplatelet and arterial plaque stabilization"},
                {"name": "Metoprolol Succinate ER 25mg (Betaloc)", "generic": "Metoprolol", "dosage": "1 Tablet", "frequency": "1 - 0 - 0 (Morning)", "timing": "Morning after breakfast", "purpose": "Rate control & cardioprotection"},
                {"name": "Ramipril 5mg (Cardace)", "generic": "Ramipril ACE Inhibitor", "dosage": "1 Tablet", "frequency": "1 - 0 - 0 (Morning)", "timing": "Morning with water", "purpose": "Afterload reduction & BP stabilization"}
            ]
        }

        amit_fhir = AbdmFhirEngine.convert_to_fhir_bundle(amit_doc_id, {
            "title": "Quarterly Cardiology Follow-up & ECG Review",
            "doc_type": "prescription",
            "patient_name": "Amit Verma",
            "doctor_name": "Dr. R. K. Singhal, DM (Cardiology)",
            "date": "2026-09-02",
            "provider": "Fortis Escorts Heart Institute, Okhla, New Delhi",
            "parsed_data": amit_parsed
        }, {"abha_number": "14-4421-8890-1123", "abha_address": "amit.verma@abdm"})

        cursor.execute("""
        INSERT INTO documents (id, patient_id, title, doc_type, provider, doctor_name, doc_date, raw_text, parsed_data, fhir_bundle)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            amit_doc_id,
            "pat-103",
            "Quarterly Cardiology Follow-up & ECG Review",
            "prescription",
            "Fortis Escorts Heart Institute, New Delhi",
            "Dr. R. K. Singhal, DM (Cardiology)",
            "2026-09-02",
            "FORTIS ESCORTS HEART INSTITUTE - Patient: Amit Verma, 68 Y, Male. Stable post-CABG status. BP 134/82 mmHg, HR 68 bpm. LDL well controlled at 68 mg/dL.",
            json.dumps(amit_parsed),
            json.dumps(amit_fhir)
        ))

        cursor.execute("""
        INSERT INTO timeline_events (id, patient_id, event_date, event_type, title, summary, badge, badge_color, document_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "evt-a1",
            "pat-103",
            "2026-09-02",
            "prescription",
            "Cardiology Review - Fortis Escorts",
            "Good functional capacity. Target LDL < 70 achieved. Maintained on Ecosprin-AV, Metoprolol and Ramipril.",
            "Cardiology",
            "success",
            amit_doc_id
        ))

        for med in amit_parsed["medications"]:
            cursor.execute("""
            INSERT INTO medications (patient_id, doc_id, name, generic, dosage, frequency, timing, duration, purpose, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            """, (
                "pat-103",
                amit_doc_id,
                med["name"],
                med["generic"],
                med["dosage"],
                med["frequency"],
                med["timing"],
                "90 Days",
                med["purpose"]
            ))

    conn.commit()


class HealthRepository:
    """High-level repository for accessing and updating multi-patient health records"""

    @classmethod
    def get_all_patients(cls) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patients ORDER BY id ASC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @classmethod
    def get_patient_profile(cls, patient_id: Optional[str] = None) -> Dict[str, Any]:
        conn = get_db_connection()
        cursor = conn.cursor()
        if patient_id:
            cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
        else:
            cursor.execute("SELECT * FROM patients LIMIT 1")
        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)

        # Fallback default
        return {
            "id": "pat-101",
            "name": "Rajesh Kumar Sharma",
            "age": 52,
            "gender": "Male",
            "blood_group": "B+",
            "abha_number": "14-8921-4350-9812",
            "abha_address": "rajesh.sharma@abdm",
            "abha_status": "ACTIVE_LINKED",
            "condition_summary": "Type 2 Diabetes Mellitus & Hypertension"
        }

    @classmethod
    def create_patient(
        cls,
        name: str,
        age: int,
        gender: str,
        blood_group: str,
        phone: Optional[str] = "",
        condition_summary: Optional[str] = "",
        emergency_contact: Optional[str] = ""
    ) -> Dict[str, Any]:
        conn = get_db_connection()
        cursor = conn.cursor()

        pat_id = f"pat-{uuid.uuid4().hex[:6]}"
        abha_number, abha_address = generate_random_abha(name)

        cursor.execute("""
        INSERT INTO patients (id, name, age, gender, blood_group, abha_number, abha_address, abha_status, phone, emergency_contact, condition_summary)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            pat_id,
            name.strip(),
            int(age),
            gender.strip(),
            blood_group.strip(),
            abha_number,
            abha_address,
            "ACTIVE_LINKED",
            phone or "+91 98000 00000",
            emergency_contact or "Family Contact",
            condition_summary or "Health records under evaluation"
        ))

        # Add initial timeline milestone
        cursor.execute("""
        INSERT INTO timeline_events (id, patient_id, event_date, event_type, title, summary, badge, badge_color, document_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            f"evt-{uuid.uuid4().hex[:6]}",
            pat_id,
            datetime.date.today().isoformat(),
            "registration",
            f"Digital Health Record Initialized for {name}",
            f"ABDM profile created with ABHA Address {abha_address}. Patient onboarded to Nirogya AI.",
            "ABHA Linked",
            "primary",
            None
        ))

        conn.commit()
        cursor.execute("SELECT * FROM patients WHERE id = ?", (pat_id,))
        created = dict(cursor.fetchone())
        conn.close()
        return created

    @classmethod
    def delete_patient(cls, patient_id: str) -> bool:
        if patient_id == "pat-101":
            return False  # Protect primary default demo patient
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
        cursor.execute("DELETE FROM documents WHERE patient_id = ?", (patient_id,))
        cursor.execute("DELETE FROM timeline_events WHERE patient_id = ?", (patient_id,))
        cursor.execute("DELETE FROM lab_observations WHERE patient_id = ?", (patient_id,))
        cursor.execute("DELETE FROM medications WHERE patient_id = ?", (patient_id,))
        conn.commit()
        conn.close()
        return True

    @classmethod
    def get_timeline(cls, patient_id: Optional[str] = None) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        if patient_id:
            cursor.execute("SELECT * FROM timeline_events WHERE patient_id = ? ORDER BY event_date DESC", (patient_id,))
        else:
            cursor.execute("SELECT * FROM timeline_events ORDER BY event_date DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @classmethod
    def get_all_documents(cls, patient_id: Optional[str] = None) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        if patient_id:
            cursor.execute("SELECT id, patient_id, title, doc_type, provider, doctor_name, doc_date, created_at FROM documents WHERE patient_id = ? ORDER BY doc_date DESC", (patient_id,))
        else:
            cursor.execute("SELECT id, patient_id, title, doc_type, provider, doctor_name, doc_date, created_at FROM documents ORDER BY doc_date DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @classmethod
    def get_document_by_id(cls, doc_id: str, patient_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        if patient_id:
            cursor.execute("SELECT * FROM documents WHERE id = ? AND patient_id = ?", (doc_id, patient_id))
        else:
            cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            d = dict(row)
            d["parsed_data"] = json.loads(d["parsed_data"]) if d.get("parsed_data") else {}
            d["fhir_bundle"] = json.loads(d["fhir_bundle"]) if d.get("fhir_bundle") else {}
            return d
        return None

    @classmethod
    def get_active_medications(cls, patient_id: Optional[str] = None) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        if patient_id:
            cursor.execute("SELECT * FROM medications WHERE patient_id = ? AND is_active = 1 ORDER BY id DESC", (patient_id,))
        else:
            cursor.execute("SELECT * FROM medications WHERE is_active = 1 ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @classmethod
    def get_vitals_history(cls, patient_id: Optional[str] = None) -> Dict[str, Any]:
        """Dynamically computes time-series for blood sugar, BP, and cholesterol from SQLite observations"""
        conn = get_db_connection()
        cursor = conn.cursor()

        # Query real lab observations for this patient
        pid = patient_id or "pat-101"
        cursor.execute("""
        SELECT test_name, value, test_date
        FROM lab_observations
        WHERE patient_id = ? AND value > 0
        ORDER BY test_date ASC
        """, (pid,))
        rows = cursor.fetchall()
        conn.close()

        # If observations exist, aggregate them by date
        sugar_by_date = {}
        cholesterol_by_date = {}
        bp_by_date = {}

        for r in rows:
            name = (r["test_name"] or "").lower()
            val = float(r["value"] or 0)
            dt = r["test_date"] or "2026-09-14"

            # Glucose / Sugar
            if "fasting" in name or "fbs" in name:
                sugar_by_date.setdefault(dt, {})["fbs"] = val
            elif "post" in name or "ppbs" in name:
                sugar_by_date.setdefault(dt, {})["ppbs"] = val
            elif "hba1c" in name:
                sugar_by_date.setdefault(dt, {})["hba1c"] = val

            # Cholesterol
            if "total cholesterol" in name:
                cholesterol_by_date.setdefault(dt, {})["total"] = val
            elif "ldl" in name:
                cholesterol_by_date.setdefault(dt, {})["ldl"] = val
            elif "triglyceride" in name:
                cholesterol_by_date.setdefault(dt, {})["triglycerides"] = val

            # Blood pressure
            if "systolic" in name:
                bp_by_date.setdefault(dt, {})["systolic"] = val
            elif "diastolic" in name:
                bp_by_date.setdefault(dt, {})["diastolic"] = val

        # Format arrays
        sugar_series = [
            {"date": d, "fbs": v.get("fbs", 120), "ppbs": v.get("ppbs", 160), "hba1c": v.get("hba1c", 7.0)}
            for d, v in sugar_by_date.items()
        ]
        bp_series = [
            {"date": d, "systolic": v.get("systolic", 130), "diastolic": v.get("diastolic", 85)}
            for d, v in bp_by_date.items()
        ]
        cholesterol_series = [
            {"date": d, "total": v.get("total", 200), "ldl": v.get("ldl", 110), "triglycerides": v.get("triglycerides", 150)}
            for d, v in cholesterol_by_date.items()
        ]

        # If patient has insufficient points for chart, fall back to default baseline series for that condition
        if len(sugar_series) >= 2 or len(bp_series) >= 2 or len(cholesterol_series) >= 2:
            return {
                "blood_sugar": sugar_series if sugar_series else VITALS_HISTORY["blood_sugar"],
                "blood_pressure": bp_series if bp_series else VITALS_HISTORY["blood_pressure"],
                "cholesterol": cholesterol_series if cholesterol_series else VITALS_HISTORY["cholesterol"]
            }

        # Otherwise return baseline history
        return VITALS_HISTORY

    @classmethod
    def save_new_document(
        cls,
        patient_id: str,
        title: str,
        doc_type: str,
        provider: str,
        doctor_name: str,
        doc_date: str,
        raw_text: str,
        parsed_data: Dict[str, Any],
        fhir_bundle: Dict[str, Any]
    ) -> str:
        conn = get_db_connection()
        cursor = conn.cursor()
        doc_id = f"doc-{uuid.uuid4().hex[:8]}"

        cursor.execute("""
        INSERT INTO documents (id, patient_id, title, doc_type, provider, doctor_name, doc_date, raw_text, parsed_data, fhir_bundle)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            doc_id,
            patient_id,
            title,
            doc_type,
            provider,
            doctor_name,
            doc_date,
            raw_text,
            json.dumps(parsed_data),
            json.dumps(fhir_bundle)
        ))

        # Add timeline event for this patient
        badge = "New Lab Report" if doc_type == "lab_report" else ("Prescription" if doc_type == "prescription" else "Discharge Summary")
        badge_color = "danger" if any(t.get("is_abnormal") for t in parsed_data.get("lab_tests", [])) else "primary"
        evt_id = f"evt-{uuid.uuid4().hex[:6]}"

        cursor.execute("""
        INSERT INTO timeline_events (id, patient_id, event_date, event_type, title, summary, badge, badge_color, document_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            evt_id,
            patient_id,
            doc_date,
            doc_type,
            title,
            f"Processed via Nirogya AI. Extracted {len(parsed_data.get('lab_tests', []))} lab observations & {len(parsed_data.get('medications', []))} medications from {provider}.",
            badge,
            badge_color,
            doc_id
        ))

        # Insert lab tests
        for test in parsed_data.get("lab_tests", []):
            cursor.execute("""
            INSERT INTO lab_observations (patient_id, doc_id, test_name, category, value, unit, ref_min, ref_max, status, is_abnormal, test_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                patient_id,
                doc_id,
                test["name"],
                test.get("category", "General"),
                test.get("value", 0.0),
                test.get("unit", ""),
                test.get("ref_min", 0.0),
                test.get("ref_max", 100.0),
                test.get("status", "NORMAL"),
                1 if test.get("is_abnormal") else 0,
                doc_date
            ))

        # Insert medications
        for med in parsed_data.get("medications", []):
            cursor.execute("""
            INSERT INTO medications (patient_id, doc_id, name, generic, dosage, frequency, timing, duration, purpose, instructions_en, instructions_hi, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            """, (
                patient_id,
                doc_id,
                med["name"],
                med.get("generic", ""),
                med.get("dosage", "1 Tablet"),
                med.get("frequency", "1 - 0 - 1"),
                med.get("timing", "After food"),
                med.get("duration", "30 Days"),
                med.get("purpose", ""),
                med.get("instructions_en", ""),
                med.get("instructions_hi", "")
            ))

        conn.commit()
        conn.close()
        return doc_id
