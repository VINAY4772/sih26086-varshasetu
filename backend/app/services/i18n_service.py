from typing import Dict, Any
from ..models.schemas import FullAdvisoryResponse, CropAdvisory

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "hi": {
        "Monsoon Onset Officially Declared": "मानसून आगमन की आधिकारिक घोषणा",
        "Onset Imminent (Expected in 48-72 Hours)": "मानसून आगमन की संभावना (48-72 घंटों में)",
        "Pre-Monsoon Season (Preparatory Stage)": "प्री-मानसून चरण (खेत तैयारी का समय)",
        "optimal": "उत्तम (बुवाई हेतु आदर्श)",
        "favorable": "अनुकूल (शीघ्र तैयारी करें)",
        "wait_for_moisture": "नमी की प्रतीक्षा करें (सूखी बुवाई न करें)",
        "high_risk_dry": "अत्यधिक सूखा जोखिम (बुवाई स्थगित करें)",
        "Postpone New Sowing until Break Spell Concludes": "मानसून ब्रेक समाप्त होने तक नई बुवाई स्थगित रखें",
        "Paddy / Rice (धान / वరి)": "धान (चावल)",
        "Cotton (कपास / పత్తి)": "कपास (कॉटन)",
        "Soybean (सोयाबीन / సోయాబీన్)": "सोयाबीन",
        "Groundnut (मूंगफली / వేరుశనగ)": "मूंगफली",
        "Maize / Corn (मक्का / మొక్కజొన్న)": "मक्का",
        "Redgram / Pigeonpea (अरहर / కంది)": "अरहर (तूर)",
        "STRICTLY SUSPEND urea top dressing; spray 1.5% KNO3 (potassium nitrate) to boost drought resilience.": "यूरिया का छिड़काव तुरंत रोकें; सूखे से बचाव के लिए 1.5% पोटेशियम नाइट्रेट (KNO3) का छिड़काव करें।",
        "Provide life-saving light irrigation in evening hours; utilize farm pond / micro-drip.": "शाम के समय जीवन रक्षक हल्की सिंचाई करें; खेत के तालाब या ड्रिप का उपयोग करें।",
        "No supplementary irrigation required; clear field drainage to prevent seedling damping-off.": "अतिरिक्त सिंचाई की आवश्यकता नहीं है; जलभराव रोकने के लिए जल निकासी की नालियां साफ रखें।",
        "Apply recommended basal dose of SSP (Phosphorus) and Potash (MOP) at 5 cm below seed depth.": "बीज की गहराई से 5 सेमी नीचे अनुशंसित बेसल एसएसपी (फॉस्फोरस) और पोटाश डालें।"
    },
    "te": {
        "Monsoon Onset Officially Declared": "నైరుతి రుతుపవనాల రాక అధికారికంగా ప్రకటించబడింది",
        "Onset Imminent (Expected in 48-72 Hours)": "రుతుపవనాల రాక ఆసన్నమైంది (48-72 గంటల్లో)",
        "Pre-Monsoon Season (Preparatory Stage)": "ముందస్తు వర్షాకాల సన్నాహక దశ (నేల తయారీ)",
        "optimal": "అనుకూలం (విత్తడానికి అత్యంత అనుకూలం)",
        "favorable": "అనుకూలం (సిద్ధంగా ఉండండి)",
        "wait_for_moisture": "నేలలో తగినంత తేమ వచ్చే వరకు వేచి చూడండి",
        "high_risk_dry": "తీవ్ర బెట్ట ముప్పు (విత్తడం వాయిదా వేయండి)",
        "Postpone New Sowing until Break Spell Concludes": "వర్షాభావ / బెట్ట కాలం ముగిసే వరకు కొత్త విత్తనాలు వేయకండి",
        "Paddy / Rice (धान / వరి)": "వరి",
        "Cotton (कपास / పత్తి)": "పత్తి",
        "Soybean (सोयाबीन / సోయాబీన్)": "సోయాబీన్",
        "Groundnut (मूंगफली / వేరుశనగ)": "వేరుశనగ",
        "Maize / Corn (मक्का / మొక్కజొన్న)": "మొక్కజొన్న",
        "Redgram / Pigeonpea (अरहर / కంది)": "కంది",
        "STRICTLY SUSPEND urea top dressing; spray 1.5% KNO3 (potassium nitrate) to boost drought resilience.": "యూరియా పైపాటు వేయడం వెంటనే నిలిపివేయండి; బెట్టను తట్టుకోవడానికి 1.5% పొటాషియం నైట్రేట్ (13-0-45) పిచికారీ చేయండి.",
        "Provide life-saving light irrigation in evening hours; utilize farm pond / micro-drip.": "సాయంత్రం వేళల్లో తుంపర లేదా బిందు సేద్యం ద్వారా జీవనాధార తడి ఇవ్వండి.",
        "No supplementary irrigation required; clear field drainage to prevent seedling damping-off.": "అదనపు నీరు అవసరం లేదు; నారు కుళ్ళు నివారణకు మురుగునీటి కాల్వలను సరిచేయండి.",
        "Apply recommended basal dose of SSP (Phosphorus) and Potash (MOP) at 5 cm below seed depth.": "సిఫార్సు చేసిన భాస్వరం మరియు పొటాష్ ఎరువులను విత్తనానికి 5 సెం.మీ దిగువన చేర్చండి."
    },
    "mr": {
        "Monsoon Onset Officially Declared": "मान्सून आगमनाची अधिकृत घोषणा",
        "Onset Imminent (Expected in 48-72 Hours)": "मान्सून लवकरच दाखल होण्याची शक्यता (४८-७२ तासांत)",
        "Pre-Monsoon Season (Preparatory Stage)": "पूर्व-मान्सून मशागतीचा टप्पा",
        "optimal": "उत्कृष्ट (पेरणीसाठी अत्यंत योग्य)",
        "favorable": "अनुकूल",
        "wait_for_moisture": "जमिनीत पुरेशी ओल येईपर्यंत थांबा",
        "high_risk_dry": "खंड / दुष्काळ धोका (पेरणी पुढे ढकला)",
        "Postpone New Sowing until Break Spell Concludes": "मान्सूनचा खंड संपेपर्यंत नवीन पेरणी पुढे ढकला",
        "Paddy / Rice (धान / వరి)": "भात (तांदूळ)",
        "Cotton (कपास / పత్తి)": "कापूस",
        "Soybean (सोयाबीन / సోయాబీన్)": "सोयाबीन",
        "Groundnut (मूंगफली / వేరుశనగ)": "भुईमूग",
        "Maize / Corn (मक्का / మొక్కజొన్న)": "मका",
        "Redgram / Pigeonpea (अरहर / కంది)": "तूर",
        "STRICTLY SUSPEND urea top dressing; spray 1.5% KNO3 (potassium nitrate) to boost drought resilience.": "युरियाचा वरखत डोस त्वरित थांबवा; कोरडवाहू ताण कमी करण्यासाठी १.५% पोटॅशियम नायट्रेट फवारा.",
        "Provide life-saving light irrigation in evening hours; utilize farm pond / micro-drip.": "संध्याकाळी शेततळे किंवा ठिबक सिंचनाद्वारे पिकाला संरक्षित पाणी द्या.",
        "No supplementary irrigation required; clear field drainage to prevent seedling damping-off.": "जादा पाण्याची गरज नाही; शेतातील पाण्याचा निचरा होण्यासाठी चर मोकळे करा."
    }
}

