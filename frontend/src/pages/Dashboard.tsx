import { useEffect, useMemo, useState } from "react";
import { api } from "../lib/api";
import Navbar from "../components/Navbar";
import { UserRound, Search } from "lucide-react";
type Patient = { id:string; name:string; imc:number|null; height_m:number|null; weight_kg:number|null; };

export default function Dashboard(){
  const [list,setList]=useState<Patient[]>([]);
  const [q,setQ]=useState("");
  useEffect(()=>{ api("/patients").then(setList).catch(console.error); },[]);
  const filtered = useMemo(()=>{
    const t = q.trim().toLowerCase();
    return t ? list.filter(p=>p.name.toLowerCase().includes(t)) : list;
  },[q,list]);

  return (
    <>
      <Navbar />
      <div className="container">
        <div className="card">
          <div className="row" style={{justifyContent:"space-between"}}>
            <div>
              <div className="kicker">Pacientes</div>
              <h2 className="h2">Visão Geral</h2>
            </div>
            <div className="row" style={{gap:6}}>
              <div className="row" style={{background:"#0c1119", border:"1px solid var(--border)", borderRadius:10, padding:"6px 10px"}}>
                <Search size={16} />
                <input placeholder="Buscar por nome..." onChange={e=>setQ(e.target.value)} style={{border:"0", background:"transparent", width:220}} />
              </div>
            </div>
          </div>

          <div className="grid">
            {filtered.map(p=>
              <a key={p.id} className="card" href={`/paciente/${p.id}`} style={{display:"flex",alignItems:"center",gap:12}}>
                <div style={{background:"#0d1320", border:"1px solid var(--border)", width:42, height:42, borderRadius:10, display:"grid", placeItems:"center"}}><UserRound size={20}/></div>
                <div style={{flex:1}}>
                  <div style={{fontWeight:700}}>{p.name}</div>
                  <div className="helper">Altura: {p.height_m ?? "—"} m · Peso: {p.weight_kg ?? "—"} kg</div>
                </div>
                <span className="badge">IMC: {p.imc ?? "—"}</span>
              </a>
            )}
            {filtered.length===0 && <div className="helper">Nenhum paciente encontrado.</div>}
          </div>
        </div>
      </div>
    </>
  );
}
