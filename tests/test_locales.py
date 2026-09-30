import json
from pathlib import Path
from config import Config

def test_locale_files_exist_and_valid():
    en_path = Config.FRONTEND_DIR / "locales" / "en.json"
    te_path = Config.FRONTEND_DIR / "locales" / "te.json"

    assert en_path.exists(), "locales/en.json missing"
    assert te_path.exists(), "locales/te.json missing"

    with open(en_path, "r", encoding="utf-8") as f:
        en_data = json.load(f)

    with open(te_path, "r", encoding="utf-8") as f:
        te_data = json.load(f)

    assert len(en_data) >= 30
    assert len(te_data) >= 30

    # Test key symmetry
    common_keys = set(en_data.keys()).intersection(set(te_data.keys()))
    assert len(common_keys) == len(en_data.keys()), "Mismatch in translation keys"

    # Verify Telugu characters exist in Telugu strings
    assert any("\u0c00" <= char <= "\u0c7f" for char in te_data["app_title"])

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