class InternationalizationService:
    def localize_advisory(self, advisory: FullAdvisoryResponse, target_lang: str) -> FullAdvisoryResponse:
        if target_lang not in TRANSLATIONS:
            return advisory  # Default English

        lang_dict = TRANSLATIONS[target_lang]

        # Translate headline if matching phrases exist
        new_headline = advisory.monsoon_headline
        for en_key, trans_val in lang_dict.items():
            if en_key in new_headline:
                new_headline = new_headline.replace(en_key, trans_val)

        # Localize crops
        localized_crops = []
        for c in advisory.crop_advisories:
            c_dict = c.model_dump()
            c_dict["crop_name"] = lang_dict.get(c.crop_name, c.crop_name)
            c_dict["irrigation_advice"] = lang_dict.get(c.irrigation_advice, c.irrigation_advice)
            c_dict["fertilizer_advice"] = lang_dict.get(c.fertilizer_advice, c.fertilizer_advice)
            localized_crops.append(CropAdvisory(**c_dict))

        return FullAdvisoryResponse(
            location=advisory.location,
            language=target_lang,
            generated_at=advisory.generated_at,
            monsoon_headline=new_headline,
            overall_advice=advisory.overall_advice,
            crop_advisories=localized_crops,
            alert_level=advisory.alert_level
        )

i18n_service = InternationalizationService()
