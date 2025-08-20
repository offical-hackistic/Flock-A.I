from typing import List, Dict, Any
import pandas as pd
import numpy as np
from pathlib import Path
import yaml
from sklearn.ensemble import IsolationForest

DATA_PATH = Path(__file__).parent / "data" / "simulated.csv"
TARGETS = yaml.safe_load((Path(__file__).parent / "config" / "targets.yaml").read_text())

def target_temp(day: int) -> float:
    curve = TARGETS.get("temperature_c_by_day", {})
    if not curve:
        return 28.0
    xs = sorted(int(k) for k in curve.keys())
    ys = [curve[str(k)] for k in xs]
    return float(np.interp(day, xs, ys))

def target_light(day: int) -> float:
    curve = TARGETS.get("light_lux_by_day", {"0": 30, "7": 20, "21": 10})
    xs = sorted(int(k) for k in curve.keys())
    ys = [curve[str(k)] for k in xs]
    return float(np.interp(day, xs, ys))

def latest_slice(df: pd.DataFrame, house_id: str) -> pd.DataFrame:
    sdf = df[df["house_id"] == house_id].sort_values("timestamp").tail(96)  # last 24h @15min
    return sdf

def anomalies(df: pd.DataFrame) -> Dict[str, float]:
    if df.empty:
        return {}
    X = df[["temp_c","humidity_pct","co2_ppm","nh3_ppm","water_lph","feed_kgph","airflow_cfm"]].values
    iso = IsolationForest(contamination=0.05, random_state=7).fit(X)
    scores = iso.decision_function(X)
    # Return anomaly rate and worst score
    return {"anomaly_rate": float((scores < np.percentile(scores, 5)).mean()), "min_score": float(scores.min())}

def build_recommendations(house_id: str, bird_age_days: int) -> Dict[str, Any]:
    df = pd.read_csv(DATA_PATH)
    window = latest_slice(df, house_id)
    if window.empty:
        return {"house_id": house_id, "recommendations": [], "targets": {}}

    avg = window.mean(numeric_only=True)
    t_target = target_temp(bird_age_days)
    h_low, h_high = TARGETS.get("humidity_pct_target_range", [50,70])
    co2_max = TARGETS.get("co2_ppm_max", 3000)
    nh3_max = TARGETS.get("ammonia_ppm_max", 25)
    light_target = target_light(bird_age_days)

    recs: List[Dict[str, Any]] = []

    # Temperature control
    delta_t = avg["temp_c"] - t_target
    if delta_t > 1.0:
        recs.append({
            "title": "Reduce House Temperature",
            "rationale": f"Avg temp {avg['temp_c']:.1f}°C is above target {t_target:.1f}°C for day {bird_age_days}.",
            "actions": [
                "Increase tunnel/sidewall ventilation setpoint by 5–10%.",
                "Lower heater setpoint by 0.5–1.0°C and monitor chicks behavior.",
                "Check inlet calibration and air speed across bird level."
            ],
            "priority": "high",
            "estimated_benefit": "Lower heat stress; better feed intake and FCR."
        })
    elif delta_t < -1.0:
        recs.append({
            "title": "Increase House Temperature",
            "rationale": f"Avg temp {avg['temp_c']:.1f}°C is below target {t_target:.1f}°C for day {bird_age_days}.",
            "actions": [
                "Increase heater setpoint by 0.5–1.0°C.",
                "Trim minimum ventilation for heat conservation; avoid CO2/Ammonia rise.",
                "Verify tightness and pre‑heat before placing chicks if at brooding."
            ],
            "priority": "high",
            "estimated_benefit": "Improves comfort and uniformity."
        })

    # Humidity control
    if avg["humidity_pct"] > h_high:
        recs.append({
            "title": "Dry the House (High Humidity)",
            "rationale": f"Avg RH {avg['humidity_pct']:.0f}% exceeds {h_high}%.",
            "actions": [
                "Increase minimum ventilation timer.",
                "Add run time on fans after drinker line checks for leaks.",
                "Top‑dress litter or add fresh, dry material in wet areas."
            ],
            "priority": "medium"
        })
    elif avg["humidity_pct"] < h_low:
        recs.append({
            "title": "Raise Humidity (Too Dry)",
            "rationale": f"Avg RH {avg['humidity_pct']:.0f}% is below {h_low}%.",
            "actions": [
                "Reduce unnecessary ventilation if gases are fine.",
                "Consider intermittent fogging if available; avoid wet litter."
            ],
            "priority": "low"
        })

    # Gases
    if avg["co2_ppm"] > co2_max:
        recs.append({
            "title": "Lower CO₂ Levels",
            "rationale": f"Avg CO₂ {avg['co2_ppm']:.0f} ppm exceeds {co2_max} ppm.",
            "actions": [
                "Increase minimum ventilation rate.",
                "Verify igniter/combustion of brooders; ensure fresh air inlets near heaters."
            ],
            "priority": "high"
        })
    if avg["nh3_ppm"] > nh3_max:
        recs.append({
            "title": "Control Ammonia (NH₃)",
            "rationale": f"Avg NH₃ {avg['nh3_ppm']:.1f} ppm exceeds {nh3_max} ppm.",
            "actions": [
                "Add litter amendment where birds lie down.",
                "Increase ventilation if temperature allows.",
                "Fix drinker leaks and adjust height/flow."
            ],
            "priority": "high"
        })

    # Water/feed sanity checks
    wf_ratio = (avg["water_lph"] * 1.0) / max(avg["feed_kgph"], 0.1)
    if wf_ratio > 2.5:
        recs.append({
            "title": "High Water-to-Feed Ratio",
            "rationale": f"Water:Feed ratio {wf_ratio:.2f} is elevated; could indicate leaks or health issues.",
            "actions": [
                "Walk lines for leaks/spills; adjust nipples.",
                "Check for diarrhea; consult advisor if persists."
            ],
            "priority": "medium"
        })

    # Lighting target
    recs.append({
        "title": "Lighting Check",
        "rationale": f"Target light ~{light_target:.0f} lux for day {bird_age_days}.",
        "actions": [
            "Measure lux at bird level in 10 spots; aim for uniformity.",
            "Gradually step down as per program; avoid sudden changes."
        ],
        "priority": "low"
    })

    # Anomaly signal
    an = anomalies(window)
    if an.get("anomaly_rate", 0) > 0.05:
        recs.append({
            "title": "Telemetry Anomalies Detected",
            "rationale": f"~{an['anomaly_rate']*100:.0f}% of points look unusual vs recent history.",
            "actions": [
                "Check sensors (calibration, obstruction).",
                "Confirm setpoints match controller display.",
                "Walk the birds and verify comfort cues (spread, noise, panting)."
            ],
            "priority": "medium"
        })

    return {
        "house_id": house_id,
        "bird_age_days": int(bird_age_days),
        "recommendations": recs,
        "targets": {
            "temp_c_target": t_target,
            "humidity_pct_range": [h_low, h_high],
            "co2_ppm_max": co2_max,
            "nh3_ppm_max": nh3_max,
            "light_lux_target": light_target
        }
    }
