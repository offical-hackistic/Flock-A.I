import axios from 'axios'

const API = (path: string) => {
  // In Codespaces, 0.0.0.0 with forwarded port works, CORS is enabled.
  const base = window.location.hostname.includes('github.dev') ? '' : ''
  return `http://localhost:8000${path}`
}

export async function simulate(days:number, houses:number, birds:number){
  const res = await axios.post(API('/simulate'), { days, houses, birds_per_house: birds })
  return res.data
}
export async function getData(houseId:string, limit=300){
  const res = await axios.get(API(`/data?house_id=${houseId}&limit=${limit}`))
  return res.data.data
}
export async function getKpis(houseId:string){
  const res = await axios.get(API(`/kpis?house_id=${houseId}`))
  return res.data
}
export async function getRecs(houseId:string, birdAgeDays:number){
  const res = await axios.get(API(`/recommendations?house_id=${houseId}&bird_age_days=${birdAgeDays}`))
  return res.data
}
