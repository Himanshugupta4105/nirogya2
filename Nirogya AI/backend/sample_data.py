"""
Nirogya AI - Sample Clinical Records & Presets
High-fidelity realistic medical records for hackathon demo & instant evaluation:
1. Comprehensive Diabetic & Lipid Lab Report
2. Apollo Hospital Outpatient Prescription (Bilingual & Handwritten elements)
3. AIIMS / Max Healthcare Inpatient Discharge Summary
4. Thyroid & Micronutrient Diagnostic Panel
"""

SAMPLE_RECORDS = {
    "sample_lab_report": {
        "title": "Comprehensive Metabolic & Lipid Panel",
        "doc_type": "lab_report",
        "patient_name": "Rajesh Kumar Sharma",
        "patient_age": 52,
        "patient_gender": "Male",
        "date": "2026-09-14",
        "provider": "Metropolis Healthcare Diagnostics, New Delhi",
        "doctor_name": "Dr. Sunita Deshmukh, MD (Pathology)",
        "raw_text": """METROPOLIS HEALTHCARE DIAGNOSTICS & RESEARCH CENTER
Patient Name: Rajesh Kumar Sharma | Age: 52 Y | Gender: Male
Ref By: Dr. A. K. Verma, MD (Internal Medicine) | Date: 14-Sep-2026
ABHA ID: 14-8921-4350-9812 | Sample ID: LAB-2026-98144

BIOCHEMISTRY & DIABETOLOGY REPORT
Test Name                    Result       Unit       Reference Range    Status
---------------------------------------------------------------------------------
Fasting Blood Glucose (FBS)  186.0        mg/dL      70.0 - 100.0       HIGH
Post-Prandial Glucose (PPBS) 264.0        mg/dL      < 140.0            HIGH
HbA1c (Glycated Hemoglobin)  8.8          %          4.0 - 5.6          HIGH
Estimated Average Glucose    206          mg/dL      --                 HIGH

LIPID PROFILE
Total Cholesterol            242.0        mg/dL      < 200.0            HIGH
Triglycerides                218.0        mg/dL      < 150.0            HIGH
HDL Cholesterol (Good)       38.0         mg/dL      > 40.0             LOW
LDL Cholesterol (Bad)        160.4        mg/dL      < 100.0            HIGH
VLDL Cholesterol             43.6         mg/dL      < 30.0             HIGH
Total / HDL Ratio            6.37         Ratio      < 4.5              HIGH

RENAL FUNCTION TEST (RFT)
Serum Creatinine             1.35         mg/dL      0.7 - 1.2          HIGH
Blood Urea Nitrogen (BUN)    22.4         mg/dL      7.0 - 20.0         HIGH
eGFR (CKD-EPI)               58           mL/min     > 60               LOW
Serum Uric Acid              7.8          mg/dL      3.5 - 7.2          HIGH

COMPLETE BLOOD COUNT (CBC)
Hemoglobin (Hb)              13.8         g/dL       13.0 - 17.0        NORMAL
Total Leukocyte Count (TLC)  7,400        /cumm      4,000 - 11,000     NORMAL
Platelet Count               245,000      /cumm      150,000 - 450,000  NORMAL
ESR (1st Hour)               14           mm/hr      0 - 15             NORMAL

CLINICAL IMPRESSION:
1. Poorly controlled Type 2 Diabetes Mellitus with elevated Glycated Hemoglobin.
2. Atherogenic Mixed Dyslipidemia with high LDL and low HDL.
3. Mild Impairment in Renal Clearance (eGFR 58 mL/min - CKD Stage 2/3a transition).
4. Hyperuricemia.
Recommend immediate clinical correlation and nephro-protective glycemic optimization.
Dr. Sunita Deshmukh, MD (Path) - Reg No: MCI-2004-9812""",
        "parsed_data": {
            "diagnoses": ["Uncontrolled Type 2 Diabetes Mellitus", "Mixed Dyslipidemia", "Mild Renal Impairment (Early Diabetic Nephropathy)", "Hyperuricemia"],
            "lab_tests": [
                {"name": "Fasting Blood Glucose (FBS)", "category": "Diabetology", "value": 186.0, "unit": "mg/dL", "ref_min": 70.0, "ref_max": 100.0, "status": "HIGH", "is_abnormal": True},
                {"name": "Post-Prandial Glucose (PPBS)", "category": "Diabetology", "value": 264.0, "unit": "mg/dL", "ref_min": 0.0, "ref_max": 140.0, "status": "HIGH", "is_abnormal": True},
                {"name": "HbA1c (Glycated Hemoglobin)", "category": "Diabetology", "value": 8.8, "unit": "%", "ref_min": 4.0, "ref_max": 5.6, "status": "HIGH", "is_abnormal": True},
                {"name": "Total Cholesterol", "category": "Lipid Profile", "value": 242.0, "unit": "mg/dL", "ref_min": 0.0, "ref_max": 200.0, "status": "HIGH", "is_abnormal": True},
                {"name": "Triglycerides", "category": "Lipid Profile", "value": 218.0, "unit": "mg/dL", "ref_min": 0.0, "ref_max": 150.0, "status": "HIGH", "is_abnormal": True},
                {"name": "HDL Cholesterol (Good)", "category": "Lipid Profile", "value": 38.0, "unit": "mg/dL", "ref_min": 40.0, "ref_max": 60.0, "status": "LOW", "is_abnormal": True},
                {"name": "LDL Cholesterol (Bad)", "category": "Lipid Profile", "value": 160.4, "unit": "mg/dL", "ref_min": 0.0, "ref_max": 100.0, "status": "HIGH", "is_abnormal": True},
                {"name": "Serum Creatinine", "category": "Renal Function", "value": 1.35, "unit": "mg/dL", "ref_min": 0.7, "ref_max": 1.2, "status": "HIGH", "is_abnormal": True},
                {"name": "eGFR (CKD-EPI)", "category": "Renal Function", "value": 58.0, "unit": "mL/min", "ref_min": 60.0, "ref_max": 120.0, "status": "LOW", "is_abnormal": True},
                {"name": "Serum Uric Acid", "category": "Renal Function", "value": 7.8, "unit": "mg/dL", "ref_min": 3.5, "ref_max": 7.2, "status": "HIGH", "is_abnormal": True},
                {"name": "Hemoglobin (Hb)", "category": "Hematology", "value": 13.8, "unit": "g/dL", "ref_min": 13.0, "ref_max": 17.0, "status": "NORMAL", "is_abnormal": False},
                {"name": "Platelet Count", "category": "Hematology", "value": 245000, "unit": "/cumm", "ref_min": 150000, "ref_max": 450000, "status": "NORMAL", "is_abnormal": False}
            ],
            "medications": []
        }
    },

    "sample_prescription": {
        "title": "Cardio-Metabolic Outpatient Prescription",
        "doc_type": "prescription",
        "patient_name": "Rajesh Kumar Sharma",
        "patient_age": 52,
        "patient_gender": "Male",
        "date": "2026-09-16",
        "provider": "Apollo Hospitals, Sarita Vihar, New Delhi",
        "doctor_name": "Dr. Arvind K. Verma, MD, DM (Cardiology)",
        "raw_text": """APOLLO HOSPITALS - OUTPATIENT DEPARTMENT
Department of Cardiology & Endocrinology
Patient: Rajesh Kumar Sharma | Age: 52/M | Date: 16-Sep-2026
ABHA: 14-8921-4350-9812 | UHID: APO-DEL-2026-4412
Clinical Notes: Review of Lab Reports (14/09/2026). FBS 186, HbA1c 8.8%, BP 148/92 mmHg.
Diagnoses: T2DM with Dyslipidemia, Essential Hypertension Stage 1.

PRESCRIPTION / Rx:
1. Tab. Glycomet-GP 2 (Metformin 500mg + Glimepiride 2mg)
   Dosage: 1 Tablet
   Frequency: 1 - 0 - 1 (Morning & Night, 15 mins before meals)
   Duration: 60 Days
   Instructions: भोजन से पहले सुबह और शाम लें। Monitor for hypoglycemia (dizziness/sweating).

2. Tab. Telma 40 (Telmisartan 40mg)
   Dosage: 1 Tablet
   Frequency: 1 - 0 - 0 (Morning after breakfast)
   Duration: 60 Days
   Instructions: सुबह नाश्ते के बाद लें। Do not skip. Regular BP check weekly.

3. Tab. Rosuvas 10 (Rosuvastatin 10mg)
   Dosage: 1 Tablet
   Frequency: 0 - 0 - 1 (At bedtime)
   Duration: 60 Days
   Instructions: रात को सोने से पहले लें। For LDL cholesterol control.

4. Tab. Pan 40 (Pantoprazole 40mg)
   Dosage: 1 Tablet
   Frequency: 1 - 0 - 0 (Empty stomach, early morning)
   Duration: 15 Days
   Instructions: खाली पेट सुबह लें। As needed for acid reflux.

ADVICE & LIFESTYLE MODIFICATION:
- Diabetic diet: Strictly eliminate refined sugar, sweets, white bread, fried foods.
- Low sodium intake (< 3g salt/day) for blood pressure control.
- 30 minutes brisk walking daily.
- Repeat FBS, PPBS, Creatinine after 45 days. Follow up with Dr. Verma.
Signed: Dr. A.K. Verma (Reg: DMC-41928)""",
        "parsed_data": {
            "diagnoses": ["Type 2 Diabetes Mellitus", "Essential Hypertension Stage 1", "Atherogenic Dyslipidemia"],
            "lab_tests": [
                {"name": "Blood Pressure (Systolic)", "category": "Vitals", "value": 148, "unit": "mmHg", "ref_min": 90, "ref_max": 120, "status": "HIGH", "is_abnormal": True},
                {"name": "Blood Pressure (Diastolic)", "category": "Vitals", "value": 92, "unit": "mmHg", "ref_min": 60, "ref_max": 80, "status": "HIGH", "is_abnormal": True}
            ],
            "medications": [
                {
                    "name": "Glycomet-GP 2 (Metformin 500mg + Glimepiride 2mg)",
                    "generic": "Metformin hydrochloride + Glimepiride",
                    "dosage": "1 Tablet",
                    "frequency": "1 - 0 - 1 (Twice daily, Morning & Night)",
                    "timing": "15 mins before meals",
                    "duration": "60 Days",
                    "purpose": "Blood sugar regulation (dual action insulin sensitizer & secretagogue)",
                    "instructions_hi": "भोजन से 15 मिनट पहले सुबह और शाम 1 गोली लें। चक्कर या पसीना आए तो मीठा लें।",
                    "instructions_en": "Take 1 tablet twice daily, 15 minutes before breakfast and dinner.",
                    "warnings": "Watch for hypoglycemia (shakiness, cold sweat, hunger). Keep glucose candy handy."
                },
                {
                    "name": "Telma 40 (Telmisartan 40mg)",
                    "generic": "Telmisartan",
                    "dosage": "1 Tablet",
                    "frequency": "1 - 0 - 0 (Once daily, Morning)",
                    "timing": "After breakfast",
                    "duration": "60 Days",
                    "purpose": "Blood pressure control & kidney protection (ARB)",
                    "instructions_hi": "सुबह नाश्ते के बाद 1 गोली लें। दवाई छोड़ें नहीं।",
                    "instructions_en": "Take 1 tablet every morning after breakfast. Do not miss doses.",
                    "warnings": "Do not stop abruptly. Report persistent dry cough or dizziness."
                },
                {
                    "name": "Rosuvas 10 (Rosuvastatin 10mg)",
                    "generic": "Rosuvastatin calcium",
                    "dosage": "1 Tablet",
                    "frequency": "0 - 0 - 1 (Once daily, Night)",
                    "timing": "At bedtime",
                    "duration": "60 Days",
                    "purpose": "Cholesterol (LDL & Triglyceride) reduction and plaque stabilization",
                    "instructions_hi": "रात को सोने से पहले 1 गोली लें।",
                    "instructions_en": "Take 1 tablet at night before sleeping.",
                    "warnings": "Report unexplained muscle pain, tenderness, or weakness."
                },
                {
                    "name": "Pan 40 (Pantoprazole 40mg)",
                    "generic": "Pantoprazole sodium",
                    "dosage": "1 Tablet",
                    "frequency": "1 - 0 - 0 (Once daily, Morning)",
                    "timing": "30 mins before breakfast on empty stomach",
                    "duration": "15 Days",
                    "purpose": "Gastric acid reduction & stomach protection",
                    "instructions_hi": "सुबह खाली पेट 1 गोली लें।",
                    "instructions_en": "Take 1 tablet early morning with water, 30 mins before food.",
                    "warnings": "Short course for symptom relief. Avoid taking beyond 15 days without consult."
                }
            ]
        }
    },

    "sample_discharge_summary": {
        "title": "Hospital Inpatient Discharge Summary",
        "doc_type": "discharge_summary",
        "patient_name": "Rajesh Kumar Sharma",
        "patient_age": 52,
        "patient_gender": "Male",
        "date": "2026-08-04",
        "provider": "Max Super Speciality Hospital, Saket, New Delhi",
        "doctor_name": "Dr. Pradeep Mehra, MD (Pulmonology & Critical Care)",
        "raw_text": """MAX SUPER SPECIALITY HOSPITAL, SAKET, NEW DELHI
DISCHARGE SUMMARY - DEPARTMENT OF PULMONARY MEDICINE
Patient Name: Rajesh Kumar Sharma | IPD No: MAX-IP-2026-8921 | ABHA: 14-8921-4350-9812
Admission Date: 30-Jul-2026 | Discharge Date: 04-Aug-2026

FINAL DIAGNOSES:
1. Community Acquired Pneumonia (Right Middle Lobe Consolidation) - Resolved
2. Type 2 Diabetes Mellitus in Hyperglycemic Stress
3. Essential Systemic Hypertension

HOSPITAL COURSE & CLINICAL SUMMARY:
52-year-old gentleman presented with 4-day history of high-grade fever, productive cough with purulent sputum, and pleuritic chest discomfort. SpO2 on admission was 91% on room air.
Chest X-Ray confirmed right middle lobe bronchopneumonic consolidation.
Patient was admitted to High Dependency Unit (HDU) and initiated on IV Ceftriaxone 1g BD, IV Azithromycin 500mg OD, along with nebulization (Levolin + Budecort) and supportive hydration.
Blood sugars were managed with sliding-scale regular insulin during inpatient stay.
Patient became afebrile by Hospital Day 3. Inflammatory markers trended down:
- CRP on admission: 68 mg/L -> at discharge: 11 mg/L.
- Procalcitonin: 0.85 ng/mL -> 0.08 ng/mL.
SpO2 maintained at 98% on room air. Tolerating normal oral intake. Cleared for discharge in hemodynamically stable condition.

DISCHARGE VITALS:
Temperature: 98.4 F | Pulse: 76 bpm | BP: 130/84 mmHg | SpO2: 98% room air | Respiratory Rate: 16/min.

POST-DISCHARGE MEDICATION REGIMEN:
1. Tab. Augmentin 625 Duo (Amoxicillin 500mg + Clavulanic Acid 125mg) - 1 tab BD x 5 days (After food)
2. Tab. Levocet M (Levocetirizine 5mg + Montelukast 10mg) - 1 tab OD at night x 10 days
3. Duolin Respules Nebulization - Twice daily SOS for bronchospasm
4. Resume baseline anti-diabetic and anti-hypertensive oral therapy under endocrinologist review.

EMERGENCY RED FLAGS & WARNINGS:
Seek immediate emergency medical attention if patient experiences:
- Recurrent high fever (> 101 F) with rigors
- Sudden shortness of breath or SpO2 dropping below 93%
- Hemoptysis (coughing up blood) or persistent chest pain.
Follow-up: Pulmonology OPD in 7 days with repeat Chest X-Ray PA view.""",
        "parsed_data": {
            "diagnoses": ["Community Acquired Pneumonia (Right Middle Lobe) - Resolved", "Hyperglycemic Stress state", "Essential Systemic Hypertension"],
            "lab_tests": [
                {"name": "C-Reactive Protein (CRP)", "category": "Inflammatory Markers", "value": 11.0, "unit": "mg/L", "ref_min": 0.0, "ref_max": 5.0, "status": "ELEVATED", "is_abnormal": True},
                {"name": "Oxygen Saturation (SpO2)", "category": "Vitals", "value": 98.0, "unit": "%", "ref_min": 95.0, "ref_max": 100.0, "status": "NORMAL", "is_abnormal": False},
                {"name": "Pulse Rate", "category": "Vitals", "value": 76.0, "unit": "bpm", "ref_min": 60.0, "ref_max": 100.0, "status": "NORMAL", "is_abnormal": False},
                {"name": "Blood Pressure (Systolic)", "category": "Vitals", "value": 130.0, "unit": "mmHg", "ref_min": 90.0, "ref_max": 120.0, "status": "BORDERLINE", "is_abnormal": False}
            ],
            "medications": [
                {
                    "name": "Augmentin 625 Duo (Amoxicillin + Clavulanic Acid)",
                    "generic": "Amoxicillin 500mg + Clavulanate Potassium 125mg",
                    "dosage": "1 Tablet",
                    "frequency": "1 - 0 - 1 (Twice daily, Morning & Night)",
                    "timing": "After meals",
                    "duration": "5 Days",
                    "purpose": "Completing oral antibacterial step-down therapy for pneumonia",
                    "instructions_hi": "भोजन के बाद सुबह और शाम 1 गोली लें। 5 दिन का पूरा कोर्स अवश्य करें।",
                    "instructions_en": "Take 1 tablet twice daily after meals. Complete full 5-day course.",
                    "warnings": "Complete the full antibiotic course even if feeling fully recovered to prevent resistance."
                },
                {
                    "name": "Levocet M (Levocetirizine 5mg + Montelukast 10mg)",
                    "generic": "Levocetirizine + Montelukast",
                    "dosage": "1 Tablet",
                    "frequency": "0 - 0 - 1 (Once daily, Bedtime)",
                    "timing": "At night",
                    "duration": "10 Days",
                    "purpose": "Airway anti-inflammatory and allergic cough relief",
                    "instructions_hi": "रात को सोने से पहले 1 गोली लें।",
                    "instructions_en": "Take 1 tablet at night before sleeping.",
                    "warnings": "May cause mild drowsiness. Avoid driving immediately after intake."
                }
            ]
        }
    },

    "sample_thyroid_vitamin": {
        "title": "Endocrine & Micronutrient Diagnostic Panel",
        "doc_type": "lab_report",
        "patient_name": "Rajesh Kumar Sharma",
        "patient_age": 52,
        "patient_gender": "Male",
        "date": "2026-07-10",
        "provider": "Thyrocare Technologies Ltd., Mumbai",
        "doctor_name": "Dr. Ramesh Nair, MD",
        "raw_text": """THYROCARE TECHNOLOGIES LTD - NATIONAL CLINICAL REFERENCE LAB
Patient: Rajesh Kumar Sharma | Age: 52 Y | Sex: M | Date: 10-Jul-2026
ABHA ID: 14-8921-4350-9812 | Barcode: TC-THY-2026-44910

THYROID FUNCTION PROFILE
Test Name                    Result       Unit       Reference Range    Status
---------------------------------------------------------------------------------
Total Triiodothyronine (T3)  0.92         ng/mL      0.80 - 2.00        NORMAL
Total Thyroxine (T4)         6.4          ug/dL      5.1 - 14.1         NORMAL
TSH (Ultrasensitive)         7.84         uIU/mL     0.35 - 4.94        HIGH

MICRONUTRIENT & VITAMIN STATUS
Vitamin D3 (25-OH Cholecalc) 14.2         ng/mL      30.0 - 100.0       DEFICIENT (LOW)
Vitamin B12 (Cyanocobalamin) 168.0        pg/mL      211.0 - 911.0      DEFICIENT (LOW)
Serum Ferritin (Iron Stores) 42.0         ng/mL      22.0 - 322.0       NORMAL
Serum Calcium                9.1          mg/dL      8.8 - 10.2         NORMAL

CLINICAL INTERPRETATION:
1. Subclinical Hypothyroidism: Elevated TSH with normal free/total peripheral thyroid hormones.
2. Moderate Vitamin D3 deficiency: Predisposes to bone demineralization and insulin resistance.
3. Vitamin B12 deficiency: Common in chronic Metformin users; can mimic peripheral neuropathy symptoms.
Recommendation: Vitamin D3 cholecalciferol weekly 60k IU therapy and oral Methylcobalamin supplementation.""",
        "parsed_data": {
            "diagnoses": ["Subclinical Hypothyroidism", "Vitamin D3 Deficiency", "Vitamin B12 Deficiency (Likely Metformin-Associated)"],
            "lab_tests": [
                {"name": "Thyroid Stimulating Hormone (TSH)", "category": "Thyroid", "value": 7.84, "unit": "uIU/mL", "ref_min": 0.35, "ref_max": 4.94, "status": "HIGH", "is_abnormal": True},
                {"name": "Total Thyroxine (T4)", "category": "Thyroid", "value": 6.4, "unit": "ug/dL", "ref_min": 5.1, "ref_max": 14.1, "status": "NORMAL", "is_abnormal": False},
                {"name": "Vitamin D3 (25-OH)", "category": "Vitamins", "value": 14.2, "unit": "ng/mL", "ref_min": 30.0, "ref_max": 100.0, "status": "DEFICIENT", "is_abnormal": True},
                {"name": "Vitamin B12", "category": "Vitamins", "value": 168.0, "unit": "pg/mL", "ref_min": 211.0, "ref_max": 911.0, "status": "DEFICIENT", "is_abnormal": True},
                {"name": "Serum Calcium", "category": "Electrolytes", "value": 9.1, "unit": "mg/dL", "ref_min": 8.8, "ref_max": 10.2, "status": "NORMAL", "is_abnormal": False}
            ],
            "medications": []
        }
    }
}

