import datetime
import math
from typing import List, Dict, Optional
from ..models.schemas import Location, WeatherDailyPoint

# Comprehensive registry of representative Indian agricultural blocks & villages
INDIAN_BLOCKS_REGISTRY: List[Location] = [
    Location(
        id="tel_wgl_dharmasagar",
        name="Dharmasagar Village",
        block="Dharmasagar",
        district="Hanamkonda / Warangal",
        state="Telangana",
        lat=17.9944,
        lon=79.4892,
        elevation_m=280.0,
        primary_soil="Red Sandy Loam & Black Soil",
        agro_climatic_zone="Southern Telangana Agro-Climatic Zone"
    ),
    Location(
        id="tel_mbnr_jadcherla",
        name="Badepally Village",
        block="Jadcherla",
        district="Mahabubnagar",
        state="Telangana",
        lat=16.7645,
        lon=78.1367,
        elevation_m=490.0,
        primary_soil="Chalka (Red Sandy)",
        agro_climatic_zone="South-Western Telangana Zone"
    ),
    Location(
        id="ap_gnr_tenali",
        name="Angalakuduru Village",
        block="Tenali",
        district="Guntur",
        state="Andhra Pradesh",
        lat=16.2437,
        lon=80.6400,
        elevation_m=15.0,
        primary_soil="Deltaic Alluvial & Black Clay",
        agro_climatic_zone="Krishna-Godavari Zone"
    ),
    Location(
        id="ap_knl_adoni",
        name="Arekal Village",
        block="Adoni",
        district="Kurnool",
        state="Andhra Pradesh",
        lat=15.6322,
        lon=77.2728,
        elevation_m=435.0,
        primary_soil="Black Cotton & Gravelly Red",
        agro_climatic_zone="Scarce Rainfall Zone of Rayalaseema"
    ),
    Location(
        id="mh_amr_chandur",
        name="Amla Vishweshwar Village",
        block="Chandur Railway",
        district="Amravati",
        state="Maharashtra",
        lat=20.8123,
        lon=77.9654,
        elevation_m=340.0,
        primary_soil="Deep Black Cotton Soil (Regur)",
        agro_climatic_zone="Vidarbha Central Plateau"
    ),
    Location(
        id="mh_ltr_ausa",
        name="Ashiv Village",
        block="Ausa",
        district="Latur",
        state="Maharashtra",
        lat=18.2514,
        lon=76.5028,
        elevation_m=620.0,
        primary_soil="Medium Deep Black Soil",
        agro_climatic_zone="Marathwada Rain-Shadow Zone"
    ),
    Location(
        id="mp_seh_ashta",
        name="Khajuria Kasam Village",
        block="Ashta",
        district="Sehore",
        state="Madhya Pradesh",
        lat=23.0189,
        lon=76.7214,
        elevation_m=485.0,
        primary_soil="Deep Heavy Vertisols (Black)",
        agro_climatic_zone="Malwa Plateau Soybean Belt"
    ),
    Location(
        id="ka_dwd_hubli",
        name="Unkal Village",
        block="Hubballi Rural",
        district="Dharwad",
        state="Karnataka",
        lat=15.3647,
        lon=75.1240,
        elevation_m=670.0,
        primary_soil="Medium Black & Mixed Red Soil",
        agro_climatic_zone="Northern Transition Zone"
    ),
    Location(
        id="wb_bdn_memari",
        name="Nimo Village",
        block="Memari I",
        district="Purba Bardhaman",
        state="West Bengal",
        lat=23.1977,
        lon=88.1123,
        elevation_m=28.0,
        primary_soil="Old Alluvial & Silt Loam",
        agro_climatic_zone="New Alluvial Zone (Rice Bowl)"
    ),
    Location(
        id="pb_ldh_jagraon",
        name="Swaddi Khas Village",
        block="Jagraon",
        district="Ludhiana",
        state="Punjab",
        lat=30.7871,
        lon=75.4789,
        elevation_m=234.0,
        primary_soil="Indo-Gangetic Coarse Loamy Alluvium",
        agro_climatic_zone="Trans-Gangetic Plains"
    )
]

