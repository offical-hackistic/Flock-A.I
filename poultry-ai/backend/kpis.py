import pandas as pd
from pathlib import Path
from typing import Dict

DATA_PATH = Path(__file__).parent / "data" / "simulated.csv"

def compute_kpis(house_id: str) -> Dict:
    df = pd.read_csv(DATA_PATH)
    df = df[df["house_id"] == house_id].copy()
    if df.empty:
        raise ValueError("No data for house")
    # Daily aggregates
    last = df.sort_values("timestamp").tail(1).iloc[0]
    days = int(last["age_days"])
    birds_start = int(last["birds_start"])
    birds_alive = int(last["birds_alive"])
    # ADG ~ slope of avg_bird_weight over days
    gpd = df.groupby("age_days")["avg_bird_weight_kg"].mean().diff().mean() * 1000
    # crude FCR estimate using feed vs weight gain
    daily_feed = df.groupby("age_days")["feed_kgph"].sum() / 24.0
    daily_gain_kg = df.groupby("age_days")["avg_bird_weight_kg"].mean().diff().clip(lower=1e-6)
    fcr = float((daily_feed[1:]/(daily_gain_kg[1:]*birds_alive)).median()) if len(daily_feed)>2 else 1.8
    # EPEF (approx): (Livability% * kg live weight *100) / (age_days * FCR)
    livability = 100.0 * birds_alive / birds_start
    kg_live = float(df["avg_bird_weight_kg"].tail(1).iloc[0] * birds_alive)
    epef = (livability * kg_live * 100.0) / max(days,1) / max(fcr, 0.5)
    return {
        "house_id": house_id,
        "days": days,
        "birds_start": birds_start,
        "birds_alive": birds_alive,
        "adg_g_per_day": round(float(gpd if pd.notna(gpd) else 0), 1),
        "fcr_estimate": round(float(fcr), 2),
        "epef": round(float(epef), 1),
    }
