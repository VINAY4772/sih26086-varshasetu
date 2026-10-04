import json
from pathlib import Path
from config import Config

def test_locale_files_exist_and_valid():
    langs = ["en", "te", "hi", "ta", "kn", "ur", "ml"]
    data_by_lang = {}

    for lang in langs:
        p = Config.FRONTEND_DIR / "locales" / f"{lang}.json"
        assert p.exists(), f"locales/{lang}.json missing"
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert len(data) >= 50, f"Too few keys in {lang}.json"
            data_by_lang[lang] = data

    # Verify key symmetry across all 7 languages
    base_keys = set(data_by_lang["en"].keys())
    for lang in langs:
        assert set(data_by_lang[lang].keys()) == base_keys, f"Key mismatch in {lang}.json"

    # Verify script characters in respective languages
    assert any("\u0c00" <= c <= "\u0c7f" for c in data_by_lang["te"]["app_title"]), "Telugu characters missing"
    assert any("\u0900" <= c <= "\u097f" for c in data_by_lang["hi"]["app_title"]), "Devanagari characters missing"
    assert any("\u0b80" <= c <= "\u0bff" for c in data_by_lang["ta"]["app_title"]), "Tamil characters missing"
    assert any("\u0c80" <= c <= "\u0cff" for c in data_by_lang["kn"]["app_title"]), "Kannada characters missing"
    assert any("\u0600" <= c <= "\u06ff" for c in data_by_lang["ur"]["app_title"]), "Arabic/Urdu characters missing"
    assert any("\u0d00" <= c <= "\u0d7f" for c in data_by_lang["ml"]["app_title"]), "Malayalam characters missing"

def test_map_basemap_tile_configuration():
    map_js_path = Config.FRONTEND_DIR / "js" / "map.js"
    assert map_js_path.exists(), "frontend/js/map.js missing"

    content = map_js_path.read_text(encoding="utf-8")

    # Must use OpenStreetMap raster tile layer
    assert "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" in content

    # Must include OpenStreetMap copyright attribution
    assert "https://www.openstreetmap.org/copyright" in content
    assert "OpenStreetMap" in content

    # Must not contain broken/watermarked CartoDB basemap URL
    assert "basemaps.cartocdn.com" not in content