# Longitudinal Timeline History for Rajesh Kumar Sharma to power the timeline & trends view
DEFAULT_TIMELINE_EVENTS = [
    {
        "id": "evt-1",
        "date": "2026-07-10",
        "type": "lab_report",
        "title": "Endocrine & Vitamin Panel (Thyrocare)",
        "summary": "Detected subclinical hypothyroidism (TSH 7.84) and severe Vitamin D3 (14.2 ng/mL) & B12 deficiencies.",
        "badge": "Thyroid & Vitamins",
        "badge_color": "warning",
        "document_key": "sample_thyroid_vitamin"
    },
    {
        "id": "evt-2",
        "date": "2026-07-30",
        "type": "inpatient_admission",
        "title": "Hospital Admission - Max Super Speciality",
        "summary": "Admitted with fever, productive cough, and right middle lobe pneumonia. Required IV antibiotics & oxygen.",
        "badge": "Hospitalization",
        "badge_color": "danger",
        "document_key": "sample_discharge_summary"
    },
    {
        "id": "evt-3",
        "date": "2026-08-04",
        "type": "discharge_summary",
        "title": "Hospital Discharge - Bronchopneumonia Resolved",
        "summary": "Successfully treated and discharged. CRP normalized from 68 to 11 mg/L. Prescribed oral Augmentin step-down.",
        "badge": "Discharge",
        "badge_color": "success",
        "document_key": "sample_discharge_summary"
    },
    {
        "id": "evt-4",
        "date": "2026-09-14",
        "type": "lab_report",
        "title": "Comprehensive Metabolic & Lipid Panel (Metropolis)",
        "summary": "Revealed uncontrolled HbA1c 8.8%, high fasting glucose 186 mg/dL, mixed dyslipidemia, and borderline kidney stress (Creatinine 1.35).",
        "badge": "Critical Lab Panel",
        "badge_color": "danger",
        "document_key": "sample_lab_report"
    },
    {
        "id": "evt-5",
        "date": "2026-09-16",
        "type": "prescription",
        "title": "Cardiology & Diabetology Consultation (Apollo)",
        "summary": "Dr. A.K. Verma initiated dual antidiabetic therapy (Glycomet-GP 2), Telmisartan for BP, and Rosuvastatin for high cholesterol.",
        "badge": "Prescription",
        "badge_color": "primary",
        "document_key": "sample_prescription"
    }
]

