import React, { useEffect, useState } from 'react'
import { simulate, getData, getKpis, getRecs } from './api'
import KpiCards from './components/KpiCards'
import Lines from './components/LineChart'

export default function App(){
  const [houseId, setHouseId] = useState('H1')
  const [days, setDays] = useState(7)
  const [houses, setHouses] = useState(2)
  const [birds, setBirds] = useState(20000)
  const [age, setAge] = useState(21)
  const [telemetry, setTelemetry] = useState<any[]>([])
  const [kpis, setKpis] = useState<any|null>(null)
  const [recs, setRecs] = useState<any|null>(null)
  const [busy, setBusy] = useState(false)

  async function runSim(){
    setBusy(true)
    try {
      await simulate(days, houses, birds)
      const data = await getData(houseId, 300)
      setTelemetry(data)
      const ks = await getKpis(houseId)
      setKpis(ks)
    } finally{
      setBusy(false)
    }
  }

  async function loadAll(){
    const data = await getData(houseId, 300)
    setTelemetry(data)
    const ks = await getKpis(houseId)
    setKpis(ks)
  }

  async function loadRecs(){
    const r = await getRecs(houseId, age)
    setRecs(r)
  }

  useEffect(()=>{ loadAll() }, [])

  return (
    <div style={{ maxWidth: 1200, margin:'0 auto', padding: 16, fontFamily:'Inter, system-ui, sans-serif'}}>
      <h1 style={{ fontSize: 28, marginBottom: 4 }}>🐔 Poultry AI Dashboard</h1>
      <div style={{ opacity: 0.7, marginBottom: 16 }}>Monitor houses, simulate data, and get recommendations.</div>

      <div style={{ display:'flex', gap: 12, flexWrap:'wrap', marginBottom: 12 }}>
        <label>House ID
          <input value={houseId} onChange={e=>setHouseId(e.target.value)} style={{ marginLeft: 8 }} />
        </label>
        <label>Days
          <input type="number" value={days} onChange={e=>setDays(parseInt(e.target.value))} style={{ marginLeft: 8, width: 80 }} />
        </label>
        <label>Houses
          <input type="number" value={houses} onChange={e=>setHouses(parseInt(e.target.value))} style={{ marginLeft: 8, width: 80 }} />
        </label>
        <label>Birds/House
          <input type="number" value={birds} onChange={e=>setBirds(parseInt(e.target.value))} style={{ marginLeft: 8, width: 120 }} />
        </label>
        <label>Bird Age (days)
          <input type="number" value={age} onChange={e=>setAge(parseInt(e.target.value))} style={{ marginLeft: 8, width: 100 }} />
        </label>
        <button onClick={runSim} disabled={busy} style={{ padding:'8px 12px', borderRadius: 10, border:'1px solid #ddd', background:'#f5f5f5', cursor:'pointer' }}>
          {busy ? 'Simulating…' : 'Generate Fake Data'}
        </button>
        <button onClick={loadRecs} style={{ padding:'8px 12px', borderRadius: 10, border:'1px solid #ddd', background:'#e8f7ef', cursor:'pointer' }}>
          Get Recommendations
        </button>
      </div>

      <KpiCards kpis={kpis} />

      <h3>Environment</h3>
      <Lines data={telemetry} series={['temp_c','humidity_pct','co2_ppm','nh3_ppm']} />

      <h3>Feed & Water</h3>
      <Lines data={telemetry} series={['feed_kgph','water_lph']} />

      {recs && (
        <div style={{ marginTop: 16 }}>
          <h3>Recommendations</h3>
          <div style={{ display:'grid', gridTemplateColumns:'repeat(2,1fr)', gap: 12 }}>
            {recs.recommendations.map((r:any, idx:number)=>(
              <div key={idx} style={{ padding: 12, border:'1px solid #eee', borderRadius: 12 }}>
                <div style={{ fontWeight: 700 }}>{r.title} <span style={{ fontSize: 12, opacity: 0.6 }}>({r.priority})</span></div>
                <div style={{ fontSize: 13, opacity: 0.8, margin: '6px 0' }}>{r.rationale}</div>
                <ul style={{ marginLeft: 16 }}>
                  {r.actions.map((a:string, i:number)=>(<li key={i}>{a}</li>))}
                </ul>
                {r.estimated_benefit && <div style={{ fontSize: 12, marginTop: 6, opacity: 0.7 }}>Benefit: {r.estimated_benefit}</div>}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
