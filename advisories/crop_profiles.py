"""
Crop Profiles & Phenological Thresholds Module: SIH26086
Defines agronomic parameters, soil moisture limits, and critical water sensitivity stages
for key Indian Kharif crops based on ICAR / CRIDA Agrometeorology Advisory Guidelines.
"""

from typing import Dict, Any

CROP_PROFILES: Dict[str, Dict[str, Any]] = {
    "paddy": {
        "crop_code": "paddy",
        "name_en": "Paddy / Rice",
        "name_te": "వరి (Paddy)",
        "name_hi": "धान / चावल (Paddy)",
        "name_ta": "நெல் / அரிசி (Paddy)",
        "name_kn": "ಭತ್ತ (Paddy)",
        "name_ur": "دھان / چاول (Paddy)",
        "name_ml": "നെല്ല് (Paddy)",
        "season": "Kharif",
        "min_sowing_rainfall_mm": 50.0,  # 3-4 day cumulative wetting for nursery bed
        "optimal_soil_moisture_pct": 70.0,
        "critical_growth_stages": [
            "Nursery Emergence (1-15 days)",
            "Tillering (20-40 days)",
            "Panicle Initiation (50-65 days)",
            "Flowering & Grain Filling (70-95 days)"
        ],
        "drought_sensitivity": "High at Flowering; Moderate at Tillering",
        "waterlogging_tolerance": "High",
        "recommended_varieties_short_duration": ["Telangana Sona (RNR 15048)", "MTU 1010", "IR 64"],
        "contingency_alternative": "If onset delayed past July 15, switch to short-duration pulses (Greengram / Blackgram) or Maize.",
        "authority_source": "ICAR-Indian Institute of Rice Research (IIRR) & CRIDA Hyderabad"
    },
    "cotton": {
        "crop_code": "cotton",
        "name_en": "Cotton",
        "name_te": "పత్తి (Cotton)",
        "name_hi": "कपास (Cotton)",
        "name_ta": "பருத்தி (Cotton)",
        "name_kn": "ಹತ್ತಿ (Cotton)",
        "name_ur": "کپاس (Cotton)",
        "name_ml": "പരുത്തി (Cotton)",
        "season": "Kharif",
        "min_sowing_rainfall_mm": 50.0,  # 50-60mm deep soil wetting to prevent seed scalding
        "optimal_soil_moisture_pct": 60.0,
        "critical_growth_stages": [
            "Square Formation (35-50 days)",
            "Flowering & Boll Development (60-90 days)",
            "Boll Bursting (100-130 days)"
        ],
        "drought_sensitivity": "Critical at Flowering and Boll development",
        "waterlogging_tolerance": "Very Low (Excess moisture triggers root asphyxiation and square drop)",
        "recommended_varieties_short_duration": ["Bt Hybrids with early boll maturity"],
        "contingency_alternative": "If onset is delayed past July 10 in shallow red soils, avoid cotton; adopt Pigeonpea or Castor.",
        "authority_source": "ICAR-Central Institute for Cotton Research (CICR) & PJTSAU"
    },
    "soybean": {
        "crop_code": "soybean",
        "name_en": "Soybean",
        "name_te": "సోయాబీన్ (Soybean)",
        "name_hi": "सोयाबीन (Soybean)",
        "name_ta": "சோயாபீன் (Soybean)",
        "name_kn": "ಸೋಯಾಬೀನ್ (Soybean)",
        "name_ur": "سویا بین (Soybean)",
        "name_ml": "സോയാബീൻ (Soybean)",
        "season": "Kharif",
        "min_sowing_rainfall_mm": 45.0,
        "optimal_soil_moisture_pct": 65.0,
        "critical_growth_stages": [
            "Germination & Emergence (1-7 days)",
            "Pod Initiation (35-50 days)",
            "Pod Filling (55-75 days)"
        ],
        "drought_sensitivity": "Extreme at Pod Filling (causes pod shattering & shriveled grain)",
        "waterlogging_tolerance": "Low",
        "recommended_varieties_short_duration": ["JS 335", "JS 95-60", "NRC 37"],
        "contingency_alternative": "If sowing delayed beyond July 7, switch to Sunflower, Sesame, or early Pulses.",
        "authority_source": "ICAR-Indian Institute of Soybean Research (IISR) Indore"
    },
    "groundnut": {
        "crop_code": "groundnut",
        "name_en": "Groundnut",
        "name_te": "వేరుశనగ (Groundnut)",
        "name_hi": "मूंगफली (Groundnut)",
        "name_ta": "நிலக்கடலை (Groundnut)",
        "name_kn": "ಕಡಲೆಕಾಯಿ (Groundnut)",
        "name_ur": "مونگ پھلی (Groundnut)",
        "name_ml": "നിലക്കടല (Groundnut)",
        "season": "Kharif",
        "min_sowing_rainfall_mm": 40.0,
        "optimal_soil_moisture_pct": 55.0,
        "critical_growth_stages": [
            "Flowering & Peg Penetration (30-50 days)",
            "Pod Development (50-75 days)"
        ],
        "drought_sensitivity": "Critical at Pegging and Pod Development",
        "waterlogging_tolerance": "Low",
        "recommended_varieties_short_duration": ["Kadiri 6", "Kadiri 9", "TAG 24"],
        "contingency_alternative": "If break spell coincides with pegging, provide protective micro-sprinkler irrigation immediately.",
        "authority_source": "ICAR-Directorate of Groundnut Research (DGR) Junagadh"
    },
    "maize": {
        "crop_code": "maize",
        "name_en": "Maize / Corn",
        "name_te": "మొక్కజొన్న (Maize)",
        "name_hi": "मक्का (Maize)",
        "name_ta": "மக்காச்சோளம் (Maize)",
        "name_kn": "ಮೆಕ್ಕೆಜೋಳ (Maize)",
        "name_ur": "مکئی (Maize)",
        "name_ml": "ചോളം (Maize)",
        "season": "Kharif",
        "min_sowing_rainfall_mm": 40.0,
        "optimal_soil_moisture_pct": 60.0,
        "critical_growth_stages": [
            "Tasseling & Silking (45-60 days)",
            "Grain Formation (65-80 days)"
        ],
        "drought_sensitivity": "Very High at Tasseling/Silking",
        "waterlogging_tolerance": "Low to Moderate",
        "recommended_varieties_short_duration": ["DHM 117", "Bio 9681", "Pioneer 30V92"],
        "contingency_alternative": "Tolerates delayed sowing up to July 20 with hybrid early cultivars.",
        "authority_source": "ICAR-Indian Institute of Maize Research (IIMR)"
    },
    "pulses": {
        "crop_code": "pulses",
        "name_en": "Redgram / Pigeonpea",
        "name_te": "కంది (Redgram)",
        "name_hi": "अरहर / तूर (Redgram)",
        "name_ta": "துவரை (Redgram)",
        "name_kn": "ತೊಗರಿ (Redgram)",
        "name_ur": "ارہر / دال تور (Redgram)",
        "name_ml": "തുവര (Redgram)",
        "season": "Kharif",
        "min_sowing_rainfall_mm": 35.0,
        "optimal_soil_moisture_pct": 50.0,
        "critical_growth_stages": [
            "Branching (30-45 days)",
            "Flowering & Pod Setting (90-120 days)"
        ],
        "drought_sensitivity": "High tolerance due to deep taproot; sensitive at flowering",
        "waterlogging_tolerance": "Very Low (Highly susceptible to Phytophthora stem blight)",
        "recommended_varieties_short_duration": ["PRG 176", "ICPL 87119 (Asha)", "WRG 65"],
        "contingency_alternative": "Ideal contingency crop when delayed onset prevents cotton or soybean.",
        "authority_source": "ICAR-Indian Institute of Pulses Research (IIPR) & PJTSAU"
    }
}

def get_crop_display_name(crop_code: str, language: str = "en") -> str:
    profile = CROP_PROFILES.get(crop_code, {})
    key = f"name_{language}"
    return profile.get(key, profile.get("name_en", crop_code.capitalize()))
