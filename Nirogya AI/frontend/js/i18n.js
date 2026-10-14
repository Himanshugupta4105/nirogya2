/**
 * Nirogya AI - Multi-Language Regional Translation Controller
 * Supports: English (EN), Hindi (HI), Telugu (TE), Tamil (TA), Bengali (BN), Marathi (MR)
 */

const LOCALES = {
  en: {
    app_title: "Nirogya AI",
    app_tagline: "Personal Health Copilot",
    upload_headline: "Smart Medical Record Ingestion & Vision OCR",
    upload_sub: "Ingest prescriptions, lab reports, or discharge summaries (PDF, PNG, JPG, TXT)",
    dropzone_prompt: "Drag & drop clinical document, or click to browse",
    dropzone_sub: "AI extracts medicines, dosages, test values, and flags abnormal biomarkers",
    presets_label: "Or instant test with verified clinical presets:",
    tab_overview: "AI Health Summary",
    tab_timeline: "Unified Timeline",
    tab_vitals: "Vitals & Biomarkers",
    tab_medications: "Active Medications",
    tab_fhir: "ABDM & FHIR R4",
    tab_architecture: "System Architecture",
    executive_title: "Executive Health Understanding",
    abnormal_section_title: "Abnormal Biomarkers & Plain-Language Explanations",
    checklist_title: "Actionable Daily Routine",
    copilot_title: "AI Health Copilot",
    copilot_placeholder: "Ask about your tests, medications, or health...",
    copilot_send: "Ask",
    btn_view_raw: "View Raw OCR",
    btn_download_fhir: "Download FHIR Bundle",
    badge_action: "Action Required",
    badge_optimal: "Optimal Range",
    abha_linked_status: "ABHA Linked (14-8921-4350-9812)",
    disclaimer_strip: "MEDICAL DISCLAIMER: Nirogya AI provides educational guidance and plain-language summaries. Seek emergency care immediately if experiencing chest pain, acute dyspnea, or severe hypoglycemia."
  },
  hi: {
    app_title: "निरोग्य AI (Nirogya AI)",
    app_tagline: "व्यक्तिगत स्वास्थ्य सहायक",
    upload_headline: "स्मार्ट मेडिकल रिकॉर्ड विश्लेषण व विज़न OCR",
    upload_sub: "डॉक्टर का पर्चा, लैब रिपोर्ट या डिस्चार्ज समरी यहाँ डालें (PDF, PNG, JPG)",
    dropzone_prompt: "दस्तावेज़ यहाँ खींचकर लाएँ या फ़ाइल चुनें",
    dropzone_sub: "दवाइयां, खुराक, टेस्ट परिणाम और असामान्य मान अपने आप पहचाने जाएंगे",
    presets_label: "या पहले से लोड किए गए क्लिनिकल सैंपल देखें:",
    tab_overview: "स्वास्थ्य सारांश (Summary)",
    tab_timeline: "टाइमलाइन (Timeline)",
    tab_vitals: "वाइटल्स व रुझान (Trends)",
    tab_medications: "चल रही दवाइयाँ (Medicines)",
    tab_fhir: "ABDM व FHIR R4",
    tab_architecture: "सिस्टम आर्किटेक्चर",
    executive_title: "स्वास्थ्य सारांश (आसान भाषा में)",
    abnormal_section_title: "असामान्य जाँच परिणाम व उनका अर्थ",
    checklist_title: "दैनिक जीवनशैली व जरूरी कदम",
    copilot_title: "AI स्वास्थ्य को-पायलट",
    copilot_placeholder: "अपनी रिपोर्ट, दवाओं या सेहत के बारे में पूछें...",
    copilot_send: "पूछें",
    btn_view_raw: "ओसीआर टेक्स्ट देखें",
    btn_download_fhir: "FHIR बंडल डाउनलोड करें",
    badge_action: "ध्यान देने योग्य",
    badge_optimal: "सामान्य सीमा",
    abha_linked_status: "ABHA लिंक है (14-8921-4350-9812)",
    disclaimer_strip: "चिकित्सा अस्वीकरण: निरोग्य AI केवल शैक्षिक मार्गदर्शन प्रदान करता है। सीने में दर्द या सांस फूलने जैसी आपातकालीन स्थिति में तुरंत डॉक्टर से संपर्क करें।"
  },
  te: {
    app_title: "నిరోగ్య AI",
    app_tagline: "వ్యక్తిగత ఆరోగ్య సహచరుడు",
    upload_headline: "మెడికల్ రికార్డుల విశ్లేషణ & విజన్ OCR",
    upload_sub: "ప్రిస్క్రిప్షన్లు, ల్యాబ్ రిపోర్టులు లేదా డిశ్చార్జ్ సారాంశాన్ని అప్‌లోడ్ చేయండి",
    dropzone_prompt: "పత్రాన్ని ఇక్కడ వేయండి లేదా ఎంచుకోండి",
    dropzone_sub: "మందులు, మోతాదులు మరియు ల్యాబ్ ఫలితాల ఆటోమేటిక్ వెలికితీత",
    presets_label: "లేదా క్లినికల్ శాంపిల్స్ ఎంచుకోండి:",
    tab_overview: "ఆరోగ్య సారాంశం",
    tab_timeline: "టైమ్‌లైన్",
    tab_vitals: "వైటల్స్ ట్రెండ్స్",
    tab_medications: "మందుల వివరాలు",
    tab_fhir: "ABDM & FHIR R4",
    tab_architecture: "ఆర్కిటెక్చర్",
    executive_title: "సమగ్ర ఆరోగ్య విశ్లేషణ",
    abnormal_section_title: "శ్రద్ధ అవసరమైన పరీక్షల వివరాలు",
    checklist_title: "రోజువారీ జీవనశైలి సూచనలు",
    copilot_title: "AI హెల్త్ కోపైలట్",
    copilot_placeholder: "రిపోర్టులు లేదా మందుల గురించి అడగండి...",
    copilot_send: "అడగండి",
    btn_view_raw: "OCR టెక్స్ట్ చూడండి",
    btn_download_fhir: "FHIR డౌన్‌లోడ్",
    badge_action: "శ్రద్ధ అవసరం",
    badge_optimal: "సాధారణ పరిధి",
    abha_linked_status: "ABHA లింక్ చేయబడింది",
    disclaimer_strip: "వైద్య హెచ్చరిక: ఇది అవగాహన కోసం మాత్రమే. అత్యవసర పరిస్థితుల్లో వెంటనే వైద్యుడిని సంప్రదించండి."
  },
  ta: {
    app_title: "நிரோக்யா AI",
    app_tagline: "தனிப்பட்ட சுகாதார வழிகாட்டி",
    upload_headline: "மருத்துவ ஆவண பகுப்பாய்வு & OCR",
    upload_sub: "மருந்துச் சீட்டு, ஆய்வக அறிக்கை அல்லது டிஸ்சார்ஜ் சுருக்கத்தை பதிவேற்றவும்",
    dropzone_prompt: "கோப்பை இங்கே இழுத்துப் போடவும்",
    dropzone_sub: "மருந்துகள், அளவுகள் மற்றும் சோதனை முடிவுகள் பிரித்தெடுக்கப்படும்",
    presets_label: "அல்லது மாதிரி அறிக்கைகளை பார்க்கவும்:",
    tab_overview: "சுகாதார சுருக்கம்",
    tab_timeline: "காலவரிசை",
    tab_vitals: "உடல்நிலை போக்குகள்",
    tab_medications: "நடப்பு மருந்துகள்",
    tab_fhir: "ABDM & FHIR R4",
    tab_architecture: "கட்டமைப்பு",
    executive_title: "முழுமையான சுகாதார சுருக்கம்",
    abnormal_section_title: "கவனம் தேவைப்படும் பரிசோதனை முடிவுகள்",
    checklist_title: "தினசரி வாழ்க்கை முறை குறிப்புகள்",
    copilot_title: "AI மருத்துவ வழிகாட்டி",
    copilot_placeholder: "உங்கள் அறிக்கைகள் பற்றி கேட்கவும்...",
    copilot_send: "கேளுங்கள்",
    btn_view_raw: "OCR உரை காண்க",
    btn_download_fhir: "FHIR பதிவிறக்கம்",
    badge_action: "கவனம் தேவை",
    badge_optimal: "சாதாரண அளவு",
    abha_linked_status: "ABHA இணைக்கப்பட்டது",
    disclaimer_strip: "மருத்துவ எச்சரிக்கை: தகவல் நோக்கங்களுக்கு மட்டுமே. அவசர காலங்களில் உடனடியாக மருத்துவரை அணுகவும்."
  },
  bn: {
    app_title: "নিরোগ্য AI",
    app_tagline: "ব্যক্তিগত স্বাস্থ্য সহযোগী",
    upload_headline: "মেডিকেল রেকর্ড বিশ্লেষণ ও ভিশন OCR",
    upload_sub: "প্রেসক্রিপশন, ল্যাব রিপোর্ট বা ডিসচার্জ সামারি আপলোড করুন",
    dropzone_prompt: "ডকুমেন্ট এখানে ড্রপ করুন বা ব্রাউজ করুন",
    dropzone_sub: "ওষুধের নাম, ডোজ ও টেস্ট রেজাল্ট নির্ভুল নিষ্কাশন",
    presets_label: "অথবা নমুনা রিপোর্ট দেখুন:",
    tab_overview: "স্বাস্থ্য সারাংশ",
    tab_timeline: "টাইমলাইন",
    tab_vitals: "ভাইটালস ট্রেন্ড",
    tab_medications: "চলতি ওষুধ",
    tab_fhir: "ABDM ও FHIR R4",
    tab_architecture: "সিস্টেম আর্কিটেকচার",
    executive_title: "সহজ ভাষায় স্বাস্থ্য পর্যালোচনা",
    abnormal_section_title: "অস্বাভাবিক টেস্ট ও সহজ ব্যাখ্যা",
    checklist_title: "দৈনন্দিন করণীয় রুটিন",
    copilot_title: "AI হেলথ কো-পাইলট",
    copilot_placeholder: "আপনার রিপোর্ট বা ওষুধ সম্পর্কে জিজ্ঞাসা করুন...",
    copilot_send: "পাঠান",
    btn_view_raw: "OCR টেক্সট দেখুন",
    btn_download_fhir: "FHIR ডাউনলোড",
    badge_action: "নজর প্রয়োজন",
    badge_optimal: "স্বাভাবিক",
    abha_linked_status: "ABHA সংযুক্ত",
    disclaimer_strip: "সতর্কতা: এটি শুধুমাত্র তথ্যের উদ্দেশ্যে। জরুরি প্রয়োজনে সরাসরি চিকিৎসকের পরামর্শ নিন।"
  },
  mr: {
    app_title: "निरोग्य AI",
    app_tagline: "वैयक्तिक आरोग्य सहाय्यक",
    upload_headline: "वैद्यकीय अहवाल विश्लेषण व OCR",
    upload_sub: "प्रिस्क्रिप्शन, लॅब रिपोर्ट किंवा डिस्चार्ज सारांश अपलोड करा",
    dropzone_prompt: "कागदपत्र इथे ड्रॅग करा किंवा निवडा",
    dropzone_sub: "औषधे, डोस आणि चाचणीचे निष्कर्ष स्वयंचलित विश्लेषित होतात",
    presets_label: "किंवा नमुना अहवाल निवडा:",
    tab_overview: "आरोग्य सारांश",
    tab_timeline: "टाइमलाइन",
    tab_vitals: "व्हाइटल्स ट्रेंड्स",
    tab_medications: "सध्याची औषधे",
    tab_fhir: "ABDM आणि FHIR R4",
    tab_architecture: "सिस्टम रचना",
    executive_title: "आरोग्य सारांश (सोप्या भाषेत)",
    abnormal_section_title: "असामान्य चाचणी निष्कर्ष व अर्थ",
    checklist_title: "दैनंदिन जीवनशैली मार्गदर्शक",
    copilot_title: "AI आरोग्य मार्गदर्शक",
    copilot_placeholder: "आपल्या अहवाल किंवा औषधांविषयी विचारा...",
    copilot_send: "विचारा",
    btn_view_raw: "OCR मजकूर पहा",
    btn_download_fhir: "FHIR डाउनलोड",
    badge_action: "लक्ष देणे गरजेचे",
    badge_optimal: "सामान्य मर्यादा",
    abha_linked_status: "ABHA जोडलेले",
    disclaimer_strip: "वैद्यकीय अस्वीकरण: हे केवळ माहितीसाठी आहे. आपत्कालीन परिस्थितीत तात्काळ डॉक्टरांशी संपर्क साधा."
  }
};

class I18nManager {
  static currentLanguage = "en";

  static setLanguage(lang) {
    if (LOCALES[lang]) {
      this.currentLanguage = lang;
      this.applyTranslations();
      return true;
    }
    return false;
  }

  static get(key) {
    const dict = LOCALES[this.currentLanguage] || LOCALES.en;
    return dict[key] || LOCALES.en[key] || key;
  }

  static applyTranslations() {
    const dict = LOCALES[this.currentLanguage] || LOCALES.en;

    document.querySelectorAll("[data-i18n]").forEach(el => {
      const key = el.getAttribute("data-i18n");
      if (dict[key]) {
        if (el.tagName === "INPUT" || el.tagName === "TEXTAREA") {
          el.placeholder = dict[key];
        } else {
          el.textContent = dict[key];
        }
      }
    });
  }
}
