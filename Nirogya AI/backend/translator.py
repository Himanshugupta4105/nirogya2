"""
Nirogya AI - Multi-Language Regional Translation Engine
Provides regional language translations for:
- English (EN)
- Hindi (HI) - हिन्दी
- Telugu (TE) - తెలుగు
- Tamil (TA) - தமிழ்
- Bengali (BN) - বাংলা
- Marathi (MR) - मराठी
Translates medical summaries, abnormal test interpretations, medication instructions,
and conversational Copilot responses.
"""

from typing import Dict, Any, List

UI_LOCALES = {
    "en": {
        "app_title": "Nirogya AI",
        "app_tagline": "Personal Health Copilot",
        "upload_headline": "Smart Medical Record Ingestion",
        "upload_sub": "Drag & drop prescriptions, lab reports, or discharge summaries (PDF, PNG, JPG)",
        "btn_upload": "Upload Document",
        "btn_sample_lab": "Load Metabolic Lab Panel",
        "btn_sample_rx": "Load Cardio-Diabetic Prescription",
        "btn_sample_discharge": "Load Hospital Discharge Summary",
        "tab_overview": "Health Summary",
        "tab_timeline": "Health Timeline",
        "tab_vitals": "Vitals Trends",
        "tab_medications": "Active Medications",
        "tab_fhir": "ABDM & FHIR R4",
        "tab_architecture": "System Architecture",
        "copilot_title": "AI Health Copilot",
        "copilot_placeholder": "Ask anything about your reports, medicines, or health...",
        "copilot_send": "Ask Copilot",
        "abnormal_badge": "Action Required",
        "normal_badge": "Optimal Range",
        "abha_linked": "ABHA Linked",
        "disclaimer_text": "Informational health guidance only. Always consult your treating physician."
    },
    "hi": {
        "app_title": "निरोग्य AI (Nirogya AI)",
        "app_tagline": "आपका व्यक्तिगत स्वास्थ्य सहायक (AI Health Copilot)",
        "upload_headline": "स्मार्ट मेडिकल रिकॉर्ड विश्लेषण",
        "upload_sub": "पर्चे (Prescription), लैब रिपोर्ट या डिस्चार्ज समरी यहाँ अपलोड करें (PDF, PNG, JPG)",
        "btn_upload": "दस्तावेज़ अपलोड करें",
        "btn_sample_lab": "सैंपल लैब रिपोर्ट देखें (मधुमेह व कोलेस्ट्रॉल)",
        "btn_sample_rx": "सैंपल डॉक्टर पर्चा देखें (दवाइयाँ)",
        "btn_sample_discharge": "अस्पताल डिस्चार्ज समरी देखें",
        "tab_overview": "स्वास्थ्य सारांश (Summary)",
        "tab_timeline": "स्वास्थ्य टाइमलाइन (Timeline)",
        "tab_vitals": "वाइटल्स व रुझान (Trends)",
        "tab_medications": "चल रही दवाइयाँ (Medicines)",
        "tab_fhir": "ABDM व FHIR R4 रिकॉर्ड",
        "tab_architecture": "सिस्टम आर्किटेक्चर",
        "copilot_title": "AI स्वास्थ्य को-पायलट",
        "copilot_placeholder": "अपनी रिपोर्ट, दवाओं या सेहत के बारे में पूछें...",
        "copilot_send": "पूछें",
        "abnormal_badge": "ध्यान देने योग्य (असामान्य)",
        "normal_badge": "सामान्य सीमा में",
        "abha_linked": "ABHA आईडी लिंक है",
        "disclaimer_text": "यह केवल शैक्षिक मार्गदर्शन के लिए है। किसी भी बदलाव से पहले अपने चिकित्सक से परामर्श लें।"
    },
    "te": {
        "app_title": "నిరోగ్య AI (Nirogya AI)",
        "app_tagline": "మీ వ్యక్తిగత ఆరోగ్య సహచరుడు",
        "upload_headline": "మెడికల్ రికార్డుల స్మార్ట్ విశ్లేషణ",
        "upload_sub": "ప్రిస్క్రిప్షన్లు, ల్యాబ్ రిపోర్టులు లేదా డిశ్చార్జ్ సారాంశాన్ని అప్‌లోడ్ చేయండి",
        "btn_upload": "పత్రం అప్‌లోడ్ చేయండి",
        "btn_sample_lab": "ల్యాబ్ రిపోర్ట్ చూడండి",
        "btn_sample_rx": "ప్రిస్క్రిప్షన్ చూడండి",
        "btn_sample_discharge": "డిశ్చార్జ్ సారాంశం చూడండి",
        "tab_overview": "ఆరోగ్య సారాంశం",
        "tab_timeline": "టైమ్‌లైన్",
        "tab_vitals": "వైటల్స్ ట్రెండ్స్",
        "tab_medications": "మందుల వివరాలు",
        "tab_fhir": "ABDM & FHIR R4",
        "tab_architecture": "సిస్టమ్ ఆర్కిటెక్చర్",
        "copilot_title": "AI హెల్త్ కోపైలట్",
        "copilot_placeholder": "మీ రిపోర్టులు లేదా మందుల గురించి అడగండి...",
        "copilot_send": "అడగండి",
        "abnormal_badge": "శ్రద్ధ అవసరం",
        "normal_badge": "సాధారణ పరిధి",
        "abha_linked": "ABHA లింక్ చేయబడింది",
        "disclaimer_text": "ఇది అవగాహన కోసం మాత్రమే. వైద్యుల సలహా తప్పనిసరి."
    },
    "ta": {
        "app_title": "நிரோக்யா AI (Nirogya AI)",
        "app_tagline": "உங்கள் தனிப்பட்ட சுகாதார வழிகாட்டி",
        "upload_headline": "மருத்துவ ஆவண பகுப்பாய்வு",
        "upload_sub": "மருந்துச் சீட்டு, ஆய்வக அறிக்கை அல்லது டிஸ்சார்ஜ் சுருக்கத்தை பதிவேற்றவும்",
        "btn_upload": "பதிவேற்றுக",
        "btn_sample_lab": "ஆய்வக அறிக்கை காண்க",
        "btn_sample_rx": "மருந்துச் சீட்டு காண்க",
        "btn_sample_discharge": "டிஸ்சார்ஜ் சுருக்கம் காண்க",
        "tab_overview": "சுகாதார சுருக்கம்",
        "tab_timeline": "காலவரிசை",
        "tab_vitals": "உடல்நிலை போக்குகள்",
        "tab_medications": "நடப்பு மருந்துகள்",
        "tab_fhir": "ABDM & FHIR R4",
        "tab_architecture": "கட்டமைப்பு",
        "copilot_title": "AI மருத்துவ வழிகாட்டி",
        "copilot_placeholder": "உங்கள் அறிக்கைகள் அல்லது மருந்துகள் பற்றி கேட்கவும்...",
        "copilot_send": "கேளுங்கள்",
        "abnormal_badge": "கவனம் தேவை",
        "normal_badge": "சாதாரண அளவு",
        "abha_linked": "ABHA இணைக்கப்பட்டது",
        "disclaimer_text": "தகவல் வழிகாட்டுதலுக்கு மட்டுமே. மருத்துவரை அணுகவும்."
    },
    "bn": {
        "app_title": "নিরোগ্য AI (Nirogya AI)",
        "app_tagline": "আপনার ব্যক্তিগত স্বাস্থ্য সহযোগী",
        "upload_headline": "স্মার্ট মেডিকেল রেকর্ড বিশ্লেষণ",
        "upload_sub": "প্রেসক্রিপশন, ল্যাব রিপোর্ট বা ডিসচার্জ সামারি আপলোড করুন",
        "btn_upload": "ডকুমেন্ট আপলোড করুন",
        "btn_sample_lab": "নমুনা ল্যাব রিপোর্ট দেখুন",
        "btn_sample_rx": "নমুনা প্রেসক্রিপশন দেখুন",
        "btn_sample_discharge": "ডিসচার্জ সামারি দেখুন",
        "tab_overview": "স্বাস্থ্য সারাংশ",
        "tab_timeline": "টাইমলাইন",
        "tab_vitals": "ভাইটালস ট্রেন্ড",
        "tab_medications": "চলতি ওষুধ",
        "tab_fhir": "ABDM ও FHIR R4",
        "tab_architecture": "সিস্টেম আর্কিটেকচার",
        "copilot_title": "AI হেলথ কো-পাইলট",
        "copilot_placeholder": "আপনার রিপোর্ট বা ওষুধ সম্পর্কে প্রশ্ন করুন...",
        "copilot_send": "জিজ্ঞাসা করুন",
        "abnormal_badge": "বিশেষ নজর প্রয়োজন",
        "normal_badge": "স্বাভাবিক মাত্রা",
        "abha_linked": "ABHA সংযুক্ত",
        "disclaimer_text": "শুধুমাত্র তথ্যের উদ্দেশ্যে। ডাক্তারের পরামর্শ নেওয়া আবশ্যক।"
    },
    "mr": {
        "app_title": "निरोग्य AI (Nirogya AI)",
        "app_tagline": "तुमचा वैयक्तिक आरोग्य सहाय्यक",
        "upload_headline": "वैद्यकीय अहवाल स्मार्ट विश्लेषण",
        "upload_sub": "प्रिस्क्रिप्शन, लॅब रिपोर्ट किंवा डिस्चार्ज सारांश अपलोड करा",
        "btn_upload": "कागदपत्र अपलोड करा",
        "btn_sample_lab": "लॅब रिपोर्ट पहा",
        "btn_sample_rx": "प्रिस्क्रिप्शन पहा",
        "btn_sample_discharge": "डिस्चार्ज सारांश पहा",
        "tab_overview": "आरोग्य सारांश",
        "tab_timeline": "टाइमलाइन",
        "tab_vitals": "व्हाइटल्स ट्रेंड्स",
        "tab_medications": "सध्याची औषधे",
        "tab_fhir": "ABDM आणि FHIR R4",
        "tab_architecture": "सिस्टम रचना",
        "copilot_title": "AI आरोग्य मार्गदर्शक",
        "copilot_placeholder": "आपल्या रिपोर्ट किंवा औषधांविषयी विचारा...",
        "copilot_send": "विचारा",
        "abnormal_badge": "लक्ष देणे गरजेचे",
        "normal_badge": "सामान्य मर्यादा",
        "abha_linked": "ABHA जोडलेले",
        "disclaimer_text": "केवळ माहितीच्या उद्देशाने. डॉक्टरांचा सल्ला अवश्य घ्या."
    }
}

