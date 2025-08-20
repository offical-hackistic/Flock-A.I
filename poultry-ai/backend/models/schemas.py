from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class SimulateRequest(BaseModel):
    days: int = Field(7, ge=1, le=60)
    houses: int = Field(2, ge=1, le=10)
    birds_per_house: int = Field(20000, ge=1000, le=60000)

class Telemetry(BaseModel):
    timestamp: str
    house_id: str
    temp_c: float
    humidity_pct: float
    co2_ppm: float
    nh3_ppm: float
    airflow_cfm: float
    water_lph: float  # liters/hour
    feed_kgph: float  # kg/hour
    avg_bird_weight_kg: float
    mortality_today: int

class KPIResponse(BaseModel):
    house_id: str
    days: int
    birds_start: int
    birds_alive: int
    adg_g_per_day: float
    fcr_estimate: float
    epef: float

class Recommendation(BaseModel):
    title: str
    rationale: str
    actions: List[str]
    priority: str  # low/medium/high
    estimated_benefit: Optional[str] = None

class RecResponse(BaseModel):
    house_id: str
    bird_age_days: int
    recommendations: List[Recommendation]
    targets: Dict[str, Any]
