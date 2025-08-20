from typing import Dict

def suggest_setpoints(avg: Dict, targets: Dict) -> Dict:
    # Simple proportional tweaks; replace with your controller mapping.
    out = {}
    if "temp_c" in avg and "temp_c_target" in targets:
        out["heater_setpoint_c"] = round(targets["temp_c_target"], 1)
        out["ventilation_percent"] = max(0, min(100, 40 + (avg["temp_c"] - targets["temp_c_target"]) * 10))
    if "humidity_pct" in avg and "humidity_pct_range" in targets:
        low, high = targets["humidity_pct_range"]
        out["min_vent_timer_sec_per_5min"] = 30 if avg["humidity_pct"] > high else 10
    return out
