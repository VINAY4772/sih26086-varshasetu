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

        # 5. Language Selection
        is_te = (language == "te")
        crop_display_name = profile["name_te"] if is_te else profile["name_en"]
        priority_action = priority_action_te if is_te else priority_action_en
        irrigation_advice = irrigation_te if is_te else irrigation_en
        fertilizer_advice = fertilizer_te if is_te else fertilizer_en
        pest_advice = pest_te if is_te else pest_en

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
