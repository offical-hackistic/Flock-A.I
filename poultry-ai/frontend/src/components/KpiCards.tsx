import React from 'react'

export default function KpiCards({ kpis }:{ kpis: any }){
  if(!kpis) return null
  const items = [
    { label: 'Days', value: kpis.days },
    { label: 'Birds Alive', value: kpis.birds_alive },
    { label: 'ADG (g/day)', value: kpis.adg_g_per_day },
    { label: 'FCR (est)', value: kpis.fcr_estimate },
    { label: 'EPEF', value: kpis.epef }
  ]
  return (
    <div style={{ display:'grid', gridTemplateColumns:'repeat(5,1fr)', gap: '12px', margin:'12px 0'}}>
      {items.map((it, idx)=>(
        <div key={idx} style={{ padding:'12px', border:'1px solid #eee', borderRadius:12, boxShadow:'0 1px 4px rgba(0,0,0,0.05)'}}>
          <div style={{ fontSize:12, opacity:0.7 }}>{it.label}</div>
          <div style={{ fontSize:22, fontWeight:700 }}>{it.value}</div>
        </div>
      ))}
    </div>
  )
}
