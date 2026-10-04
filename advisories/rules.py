"""
Agricultural Advisory Rules Engine: SIH26086
Translates multi-scale meteorological forecasts into actionable, crop-specific guidance
with transparent reasoning, rule triggers, validity periods, and limitations.
"""

from typing import Dict, Any, List, Optional
import datetime
from advisories.crop_profiles import CROP_PROFILES

class AdvisoryRuleEngine:
    def generate_crop_advisory(
        self,
        crop_code: str,
        forecast_data: Dict[str, Any],
        growth_stage: Optional[str] = None,
        language: str = "en"
    ) -> Dict[str, Any]:
        profile = CROP_PROFILES.get(crop_code)
        if not profile:
            raise ValueError(f"Unknown crop_code: '{crop_code}'")

        break_outlook = forecast_data.get("break_spell_outlook", {})
        onset_outlook = forecast_data.get("onset_outlook", {})
        heavy_rain = forecast_data.get("heavy_rainfall_risk", {})
        timeline = forecast_data.get("timeline", [])
        location = forecast_data.get("location", {})

        is_break_critical = break_outlook.get("risk_level") in ["HIGH", "CRITICAL"]
        is_break_prob_high = break_outlook.get("probability", 0.0) >= 0.50
        is_onset_declared = onset_outlook.get("status") == "ONSET_DECLARED"
        is_false_alarm = onset_outlook.get("is_false_alarm", False)
        heavy_risk = heavy_rain.get("heavy_rainfall_risk", "GREEN_NO_HEAVY_RAIN")

        cur_soil_moist = timeline[0].get("soil_moisture_pct", 50.0) if timeline else 50.0
        today = datetime.date.today()
        validity = f"{today.strftime('%d %b %Y')} to {(today + datetime.timedelta(days=7)).strftime('%d %b %Y')}"

        # 1. Determine Sowing Status
        if is_false_alarm:
            sowing_status = "HIGH_RISK_FALSE_ALARM"
            sowing_window = "Postpone dry sowing (Pre-monsoon shower only)"
            reasoning = (
                f"Isolated rainfall detected without deep tropospheric westerly shear. "
                f"Dry sowing now will lead to seed scorched failure upon imminent dry spell."
            )
            rule_applied = "Rule AGR-01: False Onset Protection (Pai et al. 2014 & CRIDA)"
            priority_action_en = "Do NOT sow in dry dust. Await sustained monsoonal wetting."
            priority_action_te = "పొడి దుక్కిలో విత్తనాలు వేయకండి. నైరుతి రుతుపవనాలు స్థిరపడే వరకు ఆగండి."
        elif is_break_critical or is_break_prob_high:
            sowing_status = "POSTPONE_BREAK_SPELL"
            sowing_window = f"Suspend sowing until break spell concludes ({break_outlook.get('projected_consecutive_dry_days', 5)} dry days projected)"
            reasoning = (
                f"Severe convective lull projected across {location.get('block_or_mandal', 'block')} with high evapotranspiration stress. "
                f"Emerging seedlings will suffer irreversible wilting."
            )
            rule_applied = "Rule AGR-02: Break Spell Sowing Suppression (Rajeevan et al. 2010)"
            priority_action_en = "Postpone sowing. Apply crop residue mulch across existing stands."
            priority_action_te = "విత్తడం వాయిదా వేయండి. ఇప్పటికే వేసిన పంటలపై ఎండుగడ్డితో ఆచ్ఛాదన (మల్చింగ్) చేయండి."
        elif is_onset_declared and cur_soil_moist >= profile["optimal_soil_moisture_pct"] * 0.8:
            sowing_status = "OPTIMAL_SOWING"
            sowing_window = f"{today.strftime('%d %b')} – {(today + datetime.timedelta(days=6)).strftime('%d %b')}"
            reasoning = (
                f"Monsoon onset validated. Cumulative rainfall and root-zone soil moisture ({cur_soil_moist:.1f}%) "
                f"have reached optimal seed germination threshold for {profile['name_en']}."
            )
            rule_applied = "Rule AGR-03: Optimum Moisture Window Verification (ICAR Guidelines)"
            priority_action_en = f"Commence sowing with certified treated seeds. Maintain recommended line spacing."
            priority_action_te = f"సిఫార్సు చేసిన విత్తన శుద్ధి పూర్తి చేసుకుని, వరుసల పద్ధతిలో విత్తుకోండి."
        else:
            sowing_status = "AWAIT_MOISTURE"
            sowing_window = f"Awaiting soil profile saturation (Target: {profile['optimal_soil_moisture_pct']}%)"
            reasoning = f"Current soil moisture ({cur_soil_moist:.1f}%) is below optimal threshold. Wait for next widespread rain spell."
            rule_applied = "Rule AGR-04: Sub-optimal Soil Moisture Watch"
            priority_action_en = "Complete summer tillage and seed procurement; prepare bunds."
            priority_action_te = "వేసవి దుక్కులు, విత్తనాల సేకరణ పూర్తి చేసి గట్లను పటిష్టం చేసుకోండి."

        # 2. Irrigation Advice
        if "EXTREME" in heavy_risk or "VERY_HEAVY" in heavy_risk:
            irrigation_en = "STOP ALL IRRIGATION. Open field drainage channels immediately to prevent root asphyxiation."
            irrigation_te = "ఎలాంటి నీటిపారుదల చేయకండి. పొలంలో నీరు నిల్వ ఉండకుండా మురుగు కాల్వలను తెరిచి ఉంచండి."
        elif is_break_critical:
            irrigation_en = "Provide life-saving protective irrigation during evening hours using micro-sprinklers or drip systems."
            irrigation_te = "సాయంత్రం వేళల్లో తుంపర లేదా బిందు సేద్యం ద్వారా జీవనాధార రక్షక తడి ఇవ్వండి."
        else:
            irrigation_en = "Normal rainfed soil moisture adequate. No supplemental irrigation needed."
            irrigation_te = "నేలలో తగినంత తేమ ఉన్నందున అదనపు నీరు అవసరం లేదు."

        # 3. Fertilizer Advice
        if is_break_critical:
            fertilizer_en = "STRICTLY SUSPEND urea top-dressing to prevent leaf scorch. Spray 1.5% KNO3 (13-0-45) to alleviate moisture stress."
            fertilizer_te = "యూరియా పైపాటు వేయడం వెంటనే ఆపండి. బెట్టను తట్టుకోవడానికి 1.5% పొటాషియం నైట్రేట్ పిచికారీ చేయండి."
        elif is_onset_declared:
            fertilizer_en = "Apply full basal dose of Single Super Phosphate (Phosphorus) and MOP (Potash) placed 5 cm below seed depth."
            fertilizer_te = "విత్తనం నాటే సమయంలో సిఫార్సు చేసిన భాస్వరం మరియు పొటాష్ ఎరువులను విత్తనానికి 5 సెం.మీ దిగువన వేయండి."
        else:
            fertilizer_en = "Incorporate well-decomposed Farm Yard Manure (FYM) @ 8-10 t/ha during seedbed preparation."
            fertilizer_te = "దుక్కి తయారీ సమయంలో ఎకరాకు 4-5 టన్నుల పశువుల ఎరువును కలియదున్నండి."

        # 4. Pest & Disease Alert
        if is_break_critical:
            pest_en = "Scout for sucking pests (thrips, aphids, whiteflies, red spider mites) proliferating in hot dry weather."
            pest_te = "పొడి వాతావరణంలో ఎక్కువగా వచ్చే రసం పీల్చే పురుగుల (తామర పురుగులు, పేనుబంక) ఉధృతిని గమనించండి."
        elif "HEAVY" in heavy_risk:
            pest_en = "High humidity risk: Monitor for collar rot, damping off, and bacterial leaf blight."
            pest_te = "అధిక తేమ వల్ల వచ్చే కాండం కుళ్ళు, మొలక కుళ్ళు తెగుళ్ళ పట్ల అప్రమత్తంగా ఉండండి."
        else:
            pest_en = "Treat seeds with Trichoderma viride (10g/kg) or Imidacloprid (5ml/kg) before sowing."
            pest_te = "విత్తే ముందు ట్రైకోడెర్మా విరిడే (10 గ్రా/కేజీ) లేదా ఇమిడాక్లోప్రిడ్ తో విత్తన శుద్ధి చేయండి."

        # Multilingual Advisory Mappings for all 7 Supported Languages
        ADVISORY_TEXTS = {
            "action_false_alarm": {
                "en": "Do NOT sow in dry dust. Await sustained monsoonal wetting.",
                "te": "పొడి దుక్కిలో విత్తనాలు వేయకండి. నైరుతి రుతుపవనాలు స్థిరపడే వరకు ఆగండి.",
                "hi": "सूखी मिट्टी में बुवाई न करें। नियमित मानसूनी वर्षा की प्रतीक्षा करें।",
                "ta": "வறண்ட புழுதியில் விதைக்க வேண்டாம். தென்மேற்கு பருவமழை நிலைபெறும் வரை காத்திருங்கள்.",
                "kn": "ಒಣ ಮಣ್ಣಿನಲ್ಲಿ ಬಿತ್ತನೆ ಮಾಡಬೇಡಿ. ಮುಂಗಾರು ಮಳೆ ಸ್ಥಿರಗೊಳ್ಳುವವರೆಗೆ ಕಾಯಿರಿ.",
                "ur": "خشک مٹی میں بوائی نہ کریں۔ باقاعدہ مانسونی بارشوں کا انتظار کریں۔",
                "ml": "വരണ്ട മണ്ണിൽ വിതയ്ക്കരുത്. കാലവർഷം ശക്തമാകുന്നതുവരെ കാത്തിരിക്കുക."
            },
            "action_break_spell": {
                "en": "Postpone sowing. Apply crop residue mulch across existing stands.",
                "te": "విత్తడం వాయిదా వేయండి. ఇప్పటికే వేసిన పంటలపై ఎండుగడ్డితో ఆచ్ఛాదన (మల్చింగ్) చేయండి.",
                "hi": "बुवाई स्थगित करें। खड़ी फसलों पर फसल अवशेष की मल्चिंग करें।",
                "ta": "விதையெடுப்பை ஒத்திவையுங்கள். நின்ற பயிர்களுக்கு பயிர் கழிவு மூடாக்கு இடவும்.",
                "kn": "ಬಿತ್ತನೆ ಮುಂದೂಡಿ. ಈಗಾಗಲೇ ಇರುವ ಬೆಳೆಗಳಿಗೆ ಕೃಷಿ ತ್ಯಾಜ್ಯದಿಂದ ಹೊದಿಕೆ (ಮಲ್ಚಿಂಗ್) ಮಾಡಿ.",
                "ur": "بوائی مؤخر کریں۔ کھڑی فصلوں پر باقیات کی ملچنگ کریں۔",
                "ml": "വിത മാറ്റിവെയ്ക്കുക. നിലവിലുള്ള വിളകൾക്ക് പുതയിടൽ (മൾച്ചിംഗ്) നൽകുക."
            },
            "action_optimal": {
                "en": "Commence sowing with certified treated seeds. Maintain recommended line spacing.",
                "te": "సిఫార్సు చేసిన విత్తన శుద్ధి పూర్తి చేసుకుని, వరుసల పద్ధతిలో విత్తుకోండి.",
                "hi": "प्रमाणित एवं उपचारित बीजों से बुवाई शुरू करें। उचित कतार दूरी बनाए रखें।",
                "ta": "சான்றளிக்கப்பட்ட விதை நேர்த்தி செய்யப்பட்ட விதைகளுடன் விதைப்பைத் தொடங்குங்கள். பரிந்துரைக்கப்பட்ட இடைவெளியைப் பராமரிக்கவும்.",
                "kn": "ಪ್ರಮಾಣೀಕೃತ ಬೀಜೋಪಚಾರ ಮಾಡಿದ ಬೀಜಗಳಿಂದ ಬಿತ್ತನೆ ಆರಂಭಿಸಿ. ಶಿಫಾರಸು ಮಾಡಿದ ಸಾಲಿನ ಅಂತರ ಕಾಪಾಡಿ.",
                "ur": "تصدیق شدہ اور زہر آلود بیجوں سے بوائی شروع کریں۔ قطاروں کا مناسب فاصلہ رکھیں۔",
                "ml": "സാക്ഷ്യപ്പെടുത്തിയ വിത്ത് സംസ്കരണം നടത്തി വിത ആരംഭിക്കുക. ശുപാർശ ചെയ്ത അകലം പാലിക്കുക."
            },
            "action_await_moisture": {
                "en": "Complete summer tillage and seed procurement; prepare bunds.",
                "te": "వేసవి దుక్కులు, విత్తనాల సేకరణ పూర్తి చేసి గట్లను పటిష్టం చేసుకోండి.",
                "hi": "ग्रीष्मकालीन जुताई और बीज खरीद पूरी करें; मेड़बंदी मजबूत करें।",
                "ta": "கோடைக்கால உழவு மற்றும் விதை கொள்முதலை முடிக்கவும்; வரப்புகளை பலப்படுத்துங்கள்.",
                "kn": "ಬೇಸಿಗೆ ಉಳುಮೆ ಮತ್ತು ಬೀಜ ಸಂಗ್ರಹಣೆ ಪೂರ್ಣಗೊಳಿಸಿ; ಬದುಗಳನ್ನು ಸರಿಪಡಿಸಿ.",
                "ur": "گرمیوں کی جوتائی اور بیج کی خریداری مکمل کریں؛ مینڈھوں کی مرمت کریں۔",
                "ml": "വേനൽക്കാല ഉഴവും വിത്തുശേഖരണവും പൂർത്തിയാക്കുക; വരമ്പുകൾ ബലപ്പെടുത്തുക."
            },
            "irrig_drainage": {
                "en": "STOP ALL IRRIGATION. Open field drainage channels immediately to prevent root asphyxiation.",
                "te": "ఎలాంటి నీటిపారుదల చేయకండి. పొలంలో నీరు నిల్వ ఉండకుండా మురుగు కాల్వలను తెరిచి ఉంచండి.",
                "hi": "सिंचाई तुरंत बंद करें। खेत में जलभराव रोकने के लिए जल निकासी नाली तुरंत खोलें।",
                "ta": "அனைத்து பாசனங்களையும் நிறுத்துங்கள். வேர் அழுகலைத் தடுக்க வடிகால் வாய்க்கால்களைத் திறக்கவும்.",
                "kn": "ಎಲ್ಲಾ ನೀರಾವರಿ ನಿಲ್ಲಿಸಿ. ಬೇರು ಕೊಳೆಯುವುದನ್ನು ತಡೆಯಲು ನೀರು ಬಸಿದು ಹೋಗುವ ಕಾಲುವೆಗಳನ್ನು ತೆರೆಯಿರಿ.",
                "ur": "تمام آبپاشی روک دیں۔ جڑوں کو سڑنے سے بچانے کے لیے نکاسی آب کی نالیاں فوری کھولیں۔",
                "ml": "എല്ലാ നനയ്ക്കലും നിർത്തുക. വേരുകൾ ചീഞ്ഞുപോകാതിരിക്കാൻ നീർവാർച്ചാ ചാലുകൾ തുറക്കുക."
            },
            "irrig_protective": {
                "en": "Provide life-saving protective irrigation during evening hours using micro-sprinklers or drip systems.",
                "te": "సాయంత్రం వేళల్లో తుంపర లేదా బిందు సేద్యం ద్వారా జీవనాధార రక్షక తడి ఇవ్వండి.",
                "hi": "शाम के समय स्प्रिंकलर या ड्रिप से जीवनरक्षक सुरक्षात्मक सिंचाई प्रदान करें।",
                "ta": "மாலை வேளையில் தெளிப்பு அல்லது சொட்டு நீர் பாசனம் மூலம் உயிர் காக்கும் பாசனம் அளியுங்கள்.",
                "kn": "ಸಂಜೆ ಸಮಯದಲ್ಲಿ ತುಂತುರು ಅಥವಾ ಹನಿ ನೀರಾವರಿ ಮೂಲಕ ಜೀವ ರಕ್ಷಕ ನೀರಾವರಿ ಒದಗಿಸಿ.",
                "ur": "شام کے اوقات میں مائیکرو اسپرنکلر یا ڈرپ سے زندگی بچانے والی حفاظتی آبپاشی کریں۔",
                "ml": "വൈകുന്നേരങ്ങളിൽ സ്പ്രിംഗ്ലർ അല്ലെങ്കിൽ തുള്ളിനന വഴി ജീവൻരക്ഷാ നനവ് നൽകുക."
            },
            "irrig_normal": {
                "en": "Normal rainfed soil moisture adequate. No supplemental irrigation needed.",
                "te": "నేలలో తగినంత తేమ ఉన్నందున అదనపు నీరు అవసరం లేదు.",
                "hi": "मृदा में पर्याप्त नमी उपलब्ध है। अतिरिक्त सिंचाई की आवश्यकता नहीं है।",
                "ta": "மண்ணில் போதிய ஈரம் உள்ளது. கூடுதல் பாசனம் தேவையில்லை.",
                "kn": "ಮಣ್ಣಿನಲ್ಲಿ ಸಮರ್ಪಕ ತೇವಾಂಶವಿದೆ. ಹೆಚ್ಚುವರಿ ನೀರಾವರಿ ಅಗತ್ಯವಿಲ್ಲ.",
                "ur": "مٹی میں مناسب نمی موجود ہے۔ اضافی آبپاشی کی ضرورت نہیں ہے۔"
            },
            "fert_break": {
                "en": "STRICTLY SUSPEND urea top-dressing to prevent leaf scorch. Spray 1.5% KNO3 (13-0-45) to alleviate moisture stress.",
                "te": "యూరియా పైపాటు వేయడం వెంటనే ఆపండి. బెట్టను తట్టుకోవడానికి 1.5% పొటాషియం నైట్రేట్ పిచికారీ చేయండి.",
                "hi": "यूरिया का छिड़काव तुरंत रोकें। नमी के तनाव को कम करने के लिए 1.5% पोटेशियम नाइट्रेट का छिड़काव करें।",
                "ta": "யூரியா மேலுரமிடுவதை உடனடியாக நிறுத்துங்கள். ஈரப்பத அழுத்தத்தை குறைக்க 1.5% பொட்டாசியம் நைட்ரேட் தெளிக்கவும்.",
                "kn": "ಯೂರಿಯಾ ಮೇಲುಗೊಬ್ಬರ ಹಾಕುವುದನ್ನು ನಿಲ್ಲಿಸಿ. ತೇವಾಂಶ ಕೊರತೆ ನಿವಾರಿಸಲು 1.5% ಪೊಟ್ಯಾಸಿಯಮ್ ನೈಟ್ರೇಟ್ ಸಿಂಪಡಿಸಿ.",
                "ur": "یوریا کا اوپر سے استعمال فوری روک دیں۔ نمی کی کمی دور کرنے کے لیے 1.5% پوٹاشیم نائٹریٹ کا سپرے کریں۔",
                "ml": "യൂറിയ മേൽവളപ്രയോഗം നിർത്തിവെയ്ക്കുക. ഈർപ്പ സമ്മർദ്ദം കുറയ്ക്കാൻ 1.5% പൊട്ടാസ്യം നൈട്രേറ്റ് തളിക്കുക."
            },
            "fert_onset": {
                "en": "Apply full basal dose of Single Super Phosphate (Phosphorus) and MOP (Potash) placed 5 cm below seed depth.",
                "te": "విత్తనం నాటే సమయంలో సిఫార్సు చేసిన భాస్వరం మరియు పొటాష్ ఎరువులను విత్తనానికి 5 సెం.మీ దిగువన వేయండి.",
                "hi": "बुवाई के समय फॉस्फोरस और पोटाश की पूरी बेसल खुराक बीज से 5 सेमी नीचे दें।",
                "ta": "விதைப்புக்கு முன் மணிச்சத்து மற்றும் சாம்பல் சத்து உரங்களை விதை ஆழத்திற்கு 5 செ.மீ கீழே அடியுரமாக இடவும்.",
                "kn": "ಬಿತ್ತನೆ ಸಮಯದಲ್ಲಿ ಶಿಫಾರಸು ಮಾಡಿದ ರಂಜಕ ಮತ್ತು ಪೊಟ್ಯಾಶ್ ಗೊಬ್ಬರಗಳನ್ನು ಬೀಜದ ಆಳಕ್ಕಿಂತ 5 ಸೆಂ.ಮೀ ಕೆಳಗೆ ಹಾಕಿ.",
                "ur": "بوائی کے وقت فاسفورس اور پوٹاش کی بنیادی خوراک بیج سے 5 سینٹی میٹر نیچے ڈالیں۔",
                "ml": "വിത്ത് നടുന്ന സമയത്ത് ശുപാർശ ചെയ്ത ഫോസ്ഫറസ്, പൊട്ടാഷ് അടിവളങ്ങൾ വിത്തിന്റെ 5 സെ.മീ താഴെ ഇടുക."
            },
            "fert_fym": {
                "en": "Incorporate well-decomposed Farm Yard Manure (FYM) @ 8-10 t/ha during seedbed preparation.",
                "te": "దుక్కి తయారీ సమయంలో ఎకరాకు 4-5 టన్నుల పశువుల ఎరువును కలియదున్నండి.",
                "hi": "खेत की तैयारी के दौरान 8-10 टन/हेक्टेयर अच्छी सड़ी गोबर की खाद मिलाएं।",
                "ta": "நிலம் தயாரிப்பின் போது ஒரு ஹெக்டேருக்கு 8-10 டன் நன்கு மக்கிய தொழுவுரத்தை இடவும்.",
                "kn": "ಭೂಮಿ ಸಿದ್ಧತೆಯ ಸಮಯದಲ್ಲಿ ಎಕರೆಗೆ 4-5 ಟನ್ ಚೆನ್ನಾಗಿ ಕೊಳೆತ ಕೊಟ್ಟಿಗೆ ಗೊಬ್ಬರವನ್ನು ಬೆರೆಸಿ.",
                "ur": "زمین کی تیاری کے دوران 8-10 ٹن فی ہیکٹر اچھی طرح سے گلی سڑی گوبر کی کھاد ملائیں۔",
                "ml": "നിലമൊരുക്കുമ്പോൾ ഹെക്ടറിന് 8-10 ടൺ നല്ല കാലിവളമോ കമ്പോസ്റ്റോ ചേർക്കുക."
            },
            "pest_break": {
                "en": "Scout for sucking pests (thrips, aphids, whiteflies, red spider mites) proliferating in hot dry weather.",
                "te": "పొడి వాతావరణంలో ఎక్కువగా వచ్చే రసం పీల్చే పురుగుల (తామర పురుగులు, పేనుబంక) ఉధృతిని గమనించండి.",
                "hi": "गर्म शुष्क मौसम में रस चूसक कीटों (थ्रिप्स, एफिड्स, सफेद मक्खी) के प्रकोप की निगरानी करें।",
                "ta": "வெப்பமான வறண்ட வானிலையில் பெருகும் சாறு உறிஞ்சும் பூச்சிகள் (இலைப்பேன், அசுவினி) குறித்து கண்காணிக்கவும்.",
                "kn": "ಬಿಸಿಲು ಹಾಗೂ ಒಣ ಹವೆ ಹೆಚ್ಚಾದಾಗ ರಸ ಹೀರುವ ಕೀಟಗಳ (ಥ್ರಿಪ್ಸ್, ಜಿಗಿಹುಳು) ಹಾವಳಿಯನ್ನು ಗಮನಿಸಿ.",
                "ur": "گرم خشک موسم میں رس چوسنے والے کیڑوں (تھرپس، تیلا، سفید مکھی) کے حملے پر نظر رکھیں۔",
                "ml": "ചൂടുള്ള വരണ്ട കാലാവസ്ഥയിൽ പെരുകുന്ന നീരൂറ്റിക്കുടിക്കുന്ന കീടങ്ങളെ (ഇലപ്പേൻ, മുഞ്ഞ) നിരീക്ഷിക്കുക."
            },
            "pest_heavy": {
                "en": "High humidity risk: Monitor for collar rot, damping off, and bacterial leaf blight.",
                "te": "అధిక తేమ వల్ల వచ్చే కాండం కుళ్ళు, మొలక కుళ్ళు తెగుళ్ళ పట్ల అప్రమత్తంగా ఉండండి.",
                "hi": "अधिक आर्द्रता का जोखिम: तना गलन, आद्र-पतन और जीवाणु झुलसा रोग की निगरानी करें।",
                "ta": "அதிக ஈரப்பதம்: தண்டு அழுகல், நாற்று அழுகல் மற்றும் இலை கருகல் நோய்களைக் கண்காணிக்கவும்.",
                "kn": "ಹೆಚ್ಚಿನ ತೇವಾಂಶ: ಕಾಂಡ ಕೊಳೆತ, ಸಸಿ ಕೊಳೆತ ಮತ್ತು ಬ್ಯಾಕ್ಟೀರಿಯಲ್ ಎಲೆ ಕರಕಲು ರೋಗದ ಮೇಲೆ ನಿಗಾ ಇರಿಸಿ.",
                "ur": "زیادہ نمی کا خطرہ: تنے کی سڑاند، پودوں کے مرجھانے اور پتوں کے جھلسنے کی بیماریوں پر نظر رکھیں۔",
                "ml": "കൂടിയ ഈർപ്പം: തണ്ട് ചീയൽ, വേര് ചീയൽ, ബാക്ടീരിയൽ ഇലകരിച്ചിൽ എന്നിവ ശ്രദ്ധിക്കുക."
            },
            "pest_seed": {
                "en": "Treat seeds with Trichoderma viride (10g/kg) or Imidacloprid (5ml/kg) before sowing.",
                "te": "విత్తే ముందు ట్రైకోడెర్మా విరిడే (10 గ్రా/కేజీ) లేదా ఇమిడాక్లోప్రిడ్ తో విత్తన శుద్ధి చేయండి.",
                "hi": "बुवाई से पहले ट्राइकोडर्मा विरिडी (10 ग्राम/किग्रा) या इमिडाक्लोप्रिड से बीजोपचार करें।",
                "ta": "விதைப்பதற்கு முன் ட்ரைக்கோடெர்மா விரிடி (10g/kg) அல்லது இமிடாக்குளோபிரிட் மூலம் விதை நேர்த்தி செய்யவும்.",
                "kn": "ಬಿತ್ತನೆಗೆ ಮುನ್ನ ಟ್ರೈಕೋಡರ್ಮಾ ವಿರಿಡೆ (10ಗ್ರಾಂ/ಕೆಜಿ) ಅಥವಾ ಇಮಿಡಾಕ್ಲೋಪ್ರಿಡ್‌ನೊಂದಿಗೆ ಬೀಜೋಪಚಾರ ಮಾಡಿ.",
                "ur": "بوائی سے پہلے ٹرائیکوڈرما وریڈی (10 گرام/کلو) یا امیڈاکلوپرڈ سے بیج کا علاج کریں۔",
                "ml": "വിതയ്ക്കുന്നതിന് മുമ്പ് ട്രൈക്കോഡെർമ വിരിഡി (10 ഗ്രാം/കിലോഗ്രാം) അല്ലെങ്കിൽ ഇമിഡാക്ലോപ്രിഡ് ഉപയോഗിച്ച് വിത്ത് സംസ്കരിക്കുക."
            }
        }

        # Resolve language key
        lang_key = language if language in ["en", "te", "hi", "ta", "kn", "ur", "ml"] else "en"

        # Determine active keys
        if is_false_alarm:
            act_key = "action_false_alarm"
        elif is_break_critical or is_break_prob_high:
            act_key = "action_break_spell"
        elif is_onset_declared and cur_soil_moist >= profile["optimal_soil_moisture_pct"] * 0.8:
            act_key = "action_optimal"
        else:
            act_key = "action_await_moisture"

        if "EXTREME" in heavy_risk or "VERY_HEAVY" in heavy_risk:
            irrig_key = "irrig_drainage"
        elif is_break_critical:
            irrig_key = "irrig_protective"
        else:
            irrig_key = "irrig_normal"

        if is_break_critical:
            fert_key = "fert_break"
        elif is_onset_declared:
            fert_key = "fert_onset"
        else:
            fert_key = "fert_fym"

        if is_break_critical:
            pest_key = "pest_break"
        elif "HEAVY" in heavy_risk:
            pest_key = "pest_heavy"
        else:
            pest_key = "pest_seed"

        crop_display_name = profile.get(f"name_{lang_key}", profile.get("name_en", crop_code.capitalize()))
        priority_action = ADVISORY_TEXTS[act_key].get(lang_key, ADVISORY_TEXTS[act_key]["en"])
        irrigation_advice = ADVISORY_TEXTS[irrig_key].get(lang_key, ADVISORY_TEXTS[irrig_key]["en"])
        fertilizer_advice = ADVISORY_TEXTS[fert_key].get(lang_key, ADVISORY_TEXTS[fert_key]["en"])
        pest_advice = ADVISORY_TEXTS[pest_key].get(lang_key, ADVISORY_TEXTS[pest_key]["en"])

        # 5. Fix 3: CROP CHOICE / VARIETY ALTERNATIVE Advisory Category
        is_alteration_needed = bool(is_false_alarm or is_break_critical or is_break_prob_high)
        short_vars = profile.get("recommended_varieties_short_duration", [])
        contingency_text = profile.get("contingency_alternative", "")

        COND_TEXTS = {
            "unsuitable": {
                "en": "Delayed onset / prolonged dry spell",
                "te": "ఆలస్యమైన రుతుపవనాలు / సుదీర్ఘ వర్షపు విరామం (డ్రై స్పెల్)",
                "hi": "मानसून में देरी / लंबा शुष्क दौर (ड्राई स्पेल)",
                "ta": "தாமதமான பருவமழை / நீண்ட வறட்சி இடைவெளி",
                "kn": "ಮುಂಗಾರು ವಿಳಂಬ / ದೀರ್ಘ ಶುಷ್ಕ ಅವಧಿ",
                "ur": "مانسون میں تاخیر / طویل خشک دورانیہ",
                "ml": "കാലവർഷം വൈകൽ / നീണ്ട വരണ്ട കാലാവസ്ഥ"
            },
            "favorable": {
                "en": "Normal onset progression / favorable moisture",
                "te": "సాధారణ రుతుపవన పురోగతి / అనుకూలమైన తేమ",
                "hi": "सामान्य मानसूनी प्रगति / अनुकूल नमी",
                "ta": "வழக்கமான பருவமழை முன்னேற்றம் / உகந்த ஈரப்பதம்",
                "kn": "ಸಾಮಾನ್ಯ ಮುಂಗಾರು ಪ್ರಗತಿ / ಅನುಕೂಲಕರ ತೇವಾಂಶ",
                "ur": "معمول کے مطابق مانسونی پیش رفت / سازگار نمی",
                "ml": "സാധാരണ കാലവർഷ പുരോഗതി / അനുകൂല ഈർപ്പം"
            }
        }

        REASON_TEXTS = {
            "unsuitable": {
                "en": "Expected rainfall conditions and extended dry spell are unsuitable for the planned crop during early vegetative establishment.",
                "te": "ఎదురుచూస్తున్న వర్షాభావ పరిస్థితులు మరియు సుదీర్ఘ బెట్ట వల్ల పంట ప్రారంభ దశ దెబ్బతినే ప్రమాదం ఉంది.",
                "hi": "अपेक्षित वर्षा की कमी और लंबा शुष्क दौर प्रारंभिक वनस्पति विकास के लिए अनुपयुक्त है।",
                "ta": "எதிர்பார்க்கப்படும் மழைப் பற்றாக்குறை மற்றும் வறட்சி இடைவெளி பயிர் வளர்ச்சிக்கு உகந்ததாக இல்லை.",
                "kn": "ನಿರೀಕ್ಷಿತ ಮಳೆ ಕೊರತೆ ಮತ್ತು ದೀರ್ಘ ಶುಷ್ಕ ಹವೆ ಆರಂಭಿಕ ಬೆಳೆ ಬೆಳವಣಿಗೆಗೆ ಹಾನಿಕಾರಕವಾಗಿದೆ.",
                "ur": "متوقع بارش کی کمی اور طویل خشک وقفہ ابتدائی نشوونما کے لیے غیر موزوں ہے۔",
                "ml": "പ്രതീക്ഷിക്കുന്ന മഴക്കുറവും നീണ്ട വരൾച്ചയും ആദ്യഘട്ട വളർച്ചയ്ക്ക് പ്രതികൂലമാണ്."
            },
            "favorable": {
                "en": "Current soil moisture and monsoonal progression adequately support planned crop germination and establishment.",
                "te": "ప్రస్తుత నేల తేమ మరియు రుతుపవన పురోగతి పంట మొలకెత్తడానికి పూర్తి అనుకూలంగా ఉన్నాయి.",
                "hi": "वर्तमान मृदा नमी और मानसूनी प्रगति फसल के अंकुरण के लिए पूरी तरह अनुकूल है।",
                "ta": "தற்போதைய மண் ஈரம் மற்றும் பருவமழை முன்னேற்றம் விதை முளைப்பிற்கு ஏற்றதாக உள்ளது.",
                "kn": "ಪ್ರಸ್ತುತ ಮಣ್ಣಿನ ತೇವಾಂಶ ಮತ್ತು ಮುಂಗಾರು ಪ್ರಗತಿ ಬೀಜ ಮೊಳಕೆಯೊಡೆಯಲು ಅನುಕೂಲಕರವಾಗಿದೆ.",
                "ur": "موجودہ مٹی کی نمی اور مانسون کی پیش رفت بیج کے اگنے کے لیے بالکل سازگار ہے۔",
                "ml": "നിലവിലെ മണ്ണിന്റെ ഈർപ്പവും കാലവർഷവും വിത്ത് മുളയ്ക്കുന്നതിന് തികച്ചും അനുകൂലമാണ്."
            }
        }

        cond_key = "unsuitable" if is_alteration_needed else "favorable"
        forecast_condition = COND_TEXTS[cond_key].get(lang_key, COND_TEXTS[cond_key]["en"])
        choice_reason = REASON_TEXTS[cond_key].get(lang_key, REASON_TEXTS[cond_key]["en"])

        if is_alteration_needed:
            if contingency_text:
                choice_advisory = (
                    f"{contingency_text} "
                    f"(Short-duration varieties: {', '.join(short_vars) if short_vars else 'Standard cultivars'})."
                )
            else:
                choice_advisory = "Alternative crop recommendation unavailable for this condition."
        else:
            choice_advisory = (
                f"Retain planned {profile['name_en']}. Moisture outlook is favorable for recommended varieties: "
                f"{', '.join(short_vars) if short_vars else 'Certified seeds'}."
            )

        crop_choice_alteration = {
            "advisory_type": "CROP CHOICE",
            "is_alteration_recommended": is_alteration_needed,
            "current_crop": crop_display_name,
            "forecast_condition": forecast_condition,
            "crop_choice_advisory": choice_advisory,
            "reason": choice_reason,
            "recommended_contingency": contingency_text or "Alternative crop recommendation unavailable for this condition.",
            "recommended_short_duration_varieties": short_vars,
            "authority_source": profile["authority_source"]
        }

        # 5 Explicit Advisory Categories
        explicit_advisories = [
            {
                "category": "SOWING",
                "title": "Sowing Guidance",
                "status": sowing_status,
                "window": sowing_window,
                "instruction": priority_action,
                "reasoning": reasoning
            },
            {
                "category": "IRRIGATION",
                "title": "Irrigation Guidance",
                "status": "ACTIVE_IRRIGATION_CONTROL",
                "instruction": irrigation_advice,
                "reasoning": f"Based on projected soil moisture and rainfall anomaly."
            },
            {
                "category": "FERTILIZER",
                "title": "Nutrient & Fertilizer Schedule",
                "status": "APPLY_NUTRIENT" if not is_break_critical else "SUSPEND_UREA",
                "instruction": fertilizer_advice,
                "reasoning": f"Nutrient uptake is governed by active root-zone moisture availability."
            },
            {
                "category": "PEST/WEATHER RISK",
                "title": "Pest & Atmospheric Risk",
                "status": "SURVEILLANCE_REQUIRED",
                "instruction": pest_advice,
                "reasoning": f"Atmospheric humidity and temperature trigger specific pathogen/vector thresholds."
            },
            {
                "category": "CROP CHOICE",
                "title": "Crop Choice / Variety Alternative",
                "status": "ALTERATION_RECOMMENDED" if is_alteration_needed else "PLANNED_CROP_SUITABLE",
                "instruction": choice_advisory,
                "reasoning": choice_reason,
                "forecast_condition": forecast_condition
            }
        ]

        return {
            "crop_code": crop_code,
            "crop_name": crop_display_name,
            "language": language,
            "growth_stage": growth_stage or "Pre-sowing / Early Vegetative",
            "sowing_status": sowing_status,
            "sowing_window": sowing_window,
            "priority_action": priority_action,
            "irrigation_advice": irrigation_advice,
            "fertilizer_advice": fertilizer_advice,
            "pest_disease_advice": pest_advice,
            "contingency_alternative": profile["contingency_alternative"],
            "crop_choice_alteration": crop_choice_alteration,
            "advisory_categories": explicit_advisories,
            "advisory_types": {
                "SOWING": priority_action,
                "IRRIGATION": irrigation_advice,
                "FERTILIZER": fertilizer_advice,
                "PEST/WEATHER RISK": pest_advice,
                "CROP CHOICE": choice_advisory
            },
            "reasoning": reasoning,
            "rule_applied": rule_applied,
            "applicable_period": validity,
            "uncertainty_and_limitations": (
                "Advisory relies on statistical & physical model skill. "
                "Consult local Mandal Agricultural Officer (MAO) or KVK before irreversible field operations."
            ),
            "guidance_source": profile["authority_source"]
        }

    def generate_all_crop_advisories(
        self,
        forecast_data: Dict[str, Any],
        language: str = "en"
    ) -> List[Dict[str, Any]]:
        advisories = []
        for crop_code in CROP_PROFILES.keys():
            adv = self.generate_crop_advisory(crop_code, forecast_data, language=language)
            advisories.append(adv)
        return advisories

advisory_rules = AdvisoryRuleEngine()
