import os
import json
import datetime
from pathlib import Path
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename

from database.initialise import get_db_connection
from forecasting.predict import pipeline as forecast_pipeline
from forecasting.evaluate import get_model_evaluation_report
from forecasting.data_ingestion import DataIngestionPipeline
from advisories.rules import advisory_rules
from advisories.crop_profiles import CROP_PROFILES
from config import Config

api_bp = Blueprint("api", __name__, url_prefix="/api")

ALLOWED_EXTENSIONS = {"csv"}

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@api_bp.route("/health", methods=["GET"])
def health_check():
    """
    Health check returning operational status, server timestamp, and database connectivity.
    """
    db_connected = False
    try:
        conn = get_db_connection()
        conn.execute("SELECT 1").fetchone()
        conn.close()
        db_connected = True
    except Exception:
        db_connected = False

    return jsonify({
        "status": "healthy" if db_connected else "degraded",
        "service": "VarshaSetu Flask Backend (SIH26086)",
        "product_name": "VarshaSetu",
        "tagline": "Bridging Climate Intelligence with Every Farmer",
        "database_connected": db_connected,
        "version": "1.0.0",
        "timestamp": datetime.datetime.now().isoformat()
    }), (200 if db_connected else 503)

@api_bp.route("/locations", methods=["GET"])
def get_locations():
    """
    Returns registered agricultural locations (blocks/mandals and villages).
    Optional query parameter 'q' filters by name, block, district, or state.
    """
    q = request.args.get("q", "").strip().lower()
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM locations ORDER BY state, district, block_or_mandal").fetchall()
    conn.close()

    locations = [dict(r) for r in rows]
    if q:
        locations = [
            loc for loc in locations
            if q in loc["name"].lower()
            or q in loc["block_or_mandal"].lower()
            or q in loc["district"].lower()
            or q in loc["state"].lower()
        ]
    return jsonify(locations)

@api_bp.route("/forecast", methods=["GET"])
def get_forecast():
    """
    Returns calibrated multi-horizon forecast.
    Query parameters:
    - location_id (default: 'tel_wgl_dharmasagar')
    - horizon: 7, 14, 21, 30 (default: 14)
    - scenario: 'default', 'onset_active', 'break_spell', 'pre_monsoon'
    """
    location_id = request.args.get("location_id", "tel_wgl_dharmasagar")
    horizon_str = request.args.get("horizon", "14")
    scenario = request.args.get("scenario")
    if scenario == "default":
        scenario = None

    try:
        horizon = int(horizon_str)
        if horizon not in [7, 14, 21, 30]:
            return jsonify({
                "error": "Invalid horizon. Supported forecast horizons are 7, 14, 21, and 30 days."
            }), 400
    except ValueError:
        return jsonify({"error": "Horizon parameter must be an integer."}), 400

    try:
        fc = forecast_pipeline.generate_forecast(location_id, horizon_days=horizon, scenario=scenario)
        return jsonify(fc)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"Internal forecasting error: {str(e)}"}), 500

