import { useEffect, useState } from "react";
import { api } from "../lib/api";
import { useParams } from "react-router-dom";
import Navbar from "../components/Navbar";
import { FileDown, Play, Edit3, Save, Trash2 } from "lucide-react";
import toast from "react-hot-toast";

export default function PatientView(){
  const {id} = useParams();
  const [p,setP]=useState<any>(null);
  const [encs,setEncs]=useState<any[]>([]);
  const [edit,setEdit]=useState(false);
  const [form,setForm]=useState<any>({name:"",cpf:"",height_m:"",weight_kg:"",allergies:"",meds_text:""});
  const [saving,setSaving]=useState(false);

  useEffect(()=>{
    async function load(){
      try{
        const data = await api(`/patients/${id}`); setP(data);
        setForm({
          name: data.name || "",
          cpf: data.cpf || "",
          height_m: data.height_m ?? "",
          weight_kg: data.weight_kg ?? "",
          allergies: (data.allergies || []).join(", "),
          meds_text: (data.meds || []).map((m:any)=>m.nome).join(", ")
        });
        const list = await api(`/patients/${id}/encounters`); setEncs(list);
      }catch(err){ toast.error("Erro ao carregar paciente"); console.error(err); }
    }
    load();
  },[id]);

  async function startEncounter(){
    const r = await api(`/patients/${id}/encounters`,{method:"POST"});
    location.href = `/atendimento/iniciar/${r.id}`;
  }

  async function downloadPDF(){
    const blob = await api(`/pdf/patient/${id}`);
    const url = URL.createObjectURL(blob); const a = document.createElement("a");
    a.href=url; a.download=`prontuario_${id}.pdf`; a.click(); URL.revokeObjectURL(url);
  }

  async function saveEdit(e:any){
    e.preventDefault();
    if(!form.name?.trim()){ toast.error("Informe o nome"); return; }
    setSaving(true);
    try{
      const payload:any = {
        name: form.name.trim(),
        height_m: form.height_m!=="" ? Number(form.height_m): null,
        weight_kg: form.weight_kg!=="" ? Number(form.weight_kg): null,
        allergies: form.allergies ? form.allergies.split(",").map((s:string)=>s.trim()).filter(Boolean) : [],
        meds: form.meds_text ? form.meds_text.split(",").map((s:string)=>({nome:s.trim()})) : []
      };
      await api(`/patients/${id}`, { method:"PUT", body: JSON.stringify(payload) });
      toast.success("Paciente atualizado");
      setEdit(false);
      const data = await api(`/patients/${id}`); setP(data);
    }catch(err){ toast.error("Falha ao salvar"); console.error(err); }
    finally{ setSaving(false); }
  }

  async function deletePatient(){
    if(!confirm("Tem certeza que deseja excluir este paciente? Esta ação não pode ser desfeita.")) return;
    try{
      await api(`/patients/${id}`, { method:"DELETE" });
      toast.success("Paciente excluído");
      location.href = "/dashboard";
    }catch(err){ console.error(err); toast.error("Falha ao excluir paciente"); }
  }

  if(!p) return <>
    <Navbar /><div className="container"><div className="card">Carregando…</div></div>
  </>;

  return <>
    <Navbar />
    <div className="container">
      <div className="card">
        <div className="row" style={{justifyContent:"space-between"}}>
          <div>
            <div className="kicker">Paciente</div>
            <h2 className="h2">{p.name}</h2>
            <div className="helper">CPF: {p.cpf}</div>
          </div>
          <div className="row" style={{gap:8}}>
            <button className="btn" onClick={startEncounter}><Play size={16}/>Iniciar Atendimento</button>
            <button className="btn ghost" onClick={()=>setEdit(e=>!e)}><Edit3 size={16}/>{edit?"Cancelar":"Editar"}</button>
            <button className="btn ghost" onClick={downloadPDF}><FileDown size={16}/>PDF (Cadastro)</button>
            <button className="btn ghost" onClick={deletePatient} style={{borderColor:"var(--danger)", color:"var(--danger)"}}><Trash2 size={16}/>Excluir</button>
          </div>
        </div>

        {!edit ? (
          <>
            <div className="grid cols-2">
              <div className="card"><b>IMC</b><div style={{fontSize:22, fontWeight:800}}>{p.imc ?? "—"}</div></div>
              <div className="card">
                <b>Dados</b>
                <div className="helper">Altura: {p.height_m ?? "—"} m · Peso: {p.weight_kg ?? "—"} kg</div>
              </div>
            </div>
            <div className="grid cols-2">
              <div className="card"><b>Alergias</b><div>{p.allergies?.join(", ") || "—"}</div></div>
              <div className="card"><b>Medicamentos</b><div>{p.meds?.map((m:any)=>m.nome).join(", ") || "—"}</div></div>
            </div>
          </>
        ) : (
          <form onSubmit={saveEdit} className="grid">
            <input placeholder="Nome completo *" value={form.name} onChange={e=>setForm({...form,name:e.target.value})}/>
            <input placeholder="CPF (somente números)" value={form.cpf} disabled />
            <div className="grid cols-2">
              <input placeholder="Altura (m)" value={form.height_m} onChange={e=>setForm({...form,height_m:e.target.value})}/>
              <input placeholder="Peso (kg)" value={form.weight_kg} onChange={e=>setForm({...form,weight_kg:e.target.value})}/>
            </div>
            <input placeholder="Alergias (separe por vírgula)" value={form.allergies} onChange={e=>setForm({...form,allergies:e.target.value})}/>
            <input placeholder="Medicamentos (nome1, nome2...)" value={form.meds_text} onChange={e=>setForm({...form,meds_text:e.target.value})}/>
            <button className="btn" disabled={saving}><Save size={16}/> {saving?"Salvando...":"Salvar alterações"}</button>
          </form>
        )}
      </div>

      {/* histórico permanece igual abaixo */}
      {/* ... */}
    </div>
  </>;
}