class WeatherService:
    def __init__(self):
        self.locations_by_id = {loc.id: loc for loc in INDIAN_BLOCKS_REGISTRY}

    def get_all_locations(self) -> List[Location]:
        return INDIAN_BLOCKS_REGISTRY

    def get_location_by_id(self, location_id: str) -> Optional[Location]:
        return self.locations_by_id.get(location_id)

    def find_nearest_location(self, lat: float, lon: float) -> Location:
        """Finds closest registered block/village using Euclidean distance approximation."""
        best_loc = INDIAN_BLOCKS_REGISTRY[0]
        min_dist = float("inf")
        for loc in INDIAN_BLOCKS_REGISTRY:
            dist = math.hypot(loc.lat - lat, loc.lon - lon)
            if dist < min_dist:
                min_dist = dist
                best_loc = loc
        return best_loc

    def get_hyperlocal_weather_history_and_forecast(
        self,
        location: Location,
        days_history: int = 14,
        days_forecast: int = 14,
        scenario: Optional[str] = None
    ) -> Dict[str, List[WeatherDailyPoint]]:
        """
        Generates meteorologically coherent weather timelines.
        Supported scenarios for realistic testing:
        - "onset_active": Fulfills 48hr rain criteria, OLR drop, westerly depth
        - "break_spell": Mid-monsoon prolonged dry spell (5-10 days no rain, high temp, high OLR)
        - "pre_monsoon": Isolated thunderstorm, high OLR, weak wind shear
        - "normal_monsoon": Intermittent showers, high soil moisture
        """
        today = datetime.date.today()
        history: List[WeatherDailyPoint] = []
        forecast: List[WeatherDailyPoint] = []

        # Location seed modifier based on latitude (South arrives earlier than North)
        lat_factor = (location.lat - 10.0) / 20.0  # 0.0 to 1.0 approx

        for d in range(-days_history, 0):
            day_date = today + datetime.timedelta(days=d)
            point = self._synthesize_weather_day(day_date, location, d, is_forecast=False, scenario=scenario, lat_factor=lat_factor)
            history.append(point)

        for d in range(0, days_forecast):
            day_date = today + datetime.timedelta(days=d)
            point = self._synthesize_weather_day(day_date, location, d, is_forecast=True, scenario=scenario, lat_factor=lat_factor)
            forecast.append(point)

        return {"history": history, "forecast": forecast}

    def _synthesize_weather_day(
        self,
        date_val: datetime.date,
        location: Location,
        day_offset: int,
        is_forecast: bool,
        scenario: Optional[str],
        lat_factor: float
    ) -> WeatherDailyPoint:
        # Defaults based on scenario
        if scenario == "break_spell":
            # Break spell: dry spell in forecast, hot temperatures, low cloudiness, OLR > 230
            if day_offset >= 0:
                rainfall = 0.0 if day_offset not in [3, 8] else 0.4
                t_max = 35.5 + (day_offset * 0.3)
                t_min = 25.0
                humidity = 48.0 - (day_offset * 1.2)
                olr = 245.0 + (day_offset * 2.0)
                zonal_wind = 4.0  # collapsed westerly jet
                soil_moisture = max(18.0, 48.0 - (day_offset * 3.5))
            else:
                rainfall = 12.0 if day_offset in [-4, -3] else 2.0
                t_max = 31.0
                t_min = 23.5
                humidity = 76.0
                olr = 195.0
                zonal_wind = 9.5
                soil_moisture = 55.0
        elif scenario == "onset_active":
            # Active onset: continuous rain, strong westerlies, OLR < 185
            if day_offset >= -2:
                rainfall = 18.5 + (math.sin(day_offset) * 12.0)
                rainfall = max(4.0, rainfall)
                t_max = 28.5
                t_min = 22.0
                humidity = 88.0
                olr = 175.0
                zonal_wind = 12.5
                soil_moisture = min(85.0, 50.0 + (day_offset + 3) * 8.0)
            else:
                rainfall = 1.0
                t_max = 36.0
                t_min = 26.0
                humidity = 55.0
                olr = 225.0
                zonal_wind = 6.0
                soil_moisture = 32.0
        elif scenario == "pre_monsoon":
            # False onset / pre-monsoon: one day 30mm rain from isolated thunderstorm, but OLR high & wind low
            rainfall = 28.0 if day_offset == -1 else (0.0 if day_offset >= 0 else 0.5)
            t_max = 38.0
            t_min = 27.0
            humidity = 52.0
            olr = 230.0  # High OLR! (Not sustained deep monsoonal convection)
            zonal_wind = 4.2  # Westerly jet absent!
            soil_moisture = 35.0 if day_offset <= 0 else max(20.0, 35.0 - (day_offset * 4.0))
        else:
            # Dynamically compute based on season and region
            month = date_val.month
            is_monsoon_season = (month in [6, 7, 8, 9])
            if is_monsoon_season:
                base_rain = 8.5 * (1.0 - (lat_factor * 0.3))
                rainfall = max(0.0, base_rain + math.sin(day_offset * 0.7) * 7.0)
                t_max = 31.5 - (rainfall * 0.2)
                t_min = 23.5
                humidity = min(95.0, 72.0 + rainfall * 1.5)
                olr = 190.0 if rainfall > 2.5 else 220.0
                zonal_wind = 10.0 if rainfall > 2.5 else 7.0
                soil_moisture = 62.0
            else:
                rainfall = 0.0 if day_offset % 6 != 0 else 3.0
                t_max = 34.0
                t_min = 22.0
                humidity = 45.0
                olr = 240.0
                zonal_wind = 5.0
                soil_moisture = 28.0

        wind_speed = max(2.5, abs(zonal_wind) * 1.1)
        wind_dir = 240.0 if zonal_wind > 6.0 else 110.0  # South-westerly vs easterly

        return WeatherDailyPoint(
            date=date_val.strftime("%Y-%m-%d"),
            rainfall_mm=round(rainfall, 1),
            temp_max_c=round(t_max, 1),
            temp_min_c=round(t_min, 1),
            humidity_pct=round(humidity, 1),
            wind_speed_ms=round(wind_speed, 1),
            wind_direction_deg=round(wind_dir, 1),
            olr_wm2=round(olr, 1),
            zonal_wind_850hpa_ms=round(zonal_wind, 1),
            soil_moisture_pct=round(soil_moisture, 1)
        )

# Global singleton
weather_service = WeatherService()