@api_bp.route("/risk-map", methods=["GET"])
def get_risk_map():
    """
    Returns GIS layers:
    1. Monsoon Isochrones GeoJSON (Northern Limit of Monsoon advancement)
    2. Doppler Radar Rainfall Intensity Grid
    3. Location pins with current risk status
    """
    conn = get_db_connection()
    loc_rows = conn.execute("SELECT * FROM locations").fetchall()
    conn.close()

    # GeoJSON isochrones
    isochrones = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"date": "01 June", "label": "1 June Normal (Kerala / South TN)", "color": "#10b981", "stroke_width": 3},
                "geometry": {"type": "LineString", "coordinates": [[72.5, 8.2], [76.5, 8.5], [77.5, 9.2], [80.0, 11.5], [86.0, 14.0], [92.0, 18.0]]}
            },
            {
                "type": "Feature",
                "properties": {"date": "05 June", "label": "5 June Normal (Karnataka / Rayalaseema)", "color": "#06b6d4", "stroke_width": 3},
                "geometry": {"type": "LineString", "coordinates": [[73.5, 14.5], [75.8, 14.8], [78.5, 15.2], [83.0, 16.5], [88.5, 19.5], [94.0, 24.0]]}
            },
            {
                "type": "Feature",
                "properties": {"date": "10 June", "label": "10 June Normal (Maharashtra, Telangana, South Odisha)", "color": "#3b82f6", "stroke_width": 4},
                "geometry": {"type": "LineString", "coordinates": [[72.8, 19.0], [75.5, 18.5], [79.2, 18.2], [83.5, 18.8], [87.5, 21.5], [92.5, 26.0]]}
            },
            {
                "type": "Feature",
                "properties": {"date": "15 June", "label": "15 June Normal (MP, Bengal, Gujarat border)", "color": "#8b5cf6", "stroke_width": 3},
                "geometry": {"type": "LineString", "coordinates": [[71.0, 21.5], [74.5, 22.0], [78.0, 22.5], [83.0, 23.5], [88.0, 24.5], [90.5, 27.0]]}
            },
            {
                "type": "Feature",
                "properties": {"date": "01 July", "label": "1 July Normal (NW India, Punjab, Haryana, Rajasthan)", "color": "#f59e0b", "stroke_width": 3},
                "geometry": {"type": "LineString", "coordinates": [[70.0, 25.0], [73.0, 27.0], [76.5, 29.5], [78.5, 31.0]]}
            }
        ]
    }

    # Radar gridded rainfall intensity points
    radar_grid = [
        {"lat": 17.99, "lon": 79.48, "intensity_mm_hr": 14.2, "cloud_top_km": 11.5},
        {"lat": 18.05, "lon": 79.55, "intensity_mm_hr": 18.0, "cloud_top_km": 12.2},
        {"lat": 17.92, "lon": 79.41, "intensity_mm_hr": 8.5, "cloud_top_km": 9.8},
        {"lat": 16.76, "lon": 78.13, "intensity_mm_hr": 4.2, "cloud_top_km": 8.1},
        {"lat": 20.81, "lon": 77.96, "intensity_mm_hr": 0.0, "cloud_top_km": 4.2},
        {"lat": 18.25, "lon": 76.50, "intensity_mm_hr": 0.2, "cloud_top_km": 3.8},
        {"lat": 23.01, "lon": 76.72, "intensity_mm_hr": 22.4, "cloud_top_km": 13.0},
        {"lat": 16.24, "lon": 80.64, "intensity_mm_hr": 6.1, "cloud_top_km": 9.0}
    ]

    location_markers = [dict(loc) for loc in loc_rows]

    # Load high-resolution Block/Mandal/Panchayat GeoJSON boundaries
    geojson_path = Config.DATA_DIR / "geojson" / "blocks_boundary.json"
    block_polygons = None
    if geojson_path.exists():
        try:
            with open(geojson_path, "r", encoding="utf-8") as f:
                block_polygons = json.load(f)
        except Exception:
            block_polygons = None

    return jsonify({
        "map_type": "DEMONSTRATION_RISK_MAP",
        "disclaimer": "DEMONSTRATION ONLY — Map polygons are approximate geometric illustrations, not official administrative boundaries from Survey of India.",
        "isochrones_provenance": "Simulated Normal Isochrone Contours (Illustrative Demonstration)",
        "radar_provenance": "Simulated Doppler Radar Reflectivity Points (Illustrative Demonstration)",
        "polygons_provenance": "Approximate Bounding-Box Polygons (Not Official Administrative Boundaries)",
        "isochrones": isochrones,
        "radar_grid": radar_grid,
        "locations": location_markers,
        "block_polygons": block_polygons
    })

