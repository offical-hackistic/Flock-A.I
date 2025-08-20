import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import Tuple

DATA_PATH = Path(__file__).parent / "data" / "simulated.csv"

def generate_targets(day: int) -> Tuple[float, float, float, float]:
    # Simple curves
    temp_target = np.interp(day, [0,7,14,21,28,35], [32,29,26,23,21.5,21])
    hum_low, hum_high = 50, 70
    co2_max = 3000
    nh3_max = 25
    return temp_target, np.random.uniform(hum_low, hum_high), co2_max, nh3_max

def simulate(days=7, houses=2, birds_per_house=20000, freq_minutes=15, seed=7):
    rng = np.random.default_rng(seed)
    start = datetime.utcnow() - timedelta(days=days)
    rows = []
    for h in range(houses):
        house_id = f"H{h+1}"
        birds = birds_per_house
        avg_weight = 0.04  # 40 g chick
        mortality_cum = 0
        t = start
        while t <= datetime.utcnow():
            age_days = (t - start).days
            temp_target, hum_target, co2_max, nh3_max = generate_targets(age_days)
            # Simulate environment around targets
            temp = rng.normal(temp_target, 1.2) + 0.5*np.sin(2*np.pi*(t.hour/24))
            humidity = np.clip(rng.normal(hum_target, 5), 35, 85)
            co2 = np.clip(rng.normal(1800 + age_days*30, 200), 800, 5000)
            nh3 = np.clip(rng.normal(10 + age_days*0.5, 3), 0, 60)
            airflow = max(5000 + age_days*200 + rng.normal(0, 500), 1000)
            water_lph = max(50 + age_days*8 + rng.normal(0, 6), 5)
            feed_kgph = max(20 + age_days*6 + rng.normal(0, 5), 2)
            # Growth and mortality
            avg_weight = max(avg_weight + rng.normal(0.03 + age_days*0.001, 0.005), 0.04)
            mortality_today = int(max(rng.poisson( birds*0.00002 + age_days*0.0005 ), 0))
            mortality_cum += mortality_today
            birds_alive = birds - mortality_cum
            rows.append({
                "timestamp": t.isoformat(),
                "house_id": house_id,
                "temp_c": round(temp,2),
                "humidity_pct": round(humidity,1),
                "co2_ppm": int(co2),
                "nh3_ppm": round(nh3,1),
                "airflow_cfm": int(airflow),
                "water_lph": round(water_lph,1),
                "feed_kgph": round(feed_kgph,1),
                "avg_bird_weight_kg": round(avg_weight,3),
                "mortality_today": mortality_today,
                "birds_alive": birds_alive,
                "age_days": age_days,
                "birds_start": birds_per_house
            })
            t += timedelta(minutes=freq_minutes)
    df = pd.DataFrame(rows)
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(DATA_PATH, index=False)
    return df

if __name__ == "__main__":
    simulate()
    print(f"Wrote {DATA_PATH}")
