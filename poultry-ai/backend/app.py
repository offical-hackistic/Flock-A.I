from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
import pandas as pd
from pathlib import Path

from models.schemas import SimulateRequest, KPIResponse, RecResponse
from data_simulator import simulate, DATA_PATH
from recommender import build_recommendations
from kpis import compute_kpis

app = FastAPI(title="Poultry AI", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/simulate")
def simulate_data(req: SimulateRequest):
    df = simulate(days=req.days, houses=req.houses, birds_per_house=req.birds_per_house)
    return {"rows": len(df), "houses": req.houses, "days": req.days}

@app.get("/data")
def get_data(house_id: str, limit: int = 500):
    df = pd.read_csv(DATA_PATH)
    sdf = df[df["house_id"] == house_id].sort_values("timestamp").tail(limit)
    return {"data": sdf.to_dict(orient="records")}

@app.get("/kpis", response_model=KPIResponse)
def kpis(house_id: str):
    try:
        return compute_kpis(house_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/recommendations", response_model=RecResponse)
def recommendations(house_id: str, bird_age_days: int):
    res = build_recommendations(house_id=house_id, bird_age_days=bird_age_days)
    return res
