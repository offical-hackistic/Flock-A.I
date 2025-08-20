# Poultry AI — Starter Repo (Codespaces Ready)

An end‑to‑end starter that helps commercial poultry growers monitor conditions, simulate data, and get actionable, grower‑first recommendations.

- **Backend**: FastAPI (Python) — KPIs, rule‑based insights + simple ML, fake data simulator.
- **Frontend**: React + Vite — dashboard with charts, KPIs, and one‑click recommendations.
- **Codespaces**: Devcontainer config preinstalls Python and Node, forwards ports, and gets you running fast.

> ⚠️ This is a starter for experimentation and education. Always validate recommendations with your integrator, veterinarian, and on‑farm SOPs.

## Quick Start (GitHub Codespaces)

1. **Create a repo and add these files** (or download the ZIP from ChatGPT and upload).
2. Click **Code → Create codespace on main**.
3. After it builds, open two terminals in Codespaces and run:

**Terminal A (backend):**
```bash
uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
```

**Terminal B (frontend):**
```bash
cd frontend
npm run dev -- --host
```

Codespaces will forward ports **8000** (API) and **5173** (web). Open them from the Ports tab.

## What you can do
- **Generate fake telemetry**: `/simulate` endpoint creates realistic house data (temp, humidity, gases, feed/water usage, weights).
- **See KPIs**: ADG, FCR (est.), mortality rate (simulated), EPEF.
- **Get recommendations**: ventilation/heat/lighting/feed/water guidance tied to target curves by bird age + anomaly checks.
- **Tweak targets**: `backend/config/targets.yaml` for temperature/ventilation/humidity curves.

## Project Structure
```
poultry-ai/
  .devcontainer/devcontainer.json
  backend/
    app.py
    recommender.py
    optimizer.py
    data_simulator.py
    kpis.py
    models/schemas.py
    config/targets.yaml
    data/simulated.csv
    requirements.txt
  frontend/
    index.html
    package.json
    vite.config.ts
    tsconfig.json
    src/main.tsx
    src/App.tsx
    src/api.ts
    src/components/KpiCards.tsx
    src/components/LineChart.tsx
  scripts/dev.sh
  README.md
```

## API (selected)
- `GET /health` — liveness
- `POST /simulate` — (re)generate fake data; body: `{ "days": 7, "houses": 2, "birds_per_house": 20000 }`
- `GET /kpis?house_id=H1` — returns KPIs for the latest flock/day
- `GET /recommendations?house_id=H1&bird_age_days=21` — returns actionable steps
- `GET /data?house_id=H1&limit=1000` — recent telemetry

## Notes
- Targets in `targets.yaml` are **generic approximations**; tune for breed, season, house, and integrator guidance.
- The ML placeholder uses IsolationForest for anomaly detection. Swap with your models later (LSTM, XGBoost, etc.).
- Frontend uses Recharts for simple, legible charts.
