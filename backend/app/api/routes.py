from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import datetime
from ..models.schemas import (
    Location,
    OnsetForecastResponse,
    BreakSpellForecastResponse,
    FullAdvisoryResponse,
    IsochroneGeoJSON,
    RadarGridPoint
)
from ..services.weather_service import weather_service
from ..forecasting.onset_model import onset_engine
from ..forecasting.break_model import break_engine
from ..services.advisory_service import advisory_engine
from ..services.i18n_service import i18n_service

router = APIRouter(prefix="/api/v1")

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "SIH26086 Hyperlocal Monsoon Onset & Break Prediction System",
        "version": "1.0.0",
        "timestamp": datetime.datetime.now().isoformat()
    }

@router.get("/locations", response_model=List[Location])
def get_locations(q: Optional[str] = None):
    locations = weather_service.get_all_locations()
    if q:
        query = q.lower()
        locations = [
            loc for loc in locations
            if query in loc.name.lower() or query in loc.block.lower() or query in loc.district.lower() or query in loc.state.lower()
        ]
    return locations

@router.get("/forecast/onset", response_model=OnsetForecastResponse)
def get_onset_forecast(
    location_id: Optional[str] = "tel_wgl_dharmasagar",
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    scenario: Optional[str] = None
):
    if lat is not None and lon is not None:
        location = weather_service.find_nearest_location(lat, lon)
    else:
        location = weather_service.get_location_by_id(location_id)
        if not location:
            raise HTTPException(status_code=404, detail=f"Location '{location_id}' not found.")

    weather_data = weather_service.get_hyperlocal_weather_history_and_forecast(
        location, scenario=scenario
    )
    return onset_engine.predict_onset(
        location=location,
        history=weather_data["history"],
        forecast=weather_data["forecast"]
    )

@router.get("/forecast/break", response_model=BreakSpellForecastResponse)
def get_break_forecast(
    location_id: Optional[str] = "tel_wgl_dharmasagar",
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    scenario: Optional[str] = None
):
    if lat is not None and lon is not None:
        location = weather_service.find_nearest_location(lat, lon)
    else:
        location = weather_service.get_location_by_id(location_id)
        if not location:
            raise HTTPException(status_code=404, detail=f"Location '{location_id}' not found.")

    weather_data = weather_service.get_hyperlocal_weather_history_and_forecast(
        location, scenario=scenario
    )
    return break_engine.predict_break_spell(
        location=location,
        history=weather_data["history"],
        forecast=weather_data["forecast"]
    )

@router.get("/advisory", response_model=FullAdvisoryResponse)
def get_agricultural_advisory(
    location_id: Optional[str] = "tel_wgl_dharmasagar",
    lang: str = Query("en", description="Target language code: en, hi, te, mr, ta, bn, kn"),
    scenario: Optional[str] = None
):
    location = weather_service.get_location_by_id(location_id)
    if not location:
        raise HTTPException(status_code=404, detail=f"Location '{location_id}' not found.")

    weather_data = weather_service.get_hyperlocal_weather_history_and_forecast(
        location, scenario=scenario
    )
    onset_fc = onset_engine.predict_onset(location, weather_data["history"], weather_data["forecast"])
    break_fc = break_engine.predict_break_spell(location, weather_data["history"], weather_data["forecast"])

    base_advisory = advisory_engine.generate_advisories(location, onset_fc, break_fc, language="en")
    return i18n_service.localize_advisory(base_advisory, target_lang=lang)

@router.get("/gis/isochrones", response_model=IsochroneGeoJSON)
def get_monsoon_isochrones():
    """
    Returns Northern Limit of Monsoon (NLM) isochrone lines across India
    demonstrating the historical and real-time advance of the southwest monsoon.
    """
    features = [
        {
            "type": "Feature",
            "properties": {
                "date": "June 01",
                "label": "1 June Normal (Kerala & South TN)",
                "color": "#10b981",
                "stroke_width": 3
            },
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [72.5, 8.2], [76.5, 8.5], [77.5, 9.2], [80.0, 11.5], [86.0, 14.0], [92.0, 18.0]
                ]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "date": "June 05",
                "label": "5 June Normal (Karnataka & Rayalaseema)",
                "color": "#06b6d4",
                "stroke_width": 3
            },
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [73.5, 14.5], [75.8, 14.8], [78.5, 15.2], [83.0, 16.5], [88.5, 19.5], [94.0, 24.0]
                ]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "date": "June 10",
                "label": "10 June Normal (Maharashtra, Telangana, South Odisha)",
                "color": "#3b82f6",
                "stroke_width": 4
            },
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [72.8, 19.0], [75.5, 18.5], [79.2, 18.2], [83.5, 18.8], [87.5, 21.5], [92.5, 26.0]
                ]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "date": "June 15",
                "label": "15 June Normal (Gujarat borders, MP, Jharkhand, Bengal)",
                "color": "#8b5cf6",
                "stroke_width": 3
            },
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [71.0, 21.5], [74.5, 22.0], [78.0, 22.5], [83.0, 23.5], [88.0, 24.5], [90.5, 27.0]
                ]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "date": "July 01",
                "label": "1 July Normal (NW India, Punjab, Haryana, Rajasthan)",
                "color": "#f59e0b",
                "stroke_width": 3
            },
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [70.0, 25.0], [73.0, 27.0], [76.5, 29.5], [78.5, 31.0]
                ]
            }
        }
    ]
    return IsochroneGeoJSON(features=features)

@router.get("/gis/rainfall-radar", response_model=List[RadarGridPoint])
def get_rainfall_radar_grid():
    """
    Gridded radar precipitation intensity for Leaflet map overlay.
    """
    grid = [
        RadarGridPoint(lat=17.99, lon=79.48, intensity_mm_hr=14.2, cloud_top_km=11.5),
        RadarGridPoint(lat=18.05, lon=79.55, intensity_mm_hr=18.0, cloud_top_km=12.2),
        RadarGridPoint(lat=17.92, lon=79.41, intensity_mm_hr=8.5, cloud_top_km=9.8),
        RadarGridPoint(lat=16.76, lon=78.13, intensity_mm_hr=4.2, cloud_top_km=8.1),
        RadarGridPoint(lat=20.81, lon=77.96, intensity_mm_hr=0.0, cloud_top_km=4.2),
        RadarGridPoint(lat=18.25, lon=76.50, intensity_mm_hr=0.2, cloud_top_km=3.8),
        RadarGridPoint(lat=23.01, lon=76.72, intensity_mm_hr=22.4, cloud_top_km=13.0),
        RadarGridPoint(lat=16.24, lon=80.64, intensity_mm_hr=6.1, cloud_top_km=9.0),
        RadarGridPoint(lat=23.19, lon=88.11, intensity_mm_hr=16.8, cloud_top_km=12.5),
        RadarGridPoint(lat=30.78, lon=75.47, intensity_mm_hr=1.2, cloud_top_km=6.0)
    ]
    return grid