# Regional summaries for pre-canned explanations
REGIONAL_TRANSLATIONS = {
    "hi": {
        "HbA1c (Glycated Hemoglobin)": {
            "plain_meaning": "HbA1c आपके पिछले 3 महीनों के औसत ब्लड शुगर (शर्करा) की माप है।",
            "why_it_matters": "आपका परिणाम 8.8% है जो सामान्य सीमा (5.6% से कम) से अधिक है। यह दर्शाता है कि रक्त में शुगर का स्तर लगातार बढ़ा हुआ है, जिससे हृदय और गुर्दों पर दबाव पड़ता है।",
            "lifestyle_tip": "मीठे खाद्य पदार्थ, कोल्ड ड्रिंक्स और तली हुई चीजों से बचें। मिलेट्स (बाजरा, ज्वार), हरी सब्जियां और दालें खाएं।"
        },
        "Fasting Blood Glucose (FBS)": {
            "plain_meaning": "यह रात भर भूखे रहने के बाद सुबह खाली पेट आपके रक्त में शुगर की मात्रा बताता है।",
            "why_it_matters": "आपका स्तर 186 mg/dL है, जबकि सामान्य स्तर 100 mg/dL से कम होना चाहिए।",
            "lifestyle_tip": "रात का भोजन हल्का रखें और सोने से कम से कम 3 घंटे पहले खाएं।"
        },
        "Total Cholesterol": {
            "plain_meaning": "यह आपके रक्त में तैरने वाले वसा (फैट्स) की कुल मात्रा है।",
            "why_it_matters": "242 mg/dL का स्तर अधिक है (200 से कम होना चाहिए)। इससे धमनियों में रुकावट का जोखिम बढ़ता है।",
            "lifestyle_tip": "डालडा, पाम तेल और अत्यधिक मक्खन से बचें। सरसों का तेल या जैतून का तेल सीमित मात्रा में उपयोग करें।"
        },
        "Serum Creatinine": {
            "plain_meaning": "क्रिएटिनिन मांसपेशियों का प्राकृतिक अपशिष्ट उत्पाद है, जिसे स्वस्थ गुर्दे (किडनी) छानकर पेशाब के रास्ते बाहर निकालते हैं।",
            "why_it_matters": "1.35 mg/dL का स्तर सामान्य से थोड़ा अधिक है। इसका मतलब है कि गुर्दे पर अतिरिक्त तनाव है।",
            "lifestyle_tip": "भरपूर मात्रा में स्वच्छ पानी पिएं (दिन में 2 से 2.5 लीटर)। बिना डॉक्टर की सलाह के दर्द निवारक गोलियां (पेनकिलर) न खाएं।"
        }
    },
    "te": {
        "HbA1c (Glycated Hemoglobin)": {
            "plain_meaning": "HbA1c అనేది గత 3 నెలల సగటు రక్తంలో చక్కెర స్థాయిని కొలిచే పరీక్ష.",
            "why_it_matters": "మీ ఫలితం 8.8% సాధారణ పరిమితి కంటే ఎక్కువ. ఇది గుండె మరియు మూత్రపిండాలపై ఒత్తిడిని పెంచుతుంది.",
            "lifestyle_tip": "తీపి పదార్థాలు తగ్గించండి. తృణధాన్యాలు, ఆకుకూరలు మరియు పప్పుదినుసులు ఎక్కువగా తీసుకోండి."
        },
        "Serum Creatinine": {
            "plain_meaning": "క్రియేటినిన్ అనేది మూత్రపిండాల పనితీరును సూచించే వ్యర్థ పదార్థం.",
            "why_it_matters": "1.35 mg/dL కొద్దిగా ఎక్కువగా ఉంది, అంటే మూత్రపిండాలపై శ్రద్ధ అవసరం.",
            "lifestyle_tip": "రోజూ తగినంత మంచినీరు త్రాగండి. డాక్టర్ సలహా లేకుండా పెయిన్ కిల్లర్ మందులు వాడవద్దు."
        }
    },
    "ta": {
        "HbA1c (Glycated Hemoglobin)": {
            "plain_meaning": "HbA1c என்பது கடந்த 3 மாதங்களில் உங்கள் இரத்த சர்க்கரையின் சராசரி அளவாகும்.",
            "why_it_matters": "உங்கள் அளவு 8.8% அதிகமாக உள்ளது. இது இதயம் மற்றும் சிறுநீரகங்களுக்கு கூடுதல் அழுத்தத்தை ஏற்படுத்துகிறது.",
            "lifestyle_tip": "இனிப்பு மற்றும் வறுத்த உணவுகளை தவிர்க்கவும். காய்கறிகள் மற்றும் கீரைகளை உணவில் சேர்க்கவும்."
        }
    }
}