@api_bp.route("/rainfall-history", methods=["GET"])
def get_rainfall_history():
    """
    Returns time-series observations for a location.
    Query parameters:
    - location_id (default: 'tel_wgl_dharmasagar')
    - limit (default: 30)
    """
    location_id = request.args.get("location_id", "tel_wgl_dharmasagar")
    limit = int(request.args.get("limit", 30))

    conn = get_db_connection()
    rows = conn.execute(
        """
        SELECT date, rainfall_mm, temp_max_c, humidity_pct, soil_moisture_pct, data_source_id
        FROM observations
        WHERE location_id = ?
        ORDER BY date DESC LIMIT ?
        """,
        (location_id, limit)
    ).fetchall()
    conn.close()

    history = [dict(r) for r in reversed(rows)]
    return jsonify({
        "location_id": location_id,
        "record_count": len(history),
        "history": history
    })

@api_bp.route("/advisories", methods=["GET"])
def get_advisories():
    """
    Returns crop-specific agricultural guidance.
    Query parameters:
    - location_id (default: 'tel_wgl_dharmasagar')
    - lang: 'en' or 'te' (default: 'en')
    - crop: optional crop code ('paddy', 'cotton', 'soybean', 'groundnut', 'maize', 'pulses')
    - scenario: demonstration scenario
    """
    location_id = request.args.get("location_id", "tel_wgl_dharmasagar")
    lang = request.args.get("lang", "en")
    crop = request.args.get("crop")
    scenario = request.args.get("scenario")
    if scenario == "default":
        scenario = None

    if lang not in Config.SUPPORTED_LANGUAGES:
        lang = "en"

    try:
        fc = forecast_pipeline.generate_forecast(location_id, horizon_days=14, scenario=scenario)
        if crop:
            advisories = [advisory_rules.generate_crop_advisory(crop, fc, language=lang)]
        else:
            advisories = advisory_rules.generate_all_crop_advisories(fc, language=lang)

        return jsonify({
            "location_id": location_id,
            "language": lang,
            "monsoon_onset_status": fc["onset_outlook"]["status"],
            "break_risk_level": fc["break_spell_outlook"]["risk_level"],
            "advisories": advisories
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route("/model-info", methods=["GET"])
def get_model_info():
    """
    Returns machine-learning model card, training details, Brier scores, and limitations.
    """
    report = get_model_evaluation_report()
    return jsonify(report)

@api_bp.route("/data-sources", methods=["GET"])
def get_data_sources():
    """
    Returns registered data sources and their licensing/resolution details.
    """
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM data_sources").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@api_bp.route("/data/upload", methods=["POST"])
def upload_data():
    """
    Safe file upload endpoint for CSV rainfall records.
    Validates file extension, size limit, and schema columns.
    """
    if "file" not in request.files:
        return jsonify({"error": "No file part in the request."}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected."}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Only CSV files are allowed."}), 400

    filename = secure_filename(file.filename)
    dest_path = Config.DATA_DIR / "processed" / f"upload_{int(datetime.datetime.now().timestamp())}_{filename}"
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    file.save(str(dest_path))

    # Process and ingest
    try:
        pipeline = DataIngestionPipeline()
        result = pipeline.ingest_csv_to_db(str(dest_path))
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Failed to ingest uploaded CSV: {str(e)}"}), 400

@api_bp.route("/notifications/simulate", methods=["POST"])
def simulate_notification():
    """
    Sandbox notification simulation endpoint for SMS/WhatsApp.
    Supports Farmer and Agricultural Extension Officer recipient types.
    Clearly records simulated delivery without claiming real transmission.
    """
    payload = request.get_json(silent=True) or {}
    phone = payload.get("phone", "+91-98XXXXXXXX")
    channel = payload.get("channel", "sms").lower()
    if channel not in ["sms", "whatsapp"]:
        channel = "sms"
    recipient_type = payload.get("recipient_type", "farmer").lower()
    if recipient_type not in ["farmer", "officer"]:
        recipient_type = "farmer"

    location_name = payload.get("location_name", "Local Catchment")
    crop_name = payload.get("crop_name", "Kharif Crops")
    horizon = payload.get("horizon_days", 14)
    risk_condition = payload.get("risk_condition", "Monsoon Circulation Evaluation")
    action = payload.get("action", "Follow advisory guidelines")
    raw_message = payload.get("message")

    # Construct contextual, tailored bulletin based on recipient type if not already fully formatted
    if raw_message and ("[" in raw_message and "]" in raw_message and len(raw_message) > 40):
        final_message = raw_message
    else:
        if recipient_type == "officer":
            final_message = (
                f"[VarshaSetu AGRI-OFFICER BULLETIN]\n"
                f"Recipient: Agricultural Extension Officer\n"
                f"Area / Block: {location_name}\n"
                f"Forecast Horizon: {horizon}-day outlook\n"
                f"Monsoon Risk: {risk_condition}\n"
                f"Affected Crop(s): {crop_name}\n"
                f"Mandated Directive: {action}\n"
                f"Channel: {channel.upper()} | Delivery: SIMULATED DELIVERY"
            )
        else:
            final_message = (
                f"[VarshaSetu Farmer Advisory]\n"
                f"Recipient: Farmer\n"
                f"Location: {location_name}\n"
                f"Crop: {crop_name}\n"
                f"Forecast Horizon: {horizon}-day outlook\n"
                f"Condition: {risk_condition}\n"
                f"Recommended Action: {action}\n"
                f"Channel: {channel.upper()} | Delivery: SIMULATED DELIVERY"
            )

    # Mask phone number for privacy
    clean_digits = "".join(ch for ch in phone if ch.isdigit())
    if len(clean_digits) >= 10:
        masked = f"+91-{clean_digits[-10:-4]}XXXX"
    else:
        masked = phone[:6] + "XXXX" if len(phone) >= 6 else "ANONYMIZED"

    conn = get_db_connection()
    try:
        conn.execute(
            """
            INSERT INTO notification_logs (recipient_type, recipient_mask, channel, message_body, status, simulated)
            VALUES (?, ?, ?, ?, 'DELIVERED (SIMULATED)', 1)
            """,
            (recipient_type, masked, channel, final_message)
        )
    except Exception:
        # Fallback if recipient_type column is missing in legacy table
        conn.execute(
            """
            INSERT INTO notification_logs (recipient_mask, channel, message_body, status, simulated)
            VALUES (?, ?, ?, 'DELIVERED (SIMULATED)', 1)
            """,
            (masked, channel, final_message)
        )
    conn.commit()
    conn.close()

    return jsonify({
        "status": "SIMULATED_SUCCESS",
        "delivery_status": "DELIVERED (SIMULATED)",
        "notice": "SIMULATION ONLY: No actual SMS or WhatsApp was dispatched.",
        "recipient_type": recipient_type,
        "channel": channel,
        "recipient_mask": masked,
        "message": final_message,
        "timestamp": datetime.datetime.now().isoformat()
    })

@api_bp.route("/notifications/history", methods=["GET"])
def get_notification_history():
    """
    Returns recent simulated SMS/WhatsApp transmissions for audit verification.
    """
    conn = get_db_connection()
    try:
        rows = conn.execute(
            """
            SELECT id, recipient_type, recipient_mask, channel, message_body, status, simulated, created_at
            FROM notification_logs
            ORDER BY id DESC LIMIT 15
            """
        ).fetchall()
    except Exception:
        rows = conn.execute(
            """
            SELECT id, 'farmer' as recipient_type, recipient_mask, channel, message_body, status, simulated, created_at
            FROM notification_logs
            ORDER BY id DESC LIMIT 15
            """
        ).fetchall()
    conn.close()

    return jsonify([dict(r) for r in rows])