# Longitudinal Vitals Series for interactive SVG charts
VITALS_HISTORY = {
    "blood_sugar": [
        {"date": "2026-05-10", "fbs": 142, "ppbs": 198, "hba1c": 7.4},
        {"date": "2026-07-10", "fbs": 160, "ppbs": 220, "hba1c": 7.9},
        {"date": "2026-08-04", "fbs": 174, "ppbs": 245, "hba1c": 8.2},
        {"date": "2026-09-14", "fbs": 186, "ppbs": 264, "hba1c": 8.8}
    ],
    "blood_pressure": [
        {"date": "2026-05-10", "systolic": 132, "diastolic": 86},
        {"date": "2026-07-10", "systolic": 138, "diastolic": 88},
        {"date": "2026-07-30", "systolic": 154, "diastolic": 96},
        {"date": "2026-08-04", "systolic": 130, "diastolic": 84},
        {"date": "2026-09-16", "systolic": 148, "diastolic": 92}
    ],
    "cholesterol": [
        {"date": "2026-05-10", "total": 210, "ldl": 135, "triglycerides": 180},
        {"date": "2026-07-10", "total": 225, "ldl": 148, "triglycerides": 195},
        {"date": "2026-09-14", "total": 242, "ldl": 160, "triglycerides": 218}
    ]
}
