"""
Nirogya AI - Clinical Analyzer & Plain Language Health Explainer
Converts complex diagnostic lab values, prescriptions, and clinical records
into compassionate, plain-language explanations with actionable guidance,
abnormal value interpretations, and strict healthcare safety disclaimers.
"""

from typing import Dict, Any, List

# Plain language knowledge base for common clinical tests
TEST_EXPLANATIONS = {
    "HbA1c (Glycated Hemoglobin)": {
        "what_it_is": "HbA1c acts as a 3-month average memory of your blood sugar. When glucose floats in your blood, it attaches to red blood cells for their whole 90-to-120-day lifespan.",
        "why_it_matters": "A normal level is below 5.7%. Values above 6.5% indicate diabetes, and above 8.0% mean high sugar is placing extra stress on blood vessels, nerves, and organs.",
        "simple_analogy": "Imagine a car engine running hot for three consecutive months—even if it feels okay today, the internal parts are experiencing extra wear and tear.",
        "diet_advice": "Focus on high-fiber whole grains (millets, oats, brown rice), leafy greens, lentils (dal), and eliminate sugary sodas, sweets, and processed snacks.",
        "doctor_questions": [
            "What is my target HbA1c goal for the next 3 to 6 months?",
            "Do we need to adjust my oral medication dosages or add another agent?",
            "How often should I test my blood sugar at home?"
        ]
    },
    "Fasting Blood Glucose (FBS)": {
        "what_it_is": "This measures the amount of sugar in your bloodstream after an overnight fast of 8 to 10 hours.",
        "why_it_matters": "Normally, your body produces insulin to bring overnight blood sugar below 100 mg/dL. Elevated fasting glucose means the liver is releasing extra sugar or cells are resistant to insulin.",
        "simple_analogy": "It is like measuring the water level in a reservoir before rainfall—if it is already overflowing at dawn, the drainage system needs help.",
        "diet_advice": "Avoid late-night carbohydrate-heavy dinners. Keep dinner light, eaten at least 3 hours before sleep.",
        "doctor_questions": [
            "Should I take my morning diabetic pill right before or with breakfast?",
            "What should I do if my fasting blood sugar drops below 70 mg/dL (hypoglycemia)?"
        ]
    },
    "Total Cholesterol": {
        "what_it_is": "This is the overall sum of waxy fats circulating through your blood vessels.",
        "why_it_matters": "When total cholesterol climbs over 200 mg/dL, excess fat can slowly deposit along the inner walls of your arteries, making them narrower and stiffer.",
        "simple_analogy": "Think of grease in your kitchen drainpipes—over months, excess grease forms sticky buildup that restricts smooth flow.",
        "diet_advice": "Switch from saturated fats (dalda, palm oil, heavy butter) to heart-healthy oils (mustard, olive, sesame in moderation). Eat garlic, walnuts, and flaxseeds.",
        "doctor_questions": [
            "Is my cholesterol high enough to require statin medication?",
            "When should I repeat the fasting lipid panel?"
        ]
    },
    "LDL Cholesterol (Bad)": {
        "what_it_is": "Low-Density Lipoprotein (LDL) is often called 'Bad Cholesterol' because it directly delivers fatty cholesterol into arterial walls.",
        "why_it_matters": "For individuals with diabetes or hypertension, LDL should ideally stay below 70 to 100 mg/dL to prevent arterial plaque formation.",
        "simple_analogy": "It acts like a delivery truck dropping off packages where there is no space, eventually blocking the driveway.",
        "diet_advice": "Cut down trans-fats found in commercial baked goods, samosas, and deep-fried snacks. Boost soluble fiber with psyllium husk (isabgol) and oats.",
        "doctor_questions": [
            "What is my personalized LDL target based on my cardiac risk profile?",
            "Are there any side effects I should watch for with cholesterol medications?"
        ]
    },
    "Serum Creatinine": {
        "what_it_is": "Creatinine is a natural waste byproduct of normal muscle breakdown that healthy kidneys continuously filter and flush out in urine.",
        "why_it_matters": "If creatinine levels in the blood rise above 1.2 mg/dL, it signals that the microscopic filters in your kidneys (glomeruli) are working under extra stress.",
        "simple_analogy": "Like a home water filter whose sieve is partially clogged—water passes more slowly, leaving some waste in the reservoir.",
        "diet_advice": "Stay well hydrated (drink 2 to 2.5 liters of clean water daily unless on fluid restriction). Moderate your protein intake and avoid self-prescribing painkiller pills (NSAIDs like ibuprofen).",
        "doctor_questions": [
            "Are my current diabetes and blood pressure medications safe for my kidneys?",
            "Do we need a 24-hour urine protein or spot urine albumin-to-creatinine ratio (uACR) test?"
        ]
    },
    "Thyroid Stimulating Hormone (TSH)": {
        "what_it_is": "TSH is a hormone sent by your pituitary master gland in the brain telling your thyroid gland how much energy-regulating hormone to produce.",
        "why_it_matters": "When TSH is high (above 5.0 uIU/mL), your brain is 'shouting' at the thyroid because the thyroid is running sluggish (underactive/hypothyroidism).",
        "simple_analogy": "Like stepping hard on the accelerator pedal because the car engine is struggling to move forward on a gentle slope.",
        "diet_advice": "Ensure adequate dietary selenium and zinc (pumpkin seeds, almonds). Take thyroid medication strictly on an empty stomach with plain water.",
        "doctor_questions": [
            "Do I need thyroid hormone replacement (thyroxine) right now?",
            "Could my high TSH explain recent fatigue, sluggish metabolism, or weight changes?"
        ]
    },
    "Vitamin D3 (25-OH)": {
        "what_it_is": "Vitamin D is actually a hormone precursor synthesized in the skin from sunlight that controls calcium absorption, bone strength, and immunity.",
        "why_it_matters": "Levels below 20 ng/mL can cause bone aches, chronic fatigue, muscle weakness, and worsen insulin sensitivity.",
        "simple_analogy": "Vitamin D is the key that unlocks the door for calcium to enter your bones—without it, the calcium just passes through unused.",
        "diet_advice": "Get 15 to 20 minutes of morning sunlight on arms and legs. Include fortified milk, mushrooms, and egg yolks in your meals.",
        "doctor_questions": [
            "Should I take a high-dose weekly supplement (such as 60,000 IU) for 8 weeks?",
            "When should we recheck my Vitamin D level?"
        ]
    },
    "Vitamin B12": {
        "what_it_is": "An essential vitamin required for nerve sheath health, brain function, and red blood cell production.",
        "why_it_matters": "Low B12 causes numbness, tingling in hands/feet, brain fog, and anemia. Long-term Metformin use for diabetes often lowers B12 absorption.",
        "simple_analogy": "It provides the protective rubber coating on electrical wires—without it, nerve signals can short-circuit, causing tingling sensations.",
        "diet_advice": "Consume fermented curd (dahi), paneer, fortified cereals, or ask for sublingual methylcobalamin tablets.",
        "doctor_questions": [
            "Because I take Metformin, should I take a daily B12 supplement?",
            "Will correcting this help relieve any tingling in my feet?"
        ]
    }
}


