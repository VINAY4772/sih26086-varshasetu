import csv
import datetime
import math
import random
from pathlib import Path

# Explicit notice header
CSV_HEADER = [
    "location_id",
    "date",
    "rainfall_mm",
    "temp_max_c",
    "temp_min_c",
    "humidity_pct",
    "wind_speed_ms",
    "wind_dir_deg",
    "olr_wm2",
    "zonal_wind_850hpa_ms",
    "soil_moisture_pct",
    "enso_nino34",
    "iod_dmi",
    "mjo_amplitude",
    "data_source_id"
]

LOCATIONS = [
    "tel_wgl_dharmasagar",
    "tel_mbnr_jadcherla",
    "ap_gnr_tenali",
    "ap_knl_adoni",
    "mh_amr_chandur",
    "mh_ltr_ausa",
    "mp_seh_ashta",
    "ka_dwd_hubli"
]

def generate_synthetic_data(output_file: Path, start_year: int = 2023, end_year: int = 2025):
    output_file.parent.mkdir(parents=True, exist_ok=True)
    random.seed(42)

    rows = []
    start_date = datetime.date(start_year, 5, 1)
    end_date = datetime.date(end_year, 10, 31)

    for loc_id in LOCATIONS:
        # Base climate parameters per location
        lat_bias = 0.8 if "tel_" in loc_id or "ap_" in loc_id else 1.1
        cur_date = start_date

        enso = round(random.uniform(-0.5, 0.8), 2)
        iod = round(random.uniform(-0.2, 0.4), 2)
        mjo = round(random.uniform(0.5, 1.8), 2)

        while cur_date <= end_date:
            month = cur_date.month
            day = cur_date.day

            # Skip non-monsoon months for compact demonstration dataset
            if month in [5, 6, 7, 8, 9, 10]:
                is_monsoon = (month in [6, 7, 8, 9])
                
                # Simulate onset around June 5-15
                if month == 6 and 8 <= day <= 12:
                    rain = round(random.uniform(12.0, 38.0), 1)
                    olr = round(random.uniform(160.0, 195.0), 1)
                    zonal_wind = round(random.uniform(8.5, 14.0), 1)
                    humidity = round(random.uniform(80.0, 95.0), 1)
                    soil_moist = min(85.0, 50.0 + (day - 7) * 6.0)
                # Simulate break spell in late July (July 20-30)
                elif month == 7 and 20 <= day <= 28:
                    rain = round(random.uniform(0.0, 0.8), 1)
                    olr = round(random.uniform(235.0, 260.0), 1)
                    zonal_wind = round(random.uniform(2.5, 5.0), 1)
                    humidity = round(random.uniform(42.0, 58.0), 1)
                    soil_moist = max(20.0, 60.0 - (day - 19) * 4.5)
                elif is_monsoon:
                    # Normal intermittent rainfall
                    has_rain = (random.random() < 0.45)
                    rain = round(random.uniform(2.5, 25.0), 1) if has_rain else 0.0
                    olr = round(random.uniform(180.0, 220.0), 1)
                    zonal_wind = round(random.uniform(6.5, 11.0), 1)
                    humidity = round(random.uniform(65.0, 88.0), 1)
                    soil_moist = round(random.uniform(45.0, 75.0), 1)
                else:
                    # Pre-monsoon May / Post-monsoon October
                    rain = round(random.uniform(0.0, 5.0), 1) if random.random() < 0.15 else 0.0
                    olr = round(random.uniform(220.0, 255.0), 1)
                    zonal_wind = round(random.uniform(3.0, 6.0), 1)
                    humidity = round(random.uniform(40.0, 60.0), 1)
                    soil_moist = round(random.uniform(22.0, 38.0), 1)

                t_max = round(34.0 - (rain * 0.15) + random.uniform(-1.5, 1.5), 1)
                t_min = round(23.0 + random.uniform(-1.0, 1.0), 1)
                wind_speed = round(max(2.0, zonal_wind * 1.15), 1)
                wind_dir = round(230.0 + random.uniform(-20, 20), 1) if zonal_wind > 6.0 else round(110.0 + random.uniform(-30, 30), 1)

                rows.append([
                    loc_id,
                    cur_date.strftime("%Y-%m-%d"),
                    rain,
                    t_max,
                    t_min,
                    humidity,
                    wind_speed,
                    wind_dir,
                    olr,
                    zonal_wind,
                    soil_moist,
                    enso,
                    iod,
                    mjo,
                    "synthetic_demo_feed"
                ])

            cur_date += datetime.timedelta(days=1)

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(CSV_HEADER)
        writer.writerows(rows)

    print(f"✅ Generated {len(rows)} records in SYNTHETIC DEMONSTRATION dataset: {output_file}")

if __name__ == "__main__":
    target = Path(__file__).resolve().parent.parent / "data" / "sample" / "synthetic_weather_sample.csv"
    generate_synthetic_data(target)