class TranslationEngine:
    """Translates UI labels, clinical summaries, and chat responses"""

    @classmethod
    def get_ui_strings(cls, lang: str = "en") -> Dict[str, str]:
        return UI_LOCALES.get(lang, UI_LOCALES["en"])

    @classmethod
    def translate_summary(cls, summary_obj: Dict[str, Any], lang: str = "en") -> Dict[str, Any]:
        """Injects regional language translations into clinical summary object"""
        if lang == "en" or lang not in REGIONAL_TRANSLATIONS:
            return summary_obj

        regional_dict = REGIONAL_TRANSLATIONS[lang]
        updated = dict(summary_obj)

        if lang == "hi":
            updated["overall_narrative_regional"] = (
                f"नमस्ते {summary_obj.get('patient_name', '').split()[0]} जी। आपके हालिया मेडिकल रिकॉर्ड का विश्लेषण पूरा हो गया है। "
                f"आपके रक्त परीक्षण में ब्लड शुगर (HbA1c 8.8%), कोलेस्ट्रॉल और सीरम क्रिएटिनिन सामान्य सीमा से अधिक पाए गए हैं। "
                f"यह दर्शाता है कि आपकी दिनचर्या, खान-पान और दवाइयों के नियमित सेवन पर विशेष ध्यान देने की आवश्यकता है। "
                f"डॉक्टर द्वारा सुझाई गई दवाइयों का समय पर सेवन करें और 45 दिन बाद पुनः जांच करवाएं।"
            )
        elif lang == "te":
            updated["overall_narrative_regional"] = (
                f"నమస్కారం {summary_obj.get('patient_name', '').split()[0]} గారు. మీ మెడికల్ రికార్డుల విశ్లేషణ పూర్తయింది. "
                f"బ్లడ్ షుగర్ (HbA1c 8.8%), కొలెస్ట్రాల్ మరియు క్రియేటినిన్ సాధారణ స్థాయి కంటే ఎక్కువగా ఉన్నాయి. "
                f"సమయానికి మందులు వేసుకోవడం మరియు ఆహారపు అలవాట్లను మార్చుకోవడం చాలా ముఖ్యం."
            )
        elif lang == "ta":
            updated["overall_narrative_regional"] = (
                f"வணக்கம் {summary_obj.get('patient_name', '').split()[0]}. உங்கள் மருத்துவ அறிக்கையின் பகுப்பாய்வு முடிந்தது. "
                f"இரத்த சர்க்கரை (HbA1c 8.8%), கொலஸ்ட்ரால் மற்றும் கிரியேட்டினின் அளவு சற்று அதிகமாக உள்ளது. "
                f"மருத்துவர் பரிந்துரைத்த மருந்துகளை தவறாமல் எடுத்துக்கொள்ளுங்கள்."
            )

        # Update individual abnormal test cards
        for card in updated.get("abnormal_explanations", []):
            test_name = card.get("test_name", "")
            if test_name in regional_dict:
                card["plain_meaning_regional"] = regional_dict[test_name].get("plain_meaning", card["plain_meaning"])
                card["why_it_matters_regional"] = regional_dict[test_name].get("why_it_matters", card["why_it_matters"])
                card["lifestyle_tip_regional"] = regional_dict[test_name].get("lifestyle_tip", card["lifestyle_tip"])

        return updated