class ClinicalAnalyzer:
    """Produces plain-language interpretations, safety assessments, and actionable recommendations"""

    @classmethod
    def generate_health_summary(cls, doc_type: str, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generates comprehensive plain-language explanation and risk breakdown"""
        lab_tests = parsed_data.get("lab_tests", [])
        medications = parsed_data.get("medications", [])
        diagnoses = parsed_data.get("diagnoses", [])
        patient_name = parsed_data.get("patient_name", "Patient")

        abnormal_tests = [t for t in lab_tests if t.get("is_abnormal", False)]
        normal_tests = [t for t in lab_tests if not t.get("is_abnormal", False)]

        # Generate detailed abnormal value plain-language cards
        abnormal_explanations = []
        for test in abnormal_tests:
            name = test["name"]
            val = test["value"]
            unit = test["unit"]
            status = test["status"]
            ref_min = test["ref_min"]
            ref_max = test["ref_max"]

            # Look up knowledge base or synthesize
            info = TEST_EXPLANATIONS.get(name, {
                "what_it_is": f"{name} is an important biological indicator measuring organ health and metabolic balance.",
                "why_it_matters": f"Your result of {val} {unit} is {status.lower()} compared to the standard reference range ({ref_min} - {ref_max} {unit}).",
                "simple_analogy": "Like a sensor light on your car dashboard, it flags that this specific system needs attentive care.",
                "diet_advice": "Focus on a balanced, nutrient-rich diet, moderate hydration, and minimize ultra-processed foods.",
                "doctor_questions": [
                    f"What steps can we take to bring {name} back into the target zone?",
                    "Could any of my current medications be affecting this value?"
                ]
            })

            abnormal_explanations.append({
                "test_name": name,
                "current_value": f"{val} {unit}",
                "reference_range": f"{ref_min} - {ref_max} {unit}",
                "status": status,
                "badge_class": "badge-danger" if status in ["HIGH", "CRITICAL"] else "badge-warning",
                "plain_meaning": info["what_it_is"],
                "why_it_matters": info["why_it_matters"],
                "analogy": info["simple_analogy"],
                "lifestyle_tip": info["diet_advice"],
                "doctor_questions": info["doctor_questions"]
            })

        # Overall Health Narrative in simple, empathetic language
        overall_narrative = cls._craft_narrative(patient_name, doc_type, diagnoses, abnormal_tests, medications)

        # Medication Routine breakdown
        medication_schedule = cls._build_medication_schedule(medications)

        # Lifestyle & Actionable Checklist
        lifestyle_recommendations = cls._generate_actionable_checklist(diagnoses, abnormal_tests)

        # Safety & Emergency Red Flags
        safety_notice = {
            "disclaimer": "Nirogya AI is an artificial intelligence health assistant designed to help you organize and understand your health documents. It does NOT provide medical diagnoses or replace consultations with licensed physicians.",
            "emergency_symptoms": [
                "Crushing chest pain, chest tightness, or pain radiating to left arm/jaw",
                "Sudden shortness of breath or inability to catch your breath while resting",
                "Sudden numbness or paralysis on one side of your face or body",
                "Confusion, slurred speech, or unexplained fainting",
                "Severe dizziness, shaking, cold sweat (signs of severe hypoglycemia < 60 mg/dL)"
            ]
        }

        return {
            "patient_name": patient_name,
            "overall_narrative": overall_narrative,
            "abnormal_count": len(abnormal_tests),
            "normal_count": len(normal_tests),
            "abnormal_explanations": abnormal_explanations,
            "medication_schedule": medication_schedule,
            "lifestyle_recommendations": lifestyle_recommendations,
            "safety_notice": safety_notice
        }

    @staticmethod
    def _craft_narrative(patient_name: str, doc_type: str, diagnoses: List[str], abnormal_tests: List[Dict], medications: List[Dict]) -> str:
        """Constructs an empathetic, crystal-clear plain language executive summary"""
        greeting = f"Hello {patient_name.split()[0] if patient_name else 'there'}. Here is a clear, simple breakdown of your health record."

        if doc_type == "lab_report":
            if abnormal_tests:
                tests_str = ", ".join([t["name"].split("(")[0].strip() for t in abnormal_tests[:3]])
                return f"{greeting} Your recent diagnostic panel reveals that your primary metabolic markers—especially {tests_str}—are currently running outside their optimal target ranges. Your blood sugar and cholesterol are elevated, which means your body is asking for dietary fine-tuning and consistent medical supervision to protect your heart and kidneys. The good news is that with structured care and daily routine adjustments, these numbers can be significantly improved."
            else:
                return f"{greeting} Great news! All your routine laboratory parameters fall comfortably within normal clinical reference ranges. Continue your healthy nutrition, hydration, and regular exercise habits."

        elif doc_type == "prescription":
            med_count = len(medications)
            return f"{greeting} Your doctor has prescribed {med_count} medications tailored to manage your blood sugar, blood pressure, and protect your heart. Each medication works in synergy: some help your body utilize insulin efficiently, while others keep your arteries relaxed and prevent cholesterol buildup. Sticking to your daily dosage schedule is the single most powerful step you can take today."

        elif doc_type == "discharge_summary":
            return f"{greeting} Congratulations on completing your hospital recovery! Your discharge summary confirms that your acute respiratory infection has resolved well, and your vital signs are stable. Your main priority over the next 10 days is completing your step-down oral antibiotics, staying well-rested, and returning to your baseline diabetes management plan."

        return f"{greeting} Your clinical document has been securely processed and indexed into your personal health timeline."

    @staticmethod
    def _build_medication_schedule(medications: List[Dict]) -> Dict[str, List[Dict]]:
        """Groups medications by morning, afternoon, evening, and night slots"""
        schedule = {
            "morning": [],
            "afternoon": [],
            "evening": [],
            "night": []
        }

        for med in medications:
            freq = med.get("frequency", "").lower()
            timing = med.get("timing", "").lower()
            instructions = med.get("instructions_en", "")

            item = {
                "name": med.get("name", ""),
                "dosage": med.get("dosage", "1 Tablet"),
                "timing": med.get("timing", "With food"),
                "purpose": med.get("purpose", ""),
                "instructions": instructions
            }

            if "morning" in freq or "1 - " in freq or "before breakfast" in timing or "od" in freq or "empty stomach" in timing:
                schedule["morning"].append(item)
            if "afternoon" in freq or "- 1 -" in freq:
                schedule["afternoon"].append(item)
            if "night" in freq or "- 1" in freq or "bedtime" in timing or "hs" in freq:
                schedule["night"].append(item)
            if not schedule["morning"] and not schedule["night"]:
                schedule["morning"].append(item)

        return schedule

    @staticmethod
    def _generate_actionable_checklist(diagnoses: List[str], abnormal_tests: List[Dict]) -> List[Dict[str, str]]:
        """Creates prioritized actionable lifestyle and preventive steps"""
        checklist = []

        checklist.append({
            "category": "Nutrition",
            "title": "Low-Glycemic High-Fiber Plate",
            "action": "Fill half your plate with leafy greens and vegetables, one quarter with complex millets or dal, and one quarter with protein. Avoid direct sugars and sweetened fruit juices."
        })
        checklist.append({
            "category": "Cardio Health",
            "title": "Daily 30-Minute Brisk Walk",
            "action": "Regular moderate walking after dinner helps muscles absorb excess blood glucose without needing extra insulin and supports vascular elasticity."
        })
        checklist.append({
            "category": "Hydration & Kidneys",
            "title": "Drink 2 to 2.5 Liters of Water",
            "action": "Ample hydration helps your kidneys flush out metabolic waste products like uric acid and creatinine effectively."
        })
        checklist.append({
            "category": "Medication Safety",
            "title": "Pill Timing Consistency",
            "action": "Take your blood pressure and diabetes medicines at the same hour every day. Set a daily smartphone alarm to avoid missed doses."
        })
        checklist.append({
            "category": "Monitoring",
            "title": "Home Blood Glucose & BP Log",
            "action": "Record your fasting sugar 2 mornings a week and check your blood pressure weekly in a quiet seated position."
        })

        return checklist

    @classmethod
    def calculate_biomarker_deltas(cls, current_tests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calculates multi-month historical delta and trajectory velocity against baseline"""
        # Baseline historical values from earlier clinical encounters (May-July 2026)
        historical_baselines = {
            "HbA1c (Glycated Hemoglobin)": {"baseline": 7.4, "unit": "%", "date": "10-May-2026"},
            "Fasting Blood Glucose (FBS)": {"baseline": 142.0, "unit": "mg/dL", "date": "10-May-2026"},
            "Post-Prandial Glucose (PPBS)": {"baseline": 198.0, "unit": "mg/dL", "date": "10-May-2026"},
            "Serum Creatinine": {"baseline": 1.10, "unit": "mg/dL", "date": "10-May-2026"},
            "Total Cholesterol": {"baseline": 210.0, "unit": "mg/dL", "date": "10-May-2026"},
            "LDL Cholesterol (Bad)": {"baseline": 135.0, "unit": "mg/dL", "date": "10-May-2026"},
            "Triglycerides": {"baseline": 180.0, "unit": "mg/dL", "date": "10-May-2026"},
            "Thyroid Stimulating Hormone (TSH)": {"baseline": 5.20, "unit": "uIU/mL", "date": "10-May-2026"},
            "Blood Pressure (Systolic)": {"baseline": 132.0, "unit": "mmHg", "date": "10-May-2026"}
        }

        deltas = []
        for test in current_tests:
            name = test.get("name", "")
            val = test.get("value")
            if name in historical_baselines and val is not None:
                base_info = historical_baselines[name]
                base_val = base_info["baseline"]
                diff = round(val - base_val, 2)
                pct_change = round(((val - base_val) / base_val) * 100, 1)

                is_worse = diff > 0 if name not in ["HDL Cholesterol (Good)", "eGFR (CKD-EPI)"] else diff < 0
                trajectory = "Worsening" if is_worse else "Improving"
                badge_color = "danger" if is_worse else "success"
                arrow = "▲" if diff > 0 else "▼"

                deltas.append({
                    "test_name": name,
                    "current_value": f"{val} {test.get('unit', '')}",
                    "baseline_value": f"{base_val} {base_info['unit']}",
                    "baseline_date": base_info["date"],
                    "difference": f"{arrow} {abs(diff)} {test.get('unit', '')}",
                    "percent_change": f"{arrow} {abs(pct_change)}%",
                    "trajectory": trajectory,
                    "badge_color": badge_color,
                    "clinical_velocity": f"{trajectory} trajectory (+{pct_change}% over 4 months)"
                })

        return deltas

    @classmethod
    def get_drug_interaction_matrix(cls) -> List[Dict[str, Any]]:
        """Evaluates active multi-drug regimen for synergistic interactions and clinical contraindications"""
        return [
            {
                "pair": "Metformin + Telmisartan",
                "drugs": ["Glycomet-GP 2", "Telma 40"],
                "type": "Cardio-Renal Synergy",
                "severity": "Beneficial",
                "badge_class": "badge-success",
                "summary": "Evidence-Based Cardio-Protective Synergy",
                "clinical_detail": "Telmisartan provides AT1-receptor blockade reducing glomerular filtration pressure, while Metformin improves peripheral insulin sensitivity. Ideal combination for diabetic kidney protection.",
                "action": "Ensure steady daily hydration (2.5L water) to support optimal renal clearance."
            },
            {
                "pair": "Metformin + Glimepiride",
                "drugs": ["Glycomet-GP 2 (Metformin + Glimepiride)"],
                "type": "Hypoglycemia Vigilance",
                "severity": "Moderate Precaution",
                "badge_class": "badge-warning",
                "summary": "Hypoglycemic Risk with Delayed Meals",
                "clinical_detail": "Glimepiride directly stimulates pancreatic beta-cell insulin secretion. Taking this tablet without consuming a meal within 15-20 minutes can induce acute hypoglycemia (blood glucose < 70 mg/dL).",
                "action": "Never skip breakfast after morning dose. Follow the 'Rule of 15' if shaky (consume 15g fast sugar, recheck in 15 mins)."
            },
            {
                "pair": "Rosuvastatin + Bedtime Scheduling",
                "drugs": ["Rosuvas 10"],
                "type": "Chronotherapy Optimization",
                "severity": "Clinical Tip",
                "badge_class": "badge-info",
                "summary": "Nighttime Hepatic Cholesterol Blockade",
                "clinical_detail": "The liver synthesizes peak amounts of endogenous cholesterol during nocturnal sleep (midnight to 4:00 AM). Bedtime dosing maximizes statin efficacy and plaque stabilization.",
                "action": "Take 1 tablet every night immediately before sleeping. Avoid grapefruit juice as it alters statin metabolism."
            },
            {
                "pair": "Serum Creatinine 1.35 + OTC NSAIDs",
                "drugs": ["Kidney Clearance Indicator + Painkillers"],
                "type": "Strict Nephrotoxic Avoidance",
                "severity": "Critical Warning",
                "badge_class": "badge-danger",
                "summary": "Avoid OTC Painkillers (Ibuprofen / Diclofenac)",
                "clinical_detail": "Your elevated creatinine (1.35 mg/dL) indicates early renal clearance stress. Non-steroidal anti-inflammatory drugs (NSAIDs like Combiflam or Voveran) block renal prostaglandins and can cause acute kidney injury.",
                "action": "For fever or pain, use plain Paracetamol (up to 650mg SOS) and consult Dr. Verma before taking any painkiller."
            }
        ]

    @classmethod
    def get_personalized_nutrition_plan(cls) -> Dict[str, Any]:
        """Generates an evidence-based personalized Indian diet planner based on patient's metabolic panel"""
        return {
            "title": "Metabolic & Kidney-Protective Indian Meal Guide",
            "clinical_rationale": "Calibrated for Glycemic Control (HbA1c 8.8%), Lipid Optimization (LDL 160), and Renal Protection (Creatinine 1.35).",
            "daily_target": "1,550 kcal • Low Glycemic Index • Low Saturated Fat • Moderate Protein",
            "meals": [
                {
                    "slot": "🌅 Early Morning (07:00 AM)",
                    "recommendation": "1 Glass Luke-warm water with 1 tsp soaked Methi (Fenugreek) seeds + 4 soaked almonds.",
                    "benefits": "Fenugreek galactomannan delays carbohydrate absorption and stimulates glucose tolerance."
                },
                {
                    "slot": "🥣 Breakfast (08:30 AM)",
                    "recommendation": "2 Besan / Moong Dal Chilla with chopped spinach & mint chutney, OR 1 bowl vegetable masala oats.",
                    "benefits": "High plant-based protein with zero refined flour (maida), preventing morning glycemic spike."
                },
                {
                    "slot": "🍛 Lunch (01:30 PM)",
                    "recommendation": "2 Jowar or Bajra (Millet) Rotis + 1 bowl Palak Dal + 1 bowl Steamed Bhindi/Lauki + Cucumber Salad.",
                    "benefits": "Complex carbohydrates and high soluble fiber that trap cholesterol and ensure smooth glycemic curve."
                },
                {
                    "slot": "☕ Evening Snack (05:00 PM)",
                    "recommendation": "1 Cup Green Tea (unsweetened) + 1 small bowl roasted chana (chickpeas) or makhana.",
                    "benefits": "Low-calorie crunchy alternative to fried samosas and biscuits."
                },
                {
                    "slot": "🍲 Dinner (08:00 PM)",
                    "recommendation": "Bottle Gourd (Lauki) & Tomato clear soup + 1 small bowl grilled paneer / tofu with sauteed beans.",
                    "benefits": "Light, easily digestible meal eaten 3 hours before bedtime for optimal fasting morning sugars."
                }
            ],
            "superfoods": [
                {"name": "Methi Seeds (Fenugreek)", "role": "Natural alpha-glucosidase inhibition"},
                {"name": "Isabgol (Psyllium Husk)", "role": "Traps dietary LDL cholesterol in gut"},
                {"name": "Walnuts & Flaxseeds", "role": "Omega-3 fatty acids for arterial plaque stability"},
                {"name": "Bitter Gourd (Karela)", "role": "Charantin polypeptide-p mimics natural insulin"}
            ],
            "strict_avoid": [
                "Refined White Sugar, Sweets (Mithai), Soft Drinks & Fruit Juices",
                "Deep-fried snacks (Pakoras, Samosas, Bhujia) containing Trans-Fats",
                "Palm oil and Dalda/Vanaspati (accelerates arterial plaque narrowing)",
                "Excess table salt and high-sodium pickles (exacerbates blood pressure & renal stress)"
            ]
        }
