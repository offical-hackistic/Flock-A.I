import React from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export default function Lines({ data, x='timestamp', series=['temp_c','humidity_pct'] }:{ data:any[], x?:string, series?:string[] }){
  return (
    <div style={{ width:'100%', height:320 }}>
      <ResponsiveContainer>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey={x} hide />
          <YAxis />
          <Tooltip />
          <Legend />
          {series.map((s, i)=>(
            <Line key={s} type="monotone" dataKey={s} dot={false} strokeWidth={2} />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
